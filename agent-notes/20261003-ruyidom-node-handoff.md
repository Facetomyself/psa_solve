# RuyiDOM → 纯 Node 补环境交接（2026-10-03）

## 结论

RuyiDOM 已经给 Node 一份可迁移的**行为合同**：挑战页加载顺序、五段 `/fo/` 外部边界、状态/协议/响应 header 名、Cookie 名谱系、response→DOM 的分支观察，以及发出 `/fo/` 之前实际触达的若干宿主 API。它没有给出可直接搬运的通过值：`3488` 是当前 session 收到的 opaque `cf-chl-out` 响应长度类，`3792` 是 Firefox 通过分支的另一长度类，二者都不能作为 Node 输入或目标常量。

当前 `3488/noform` 应定性为**响应语义/会话输入分支缺口**，不是“Node 少一个 `form` API”。本地已经读到 `cf-chl-out` 响应并进入诊断 DOM；真实 Firefox 在不同的同轮上下文收到通过分支后才创建 form、提交证书 document POST。Node 还缺同一 session 的新鲜请求输入、真实响应 envelope 和 response→DOM 消费 trace。

## 可迁移的 host facts

| Node 可迁移事实 | 当前证据 | 迁移边界 |
|---|---|---|
| 传输与请求角色 | causal observer `a7e045b6cf194921bb229b6741e59b8b`：page GET + 5 个 challenge-fo POST + unresolved GET；FO 为 h3；`proxy.type=0` 保留 | 迁移协议/状态机形状；不能把 h3、TLS、出口、UA 视为普通常量，必须由 Node 同一 lease 实测 |
| FO 顺序与响应分类 | Firefox `rt_20260929103550_341b734038`：page-host FO ×2、challenge-host FO ×3，前段 `text/plain`，后段 `text/html`；RuyiDOM 已能发 FO | Node 可按序生成请求并记录 method/path/status/body 长度类；不能按“第 N 次”硬编码 body 或跨轮 response |
| 通过面 header/Cookie 名 | 浏览器末轮 response 有 `cf-chl-out`、`cf-chl-out-s` 和 `cf_clearance`/`__cf_bm` 的 `Set-Cookie` 名；本地 causal run 只证明 header 名/站点分区名 | Node CookieJar 要记录 writer→consumer→egress；只迁移名字和存在性，禁止填入 Firefox 值 |
| bootstrap/DOM 因果形状 | causal chain：`document.write` → `createElement` / `innerHTML`；最后是 `h2/p/ol/a` diagnostic-copy，`forms=0`、`submits=0` | Node 需要等价的 response consumer/branch observer；不能用 `document.createElement('form')` 假造通过 |
| 真实浏览器的 pre-FO 宿主顺序 | Firefox DOMTrace 摘要：`randomUUID`、`performance.getEntries`、`PerformanceObserver.observe`、RTC data channel/`createOffer`/`setLocalDescription`、iframe/contentWindow，之后才 XHR open/header/send | Node 只实现被目标实际读取的接口语义和参数形状；RuyiDOM 的 `createOffer` 未 settle 不是当前发不出 FO 的闸，不先补它 |
| 全局/realm 行为 | RuyiDOM 旧桥显示 `window.KP` 不存在，编排函数落在另一 global/realm；`KP.call` 是执行边界 | Node VM 要保持 `window/self/global` receiver 和 callback 注册语义；不要定义任意 `window.KP` 把错误压过去 |
| RuyiDOM 运行器修复的局部事实 | `history.replaceState` 的 SecurityError、lazy `script.src`、about:blank 文档身份、资源映射是 RuyiDOM runner 适配事实 | 这些是 Gecko runner 适配，不是 Node 目标环境事实；Node 应直接提供正确 origin/resource loader，不能搬运 about:blank workaround |
| 请求/响应交接接口 | `runtime/run.js` 已有 `CF_CAPTURE_ONLY`：Node 产生 request JSONL，接收 response envelope 后继续执行 | 可迁移接口协议（status、header 名、body、Set-Cookie、readyState/onload）；当前实现把外网层留给 Python，纯 Node 最终需把同一 envelope 机制收回 Node transport |

## 3488/noform 的准确定位

1. causal observer 在最后 page-host FO（reqLen 8695）之后读到带 `cf-chl-out`/`cf-chl-out-s` 的 200 响应，body 只记为长度类 `3488`；随后首次 DOM 是 `h2`，尾部是排障 `h2/p/ol/li`，没有 form/submit/cert POST。
2. Firefox browser fact 在通过轮收到另一响应形状（文档摘要记为 `3792`），随后创建 form 并发出证书 document POST 200；主 Firefox receipt `rt_20260929103550_341b734038` 的 raw root 为 `980d1002ee040e0e513593a412600ad6ef2515b070a7a0b623659764b8b688c2`。
3. 有头对照中，本地两个大 FO 请求约比通过分支小 9 KB；这说明分叉在请求/session 输入与边缘响应语义，不能归因于“缺 form 方法”。`3488/3792` 是观察标签，不是可优化的分数或可复制 body。
4. 现有 RuyiDOM handoff 是 urllib→Gecko 的逻辑材料/Cookie 交接，不是同 TLS、同导航、同 lease provenance；异会话 body 回放已在首包触发 `InvalidCharacterError`，所以不能把 Firefox response 搬给 Node。

## Node 仍缺的同一 session 输入/trace

- **Fresh material binding**：同一次挑战的 HTML、orchestrate、Turnstile 资源、ray/时间/nonce 类输入及资源 hash；不能复用历史材料或只拿 Firefox receipt。
- **完整 FO envelope**：Node 自己产生的每一条 FO request（method、path class、header 名、Cookie 出站、body hash/长度）和同一 lease 的真实 response（status、header-name set、body hash/长度、Set-Cookie 名）。仅有 RuyiDOM 的 3488 label 不够。
- **会话/传输上下文**：`__cf_bm`/`cf_clearance` writer→consumer 链、UA/fingerprint/IP/HTTP3/TLS/连接策略；这些值必须由 Node 本轮生成或实时收到，不能从 Firefox profile 导入。
- **response→DOM 消费 trace**：记录页面读取哪些 response/header/body 属性、解码后选择了哪条分支、首个 DOM 操作、是否创建 form、是否 submit、是否产生 cert document POST。当前 Node v8trace run `v8-20261003021537-lhw7em` 是 stub DOM：FO=0、document POST=0、form.submit=0，不能解释 3488 分支。
- **最终验收边界**：Node 产生 cert document POST 后，还要在同一 client-owned lease 等待约 5 秒并读到业务 200；`cf_clearance` 名存在、widget complete、challenge endpoint 200 都不能替代 `serverAccepted`。

## 纯 Node 的下一刀

沿用现有 `runtime/run.js` 的 capture-only envelope 设计，做一轮**同一 session 的五段 FO canary**：Node 负责页面脚本、CookieJar、请求生成和 response 消费；每次 request/response 只落脱敏的 seq、path class、status、协议、body 长度/hash、header 名和 Cookie 名。验收点是 Node 是否在真实末轮 response 后进入 form/submit/cert POST；不要回灌旧 Firefox body，不要合成 `cf_clearance`，不要先补 `createOffer` 或相邻 host getter。

若 Node 直连 transport 不能保持同样的 HTTP3/TLS/会话上下文，先把失败标成 transport/session provenance，保留 Node executor 与 envelope 交接；只有同一 session 的 response 已被页面合法消费后仍落在 noform，才进入一个有证据的单 host semantic shim。当前 `experimentHygiene=stop-search`、`serverAccepted=false`，不得用这刀清除现有闸门。

## 证据路径

- RuyiDOM causal live：`evidence/web/diagnostic-causal-observer/restricted/a7e045b6cf194921bb229b6741e59b8b/`、`agent-notes/20260930-causal-observer-live.md`
- response→DOM 分类：`agent-notes/20260930-causal-observer-chain.md`
- Firefox browser fact：`evidence/web/ruyitrace/rt_20260929103550_341b734038/`、`agent-notes/20260928-ruyitrace-formal.md`
- FO/清关顺序与同会话限制：`agent-notes/20260928-fo-browser.md`、`20260928-fo-response.md`、`20260928-post-clearance.md`
- Node stub gap：`agent-notes/20261003-v8trace-bottleneck.md`、`evidence/web/v8trace/v8-20261003021537-lhw7em/`
- Node envelope entrypoint：`runtime/run.js`、`runtime/lib/config.js`
- 当前 facts：`contracts/auto-decision-facts.json`
