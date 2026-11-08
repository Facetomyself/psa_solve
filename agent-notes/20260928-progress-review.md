# 2026-09-28 补环境进度复查（只读）

Case: `psa-cf-5s-shield-20260815`  
Scope: 仅 2026-09-28 这条补环境线。web-case 必须仍视为 `patching`。没有 `serverAccepted`。  
本笔记不写 cookie / token / ray / query / body 原文 / 证书号 / 完整 URL。

核对：
- `analysis-progress.md` Current State
- `agent-notes/20260928-ruyidom-bridge.md`（KP、`/fo/`）
- `agent-notes/20260928-fo-local.md` / `20260928-fo-browser.md` / `20260928-fo-response.md`
- `workspace.json` 的 `next` 与末三切片（`slice-fo-response`、`slice-progress-review`、`slice-direction-sources`）
- 代码搜索：`diagnostics/ruyidom_bridge.js` 的 `loadFoReplay` / `foResponseManifest`；`diagnostics/bridge-input.json`

## 1. 已证实的进度

### 1.1 宿主修补（成立）

- 文档进页面；orchestrate 与 Turnstile `api.js` 按捕获 script URL 本地应答；惰性标签保留以便读 `script.src`。
- `history.replaceState` 与 `HTMLScriptElement.src` getter 在页面 realm 为 native-like；SecurityError / TurnstileError 已消。
- KP 缺口用编排前原型镜像解决：方法落到 Window；探针仍是 `kp=undefined`、`kpOwn=false`。没有定义 `window.KP`，没有改 orchestrate 字节码。
- 离线两轮一致：`errors=[]`，`orchestrate=1`，`eb=0`，`jsd=0`，Turnstile onload×2，`xdiN1` 在 Window 上是 function。
- 通道未开 `-AllowNetwork`；necko cancel 只为离线活到摘要，不是解题响应。

### 1.2 请求已发出（成立）

- 页面自己的 XHR 发出 `/fo/`：不回放时 `fo=3`，均为 POST，路径模板稳定，header 名只有 `cf-chl`、`cf-chl-ra`，body 各 2306 字节，sha256 每条/每轮不同。
- `served=false`：资源 handler 对 `/fo/` 回 `null`，计入 blocked。这不是服务端接受。
- 时间序：三组 `/fo/` 出现在摘要探针之前；本地未 settle 的 `createOffer` 不阻止发 fo。有头材料里 createOffer 在首次 fo 前已 settle，但那不是本地「发不出 fo」的闸。

### 1.3 响应回放失败（成立）

- 用另一次有头捕获的首条 `/fo/` 200（异会话 body）按序回放两次：只发出 1 次 POST，`served=true`，随后 `InvalidCharacterError`（eval line 1 col 287）；无第二次 `/fo/`。
- 不回放时同页连发 3 次；异会话回放把链截断。异会话响应体不能当本轮答案。
- 代码核对一致：`loadFoReplay` 在无 `foResponseManifest` 时返回空数组；`bridge-input.json` 当前无该字段，默认回放关闭。代码仍保留可选开关，需显式打开。

## 2. 说过满或证据不够的地方

- 「先补 `/fo/` 本地 200 响应」方向对，但「任意捕获形状的 200」已被证伪为不够：异会话首包会炸链。笔记若读成「有响应即可继续」过满；精确说法是**需要与当次请求绑定的可消费响应**，而本地尚无生成能力。
- 页面侧是否读到 status/responseText：无回放时只有 send + cancel，缺 readyState/status 探针；回放失败轮证明页面会吃响应并 eval，但不能外推「空 cancel 时页面读到了什么」。
- 观察计数器（Worker/iframe/RTC/uuid/entries/honk）只证明调用有无，不等于这些 API 语义已补齐。
- `createOffer` 未 settle 可能是并行指纹缺口；它**不是**当前 fo 发出闸，也不应抢下一刀，除非「当次绑定响应」假说也被证伪。
- 有头四次 fo 200 后出现 clearance **名**、再 POST 回证书页：那是浏览器事实，不是本地 `serverAccepted`，也不是补环境完成。
- `workspace.json` `known.lastConclusion` 仍写 2026-09-02 的 `production-integration-pending` / jsd-only，与 Current State 的 09-28 fo 线并存；读状态时以 Current State + 本线笔记为准，勿把旧结论当本轮求解结果。

## 3. 后续方向

### 允许

- 保持 `external-host-only`、单 surface 实验；继续把 case 标为 `patching`。
- 扩展**只读**探针：fo 后 XHR readyState/status/response 长度（或等价），仍一次只动一个外部面。
- 设计「当次请求绑定」的可证伪假说：本地应答必须来自**本轮发出的请求材料/形状**，或受控 stub 明确记录是否推动下一跳；失败则保留反证，不捆绑多面修补。
- 对照公开资料时只谈多轮 fo 与响应绑定机制，不把异会话落盘 body 当答案写回默认输入。

### 明确禁止

- 改 opcode / VM handler / orchestrate 字节码 / safe AST 当补环境捷径。
- 定义或伪造 `window.KP`。
- 把「没传 `-AllowNetwork`」写成用户禁令。那是 `run.ps1` 的默认开关，不是 case 合同。用户没有要求纯离线。
- 把异会话 `/fo/` body 默认接回 `bridge-input.json` 并当作求解成功。
- 把 web-case 标 `completed`，或把 `served=true` / 无错 exit / fo 计数上涨写成 `serverAccepted`。
- 硬编码历史 challenge 资源、cookie、nonce、签名输出进仓库交付物。

## 4. 卡点定性（不要改口）

下一刀**不是**「再补一个普通宿主 API 就能过」的缺口。

当前硬卡在：**响应必须与当次 `/fo/` 请求绑定**；异会话回放已失败。这不是 `serverAccepted`，也不要改口叫 `serverAccepted`。本地仍停在 patching：请求形状可观测，可消费且绑定的响应链未建立。

若资料检索也只确认「多轮 fo 依赖服务端对当次 body 的应答」，则补环境阶段应标边界：`localReproduced` 的请求侧已部分到达，响应侧需协议/材料同源或另开受控求解通道——仍禁止把异会话 body 或联网提交冒充验收。

## 证据指针

- `analysis-progress.md` Current State
- `agent-notes/20260928-ruyidom-bridge.md`
- `agent-notes/20260928-fo-local.md`
- `agent-notes/20260928-fo-browser.md`
- `agent-notes/20260928-fo-response.md`
- `diagnostics/bridge-input.json`（无 `foResponseManifest`）
- `diagnostics/ruyidom_bridge.js`（`loadFoReplay` 空路径 → 空数组）
- `workspace.json`：`next=progress-review-and-sources`；末相关切片含 `slice-fo-response` blocker「异会话首包 InvalidCharacterError」
