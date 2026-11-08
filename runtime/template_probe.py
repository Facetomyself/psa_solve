#!/usr/bin/env python3
"""template_probe.py — v0 入口 MZ 计数器改写探针生成器（生产版）。

收编自 diagnostics/atob-diff-20261107/static-payload-verify/online-verify/ov2/
make_probe_ov2gen.py（OV2 验证通过的定位器，保留其全部形态覆盖），裁剪为生产
最小面：只保留 v0 入口定位、conv-site 4 形态定位、MZ 捕获+计数器改写探针、
__psaSink 证据回传。离线验证专用的 m9/join/iife/env-capture 探针不进生产
（它们是 static-payload-verify 流水线的职责，诊断域脚本保留不动）。

OV2 已证事实（2026-11-08，见 online-verify/ov2/notes.md）：
  - 改写点：v0 编码器入口（call1 分支）按"键位置"（non-__ownN 键序的
    idx 5/6/7/22）内联改写 4 计数器；模板值 A=20/B=C=800/D=1500。
  - 服务端在 challenge 任意跳不校验这 4 个计时值（OV2 s8 全链收敛 clearance）。
  - conv-site 变体家族 4 形态，全由 bare-global hex25 唯一性锚定（form 4/5/6/7）。
  - v0 入口是 unique dense-var-chain 头（>=10 单变量声明 in 前 520 字符）。
  - challenge realm 的证据回传必须走 __psaSink（ctx.eval 读不到 challenge realm）。

公开接口：
  build_probe(orchestrate_bytes, template) -> (probe_bytes, meta dict)
  定位失败抛 TemplateProbeError（调用方降级原生模式）。
  DEFAULT_TEMPLATE — OV2 验证值。

用法（solve_ruyijs.py 改写模式）：
  from template_probe import build_probe, DEFAULT_TEMPLATE
  probe, meta = build_probe(orch_bytes, DEFAULT_TEMPLATE)
"""
from __future__ import annotations

import hashlib
import json
import re

IDC = "a-zA-Z_$0-9"  # identifier char class CONTENT (use inside [...])

DEFAULT_TEMPLATE = {
    "vA": 20, "vB": 800, "vC": 800, "vD": 1500,
}


class TemplateProbeError(RuntimeError):
    """探针生成失败（定位器未唯一命中/结构不符）。调用方应降级原生模式。"""


HEAD_RE = re.compile(
    r"\b([" + IDC + r"]{1,4})=function\(([" + IDC + r"]{1,4})\)\{var ["
    + IDC + r"]{1,4};var ")
VAR_DECL = re.compile(r"var [" + IDC + r"]{1,4};")
CONV4_SITE_RE = re.compile(
    r"([" + IDC + r"]{1,4})=([" + IDC + r"]{1,4})\((_[0-9a-f]{16,30}|_[0-9a-f]{24})(,(["
    + IDC + r"]{1,4}))?\)")
CONV1_SITE_RE = re.compile(
    r"([" + IDC + r"]{1,4})=(_[0-9a-f]{16,30}|_[0-9a-f]{24})\(\1\)")
# form 5: hex25 passed as a bare argument to any call inside the encoder body
# (dispatcher topology: `nqb(K,K,HEX25,uu[0])` — args may contain one nesting
# level of parens; the wrapper wraps the WHOLE call expression).
CONV5_SITE_RE = re.compile(
    r"\b([" + IDC + r"]{1,4})\(([^()]*(?:\([^()]*\)[^()]*){0,6})\b(_[0-9a-f]{16,30}|_[0-9a-f]{24})(?:,([^()]*(?:\([^()]*\)[^()]*){0,6}))?\)")
# form 3 (pipeline 同款): (CONSTS,FUNC)(HEX25,ARG) — comma-expr callee ending in
# a declared short-name function; CONSTS 仅容混淆器常量算术（0-9^|+()~空白），
# 避开通用 `(0,f)(x)` 惯用法误命中（optrace3: (...,iH)(_0e34...,Ol[...])）。
CONV3_SITE_RE = re.compile(
    r"\(([0-9^|+()~\s]+),([" + IDC + r"]{1,8})\)\((_[0-9a-f]{16,30}|_[0-9a-f]{24}),")


def _declared_short(text: str, name: str) -> bool:
    """短名函数已声明：var 链（var/逗号/分号/花括号后跟名字）或 =function 形态。"""
    if re.search(r"(?:var[\s,]|[;,{])" + re.escape(name) + r"(?![a-zA-Z0-9_$])", text):
        return True
    return bool(re.search(re.escape(name) + r"=function", text))


def _hex_ok(text: str, hexn: str) -> bool:
    """bare-global hex25 判据：全文件唯一出现且从无 var/function 声明。"""
    if re.search(r"(?:var|function)[\s]+" + re.escape(hexn) + r"(?![a-zA-Z0-9_$])", text):
        return False
    return len(re.findall(re.escape(hexn) + r"(?![a-zA-Z0-9_$])", text)) == 1


def find_encoder_entry(text: str) -> tuple:
    """v0 入口：唯一 dense-var-chain 头。返回 (name, param, pos, nvar)。"""
    cands = []
    for m in HEAD_RE.finditer(text):
        seg = text[m.start():m.start() + 520]
        nvar = len(VAR_DECL.findall(seg))
        declared = ("var %s;" % m.group(1)) in text[:m.start()]
        cands.append((nvar, m.group(1), m.group(2), m.start(), declared))
    strong = [c for c in cands if c[0] >= 10 and c[4]]
    if len(strong) != 1:
        raise TemplateProbeError(
            "encoder entry ambiguous: %r" % ([(c[1], c[3]) for c in strong[:5]],))
    nvar, name, param, pos, _ = strong[0]
    return name, param, pos, nvar


def match_brace(text: str, open_pos: int) -> int:
    depth = 0
    i = open_pos
    n = len(text)
    in_str = None
    while i < n:
        c = text[i]
        if in_str:
            if c == "\\":
                i += 2
                continue
            if c == in_str:
                in_str = None
            i += 1
            continue
        if c in "\"'`":
            in_str = c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def find_conv_site(text: str, body_open: int, body_close: int) -> tuple:
    """v0 体内的 converter 调用点。形态按序尝试，唯一命中即用：
    form 4: `F=AZ(HEX25,ARG)`   — 2 参调用，arg1 = bare-global hex25
    form 1b: `F=HEX25(F)`       — hex25 直接自调用
    form 5: `F(...,HEX25,...)`  — hex25 作为任意调用的裸参数（dispatcher）
    form 6: `(0,WR)(HEX25,ARG)` — 逗号 dispatcher 直调
    form 7: `=HEX25(ARG)`       — 属性/元素赋值右侧裸全局直调
    form 3: `(CONSTS,FUNC)(HEX25,ARG)` — comma-expr callee（optrace3 形态）
    返回 (site_text, hex_name, pos)。"""
    v0body = text[body_open:body_close + 1]
    hits = []

    for m in CONV4_SITE_RE.finditer(v0body):
        hexn = m.group(3)
        if _hex_ok(text, hexn):
            hits.append((m.group(0), hexn, m.start() + body_open))
    if len(hits) == 1:
        return hits[0]

    hits = []
    for m in CONV1_SITE_RE.finditer(v0body):
        hexn = m.group(2)
        if _hex_ok(text, hexn):
            hits.append((m.group(0), hexn, m.start() + body_open))
    if len(hits) == 1:
        return hits[0]

    hits = []
    for m in CONV5_SITE_RE.finditer(v0body):
        hexn = m.group(3)
        if _hex_ok(text, hexn):
            hits.append((m.group(0), hexn, m.start() + body_open))
    if len(hits) == 1:
        return hits[0]

    hits = []
    for m in re.finditer(
            r"\(0,([" + IDC + r"]{1,4})\)\((_[0-9a-f]{16,30}|_[0-9a-f]{24}),([^(),]{1,80}?)\)",
            v0body):
        hexn = m.group(2)
        if _hex_ok(text, hexn):
            hits.append((m.group(0), hexn, m.start() + body_open))
    if len(hits) == 1:
        return hits[0]

    hits = []
    for m in re.finditer(
            r"=(_[0-9a-f]{16,30}|_[0-9a-f]{24})\(([^()]*(?:\([^()]*\)[^()]*){0,4}?)\)",
            v0body):
        hexn = m.group(1)
        if _hex_ok(text, hexn):
            # strip the leading '=' boundary — it belongs to the surrounding
            # assignment, not the call expression we wrap.
            site = m.group(0)[1:]
            hits.append((site, hexn, m.start() + 1 + body_open))
    if len(hits) == 1:
        return hits[0]

    # form 3（最后尝试，pipeline 同款）：定位到即可——生产探针只包 v0 入口
    # 做计数器改写，conv-site 本身不需要包裹（Mn 流非生产需求），这里只需
    # 确认形态存在且唯一，作为"该变体结构符合已知家族"的判定。
    hits = []
    for m in CONV3_SITE_RE.finditer(v0body):
        fnn, hexn = m.group(2), m.group(3)
        if not _hex_ok(text, hexn):
            continue
        if not _declared_short(text, fnn):
            continue
        hits.append((m.group(0), hexn, m.start() + body_open))
    if len(hits) == 1:
        return hits[0]

    raise TemplateProbeError("conv site not unique across forms")


# 改写探针：v0 入口 call1 分支，键位置解析 + pre/post 证据 + __psaSink 回传。
# 键位置 idx 5/6/7/22（of non-__ownN keys）是 OV2 实测的计数器位置，跨变体稳定
# （位置语义由 R2/R2a 的角色多重集相等保证，键名哈希每变体轮换但位置不变）。
OV2_MUT = (
    "try{if(globalThis.__tpl&&!globalThis.__tplMut){"
    "globalThis.__tplMut=1;"
    "var OK=globalThis.__tpl;"
    "var __ok=Object.keys(__mzin).filter(function(k){return k!=='__ownN'});"
    "OK.kA=__ok[5];OK.kB=__ok[6];OK.kC=__ok[7];OK.kD=__ok[22];"
    "try{globalThis.__tplPre=JSON.stringify([__mzin[OK.kA],__mzin[OK.kB],__mzin[OK.kC],__mzin[OK.kD]])}catch(e){}"
    "__mzin[OK.kA]=OK.vA;__mzin[OK.kB]=OK.vB;__mzin[OK.kC]=OK.vC;__mzin[OK.kD]=OK.vD;"
    "globalThis.__tplPost=JSON.stringify([__mzin[OK.kA],__mzin[OK.kB],__mzin[OK.kC],__mzin[OK.kD]]);"
    "try{__psaSink('TP',String(globalThis.__tplPre),String(globalThis.__tplPost))}catch(e){}"
    "}"
    "if(globalThis.__tpl){globalThis.__tplSeen=(globalThis.__tplSeen||0)+1;"
    "try{__psaSink('TS',String(globalThis.__tplSeen),'')}catch(e){}}}"
    "catch(e){globalThis.__tplErr=String(e).slice(0,200);"
    "try{__psaSink('TE',globalThis.__tplErr,'')}catch(e2){}};"
)

MZ_CAPTURE = (
    "try{var C=globalThis.__tplCalls=(globalThis.__tplCalls||0)+1;"
    "if(C===1){" + OV2_MUT + "}"
    "}catch(e){}"
)


def build_probe(orchestrate_bytes: bytes, template: dict | None = None) -> tuple:
    """从 orchestrate 字节生成计数器改写探针。

    template: {"vA":..,"vB":..,"vC":..,"vD":..}（缺省用 DEFAULT_TEMPLATE）。
    返回 (probe_bytes, meta)；meta 含定位信息与探针 sha，供降级判定与审计。
    失败抛 TemplateProbeError。
    """
    text = orchestrate_bytes.decode("utf-8", errors="replace")
    tpl = dict(DEFAULT_TEMPLATE if template is None else template)
    for k in ("vA", "vB", "vC", "vD"):
        if not isinstance(tpl.get(k), (int, float)):
            raise TemplateProbeError("template.%s missing/not number" % k)

    v0name, v0param, head_pos, nvar = find_encoder_entry(text)
    body_open = text.find("{", head_pos)
    body_close = match_brace(text, body_open)
    if body_close < 0:
        raise TemplateProbeError("encoder body brace match failed")

    conv_site, conv_hex, conv_pos = find_conv_site(text, body_open, body_close)

    # 改写探针只包 v0 入口（MZ 捕获+改写），不包 conv-site（生产不需要 Mn 流）。
    # wrapper 与 OV2 同构：__mzin 参数名（避讳规则：不得与目标变量同名）。
    mut = MZ_CAPTURE
    wrapper_prefix = (
        "(function(__f){var __w=function(__mzin){"
        "var __r;"
        "try{" + mut + "}catch(e){}"
        "try{__r=__f.apply(this,arguments)}"
        "catch(__e){throw __e}"
        "return __r;};"
        "try{if(!globalThis.__v0)globalThis.__v0=__w}catch(e){}"
        "return __w;})("
    )
    patched = (
        text[:head_pos]
        + v0name + "="
        + wrapper_prefix
        + text[head_pos + len(v0name) + 1:body_close + 1]
        + ")"
        + text[body_close + 1:]
    )

    # 完整性自检（OV2 同款门禁）
    n_reg = patched.count("globalThis.__v0=__w")
    if n_reg != 1:
        raise TemplateProbeError("__v0 registration count=%d" % n_reg)
    for a, b in ((patched.count("(") - text.count("("), patched.count(")") - text.count(")")),
                 (patched.count("{") - text.count("{"), patched.count("}") - text.count("}"))):
        if a != b:
            raise TemplateProbeError("bracket deltas: (%d,%d)" % (a, b))
    for marker in ("__tplCalls", "__tpl", "__psaSink('TP'"):
        if marker not in patched:
            raise TemplateProbeError("probe marker missing: %s" % marker)

    meta = {
        "v0_name": v0name, "v0_param": v0param, "v0_head_pos": head_pos,
        "var_chain": nvar, "v0_body_span": [body_open, body_close],
        "conv_site": conv_site[:80], "conv_hex": conv_hex, "conv_pos": conv_pos,
        "template": {"vA": tpl["vA"], "vB": tpl["vB"], "vC": tpl["vC"], "vD": tpl["vD"]},
        "src_sha16": hashlib.sha256(orchestrate_bytes).hexdigest()[:16],
        "probe_len": len(patched),
        "probe_sha16": hashlib.sha256(patched.encode("utf-8", errors="replace")).hexdigest()[:16],
        "version": "template-probe-1",
    }
    return patched.encode("utf-8"), meta
