# 正式限定 BODY.attachShadow 修复与复跑 / 2026-10-20

## 执行摘要

**首个 attachShadow TypeError 已被实际对照消除，但求解未完成。** patched 按真实 options.mode 创建 closed ShadowRoot，随后走到该 root.querySelector；root 未填充、真实返回 null，下一错误为 zF 内 null.appendChild。没有伪造查询命中，也没有继续补下一个 API。

baseline 与 patched 各只运行一次，均约 5 秒、exit0、未 timeout；外层硬 timeout15 秒。两边最终都仅有 1 次 POST XHR.open 意图，body 未 send，未出现 FO/证书提交/真实网络边界。此处必须区分首错修复与服务器求解成功。

## 1. 本次正式授权与范围

用户本轮明确原文：**“正式工作流允许这次已证实的单 surface 修复与复跑”**。该外部状态变化被落实为项目独立一次性合同，不是把 goal 或普通“继续”当解锁。

- `diagnostics/shadowroot-repair-20261020/authorization.json`：精确限定 BODY.attachShadow(options.mode) 与返回 ShadowRoot 的已证 appendChild/#id-query/identity/tree scope；断网固定输入；baseline/patched 各1次；15秒 timeout；不改业务完成轴/卫生状态。
- `fixed-profile.json`：锁定原输入、browser/options 回执、baseline/patched 副本、实现模块、旧 fail-closed preload、Node runtime 与受保护原 runner/合同的 hashes。
- 当时的 profile SHA-256 是 `7043777b9c260f6b16bf555cebfcefd14b5794a966500c63bfc74ff9ef87f4b8`。2026-10-20 取消次数和时限后，适配器改为接受 `f700f5f29527e19aa0b12709d9393bf9350520fbb82a1771e330e3052bd051d9`。仍不接 caller 自报 runner/argv。
- 现有全局诊断入口只支持已固定的 RuyiDOM profile，无法复用为本次 Node surface 合同。因此采用项目限定 check→claim→execute→record 模式，不修改 web_case.py，不增加全局可执行范围、不建立另一套 goal/dispatcher 状态机。
- 这次运行当时用 exclusive create 写过 `claim-binding.json`。该次数、15 秒和“过期不退还”已从适配器移除。旧 claim、receipt 和日志留在原文件；以后再 claim 会先把原字节抄到同名 `.historical`。
- `receipt.json`：status=executed-hold，returnAction=refuse_host_enumeration，protectedUnchanged=true，businessAcceptance=not-asserted。

本轮主线 dispatcher 仍 refuse_host_enumeration / blocked；facts 已有 dualCondition=true，其余 hygiene=stop-search/完成轴均未改。本次授权只作用于此限定 receipt，不伪造外部请求移动，也不将全局 gate 改 ready/run。

## 2. 输入与对照设计

复用上一轮已校验的 4 份历史 snapshot（9月28日页面/API/orchestrate，9月29日 iframe）；原 inline source hash 为 `05102bb5158cd0ba9a41329021f124cad8778a9a556db9a0e802b11c07115262`。baseline 与 patched 的运行记录均实际确认同 hash、唯一原始 call-site。

baseline 取上一轮 body-typing control：BODY tag/prototype 已正确，attachShadow 仍缺失。两边增加完全相同的 WeakMap node-edge bookkeeping 和结束时 XHR意图计数，避免仅看早期 xhrCount=0 漏掉异步动作。该 bookkeeping 包装旧 appendChild、保留原返回行为，用于记录实际构造子树，不给未观察节点制造新身份，不补 createElement/NS、setAttribute、selector fallback 或新 API。

patched 相对 baseline 的唯一差异是安装 evidence-bound BODY.attachShadow/ShadowRoot surface，见 `single-surface.diff`。没有改目标函数/VM/opcode；沿用原有同点诊断观察 IIFE，不扩大 target 插装面。

断网复用 `diagnostics/receiver-provenance-20261020/offline-preload.cjs`，hash 已锁：HTTP/HTTPS/H2/TCP/TLS/UDP/DNS/undici/child-process/worker 等已知 Node 外联入口 fail closed；旧 XHR仅记意图，__deliver 明确拒绝，fetch明确拒绝。无真实响应回放。没有改变机器全局代理/防火墙；这是既有脚本的接口级防护，不冒称 OS 安全隔离。

## 3. 已实现的精确 surface

实现：`body-shadow-surface.cjs`，只在独立副本安装。

- 从调用实参 options.mode 读取值，验证 open/closed；实际运行读到 closed，与静态恢复相符，不硬编码历史模式。
- 返回稳定 ShadowRoot/DocumentFragment 对象；host、ownerDocument、mode 绑定；closed 时 host.shadowRoot=null，调用者仍保有返回 root。
- root.appendChild 返回原 child identity，维护私有节点树；querySelector 只支持本 slice 已观察的简单 #id，在该 root 实际子树遍历，miss=null、重复命中返回原对象，不看顶层旧 HTML，不造 DIV 兜底。
- 无通用 Proxy、无 [native code] 伪装；非法 receiver、重复附加、循环插入及超出已观察语法/option 明确拒绝，不隐式声称全浏览器 DOM。

限制：旧 createElement/NS 的 SCRIPT 错型、元素层 query/parentNode/ownerDocument 等失真没有顺手修复；本模块的私有树用于 root 消费合同，不宣称旧元素的所有公开 DOM 属性已正确。没有 HTML parser、SVG full namespace/brand、iframe realm、events/layout 或完整 WebIDL。这里只测试和执行已证 surface，不可把这些边界删掉说成完整环境补全。

## 4. 实际运行对比

正式回执：`receipt.json`、`baseline.execution.json`、`patched.execution.json`；脱敏边界摘要：`boundary-comparison.json`。原始日志留 restricted，不复制到聊天。

| 项 | baseline | patched |
|---|---|---|
| Target 执行次数 | 1 | 1 |
| Same original source/call-site | 通过 | 通过 |
| 原 attachShadow not-callable TypeError | 复现 | **消失** |
| root 创建 | 无 | 1，mode=closed |
| root.appendChild 事件 | 0 | 0 |
| root.querySelector 事件 | 0 | 1，真实 miss/null |
| 末端异常 | __rpRecv[__rpKey] is not a function | Cannot read properties of null (reading appendChild)，zF |
| 最终 XHR.open 意图 | 1 POST，body=null | 同样1 POST，body=null |
| 网络/响应投递 | 无真实发送/回放 | 无真实发送/回放 |

XHR意图是5秒结束时采样，和初始 frameEval 后立即打印的 xhrCount=0不是同一时刻；这不是新线上请求或 FO boundary-moved。既有 deliveryEventCount=1 是其 request记录，不是收到/回放了一份 response。role=other，不把它包装成完成 FO。

**可证结论**：修复已使控制流越过已配对 BODY.attachShadow 调用，并实际消费返回 root。原局部不可调用错误已解决。

**不可证结论**：没有证明完整 ShadowRoot/browser parity；patched root 在报错前没有收到任何 appendChild，和 canonical browser root 的3 append/6 query 非同一形态。当前新缺口是“root消费时所需子树未建立/未挂入，query返回null后仍被当元素使用”，不是 query实现应该伪造节点的理由。未定位造成该 UI bootstrap/分支差异的更早条件，不把任何相邻 API猜成根因。

本 slice 到这里结束，不对空树查询继续摸字段、不补第二个 API、不增加执行次数。

## 5. 验证与合同完整性

- Surface 单元测试38/38：显式实参模式、closed/open暴露、host/document身份、预构建子树append/query、重复identity、隔离其它节点、miss/null与拒绝语义。`surface-tests.json`。
- Receipt adapter 单元测试：固定 profile 与保护 hash、不可传任意 profile、允许再次写入、profile 篡改拒绝。测试不执行目标。
- check/claim/execute/record 全部实际完成，baseline/patched exit0、timedOut=false；record时6份原 runner/合同文件hash均不变。授权/profile记录的输入和模块hash全通过重验。
- 没有修改 runtime/run.js 等用户脏runner、facts、workflow、原 mirror/realm wrapper；没有commit/push。主线程后续若再次next会合法更新dispatcher stamp，不抹掉record当时的完整性事实。

## 6. 当前下一步与目标剩余差距

下一步已从“给错型SCRIPT硬补”收窄到**真实ShadowRoot返回后，UI子树构造/挂接为什么未发生**；先用本次既有日志及同源canonical的创建→赋id→append链定位首次缺失调用/分支，不猜selector、不造节点。若需要再执行，仍只做已证的同一机制。次数和 15 秒上限已从本项目合同移除。

Node fresh session/自然FO请求响应/证书提交/parity/同lease独立readback均未达成；本次明确只解决原首错和推进一个本地执行边界，不冒充已完成求解。RuyiDOM live五跳后排障仍是另一条尚未闭合的因果链。
