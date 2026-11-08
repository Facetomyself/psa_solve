# 2026-09-28 CF 请求链地图

只读汇总。不改求解代码。不写 cookie、token、ray 全值或指纹原值。正式 trace 只给路径类计数，没有时间序，下面的顺序来自 2026-08-15 浏览器事实和 2026-08-16 recovery 设计；2026-09-28 只作计数对照。

## 1. 浏览器侧请求顺序

| 步 | 方法 | 路径模板 | 状态码角色 |
|---|---|---|---|
| 主文档 | GET | `cert/{id}/psa` | 403 或 429，且 `cf-mitigated: challenge` 才是 managed 窗口。2026-09-28 主文档 GET 403，该头出现一次。无此头的 200 不是求解结果 |
| orchestrate | GET | 旧：`/cdn-cgi/challenge-platform/h/g/orchestrate/chl_page/v1`。fresh：`{id}/{id}/h/b/orchestrate/{id}/v1` | 脚本体。fresh sha256/16 `aa2b09a484f556d1`，238694 bytes。2026-09-28 该类事件 2 |
| jsd/oneshot | POST | `/cdn-cgi/challenge-platform/.../jsd/oneshot` | 2026-08-09：约 15s 后写 lease cookie，主文档仍可 200。2026-08-15 某版 orchestrate 不引用 jsd。2026-09-02 只有 oneshot=4、无 fo。2026-09-28 oneshot=2，与 managed 链并存，角色未定序 |
| fo | POST | `/cdn-cgi/challenge-platform/h/{flow}/fo/{id}:{ts}:{hash}/{ray}/{token}` | 站点与 `challenges.cloudflare.com` 各一轮是旧浏览器事实。旧 Node 为 fo×2，长度约 2178 再约 4599；第二轮 200 签发 clearance。2026-09-28 fo 事件=8，不是 solve 成功 |
| eb/managed | POST | 两套旧模板：`.../h/g/eb/{id}:{ts}:{hash}/{ray}/managed`，或 `/eb/{id}/{ray}/{token}` | 旧浏览器/RuyiDOM 会发；旧 Node 常缺。宽松窗口里 eb 不是 clearance 必要条件。2026-09-28 与本地都是 0 |
| 回读 | GET 或同路径 POST | 原 `cert/{id}/psa` | 同 lease。README：签发后约 5s 才有效，立刻回读仍 403。成功口径是 HTTP 200 且业务字段完整。2026-09-28 同路径另有一次 POST 200、无 challenge 头，只是存在性 |

flow 字母旧材料是 `g`，fresh orchestrate 路径是 `h/b`。不要把两套模板合成一条 URL。

## 2. 参数角色

页面注入（init，约 18 键；引擎可读到 33 键）：`_cf_chl_opt`，以及 `cType`（managed）、`cTplV`（5）、`cvId`（3）、`cH`、`cN`、`cRay`。orchestrate 查询段 `ray` 也是页面下发的不透明 id。

脚本生成：`h/` 后的 flow 段；fo 的 `{id}`、`{ts}`、`{hash}`、token 段（来自 `_cf_chl_opt`）；`$` 分隔 body。旧 RuyiDOM 映射 21 个混淆键，同材料 Node 29 字段、RuyiDOM 20 字段。跑深后多出 `CqJg7`、`cseK1`、`jWOLY8`，页面标志 `cf_chl_rc_ni`。`UpvLO0` 产出是 16 字节 / 128 位哈希类，不是明文指纹。

不透明，只记类别：`cH`/`cN`/`cRay` 原值、ray、token 段、fo/eb body、fo 响应体（加密 blob，非 JSON）。cookie 只记名：`__cf_bm` 两段刷新，`cf_clearance` 在接受的 fo 之后出现。值不落笔记。

## 3. Node runtime 覆盖面

`run.js` 导出用法是 vm 执行入口（求解 JSON，或 `verify` GET）。`code.js` 导出 `{booted, config, document}`，安装序：`config` → `host-globals` → `host-dom` → `host-async` → `patches` → `transport`，再加 Proxy 垫底。

| 补丁 | 宿主缺口 | 模块 |
|---|---|---|
| P1 | `window.UpvLO0` | `lib/patches.js` |
| P2 | `window.ZHfDS6`（eval 别名） | `lib/patches.js` |
| P3 | `setTimeout`/`setInterval` 变长参数 | `lib/host-async.js` |
| P4 | `document.cookie` 增量 jar | `lib/host-dom.js` |
| P5 | XHR 响应头与事件字段 | `lib/transport.js` |
| P6 | `Proxy` 的 null/undefined target | `code.js` |

其余宿主面：globals 的 window 别名、screen、navigator、performance、DOM 类；dom 的元素 stub、document、storage；async 的 Worker、四类 Observer、Blob、URL。这些是 2026-08-15 材料上的外部宿主补丁。

**没有覆盖** fresh orchestrate `aa2b09a484f556d1`（238694 bytes）。它不同于 demo6 `437c1820aeaaba6f`（227853 bytes），也不同于旧 229681 / 228910 字节档。2026-09-28 RuyiDOM 未注入 `runtime/code.js`。

## 4. 2026-09-28 分歧

正式 trace `rt_20260928061614_ee71af43b2`：orchestrate=2，fo=8，jsd/oneshot=2，eb/managed=0，主文档 GET 403。这只证明 managed 窗口出现过。

本地 RuyiDOM（`diagnostics/ruyidom_runner.js`，无 cookie，无全网，`pumpMs=15000`）：fo=0，eb=0，stdout 空，wire 未落盘。第一个错误是 eval 行 `TypeError: can't access property "call", KP is undefined`。随后 FATAL 主机名依次为 `challenges.cloudflare.com`、`www.psacard.com`，两行都没有路径。

## 5. 后续 RuyiDOM 外部宿主缺口

只列宿主面。不做 opcode、字节码或 VM 内补丁。

1. `KP` 在第一次 `.call` 前是 undefined。先确认它应是页面或 orchestrate 注册的全局，而不是去改调用点。
2. `challenges.cloudflare.com` 与 `www.psacard.com` 的无路径请求没有本地应答。缺的是 document/XHR 的源站映射，不是放行全网。
3. 本轮 cookie jar 为空。若脚本在提交前读会话，缺口在 `document.cookie` / storage，不记录原值。
4. P1–P6 未装进这次 Gecko。`UpvLO0`、`ZHfDS6`、变长定时器、cookie 合并、XHR 头、Proxy null target 都还没在 fresh 脚本上复验。
5. 更早的 `history.replaceState` SecurityError 本轮不是第一错。eb 两边都是 0，不要把 eb 当下一刀。
6. `createElementNS` 在 RuyiDOM 上曾是原生能力；本轮还没走到那一层，不要预先当缺口。

证据：`analysis-progress.md` Current State、`20260928-ruyitrace-formal.md`、`20260928-ruyidom-fresh.md`、`runtime/code.js` 头注释、`README.md` 补丁表、`findings.json` F1–F7、`psa/docs/cf-clearance-recovery-integration-analysis-20260816.md`、`psa/docs/web-risk-control-analysis-20260809.md`。
