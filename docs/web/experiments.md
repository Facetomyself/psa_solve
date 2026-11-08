# Experiments

Case: `psa-cf-5s-shield-20260815`

Append-only experiment and dated notes. Do not read this file unless `docs/web/index.md` names a section.

<!-- generated:experiments -->
| id | changedVariable | result |
| --- | --- | --- |
| exp-ua-h3 | Firefox/155 and quoted h3 mapping | pass |
| exp-fresh-profile | empty headed profile | pass |
| exp-pointer-trail | spaced trusted pointer moves | fail |
| exp-opaque-byte | stop scoring the opaque byte | inconclusive |
| exp-iv8-offline | iv8 0.1.4 offline page.load of the same snapshot | fail |
| exp-ruyijs-attachshadow-existence-20261102 | ruyijs Element.attachShadow pre-patch eval | present |
<!-- /generated:experiments -->

## 2026-11-02 ruyijs existence

- 执行器 ruyijs 0.1.3，同一条离线 load_page，无 navigate / proxy / live HTTP。
- 变量：`Element.attachShadow` 存在性。browser 已读；本地 `call=ok`，不是 miss。
- 未落地 expose/set patch，未登记新 evidence-run。

## 2026-09-29 CLI baseline

- 执行器改为主线 `mcp/ruyidom-mcp/dist/cli.js run --allow-network`。脚本仍是现有桥接，没有新字段。
- 结果：`/fo/` 200，`cf_clearance` 名字落地，widget 点击结束状态 0，证书 document POST 没有出现。
- 分类为环境缺口且请求边界未对齐。相邻宿主字段不再枚举。

## 2026-09-29 script rotation

- 有头 trace 的 orchestrate 正文 236278 字节，摘要 `1f66bff822b13c36`。同日在线抓取 233322 字节，摘要 `375d30eae3a92c7e`。查询参数按挑战轮换。
- 这是动态脚本，不是新的 method/url/status/body 长度类，也不是证书 document POST。
- `next` 仍是 `refuse_host_enumeration`。没有新开 RuyiTrace，没有把任一会话的计时、矩形或解码字节写进桥接。

## 2026-09-29 payload class

- 问题拆成两件：服务端有没有下发建表单的载荷；载荷已经是那一类时，本地为什么没有 `createElement("form")`。
- CLI 基线落在第一件。第二次解码长 2132，前 4000 字节里没有长度达到 16 的可打印游程。`Map` 写入 12 次，键长最大 38，没有整段载荷。`forms` 0。慢验证文案是脚本自带模板。
- 有头清关响应也是 3792 字节，随后整段进入一次 `Map.set` 并建表单，再出现证书 document POST。本地外层尺寸相同，结构不同。
- `/fo/` 尺寸类：有头 2252→106880、4396→798124、85260→6620、8620→3792。本地 2252、4716、84418、87564、8759，解码链里有 106876 和 80156，没有 798124。widget 子文档通道 25948 字节，结束状态 0。
- 这不是 `serverAccepted`。没有新的宿主字段。`bridge-1.json` 和 `bridge-2.json` 没有写。

## 2026-09-29 fresh control

- 新开 interactive RuyiTrace `rt_20260929073424`，runtime 3.3.0 verified，`fingerprintMode=baseline`，`dom-observe`。三道 gate 通过，已登记为当前浏览器事实。没有改桥接。
- 有头五次 `/fo/`：2252→106876、4471→779020、85271→117968、88482→6700、8727→3792。清关包带 `cf_clearance` 这个名字。随后证书 document POST 2221→154040。
- CLI 基线的五次请求长是 2252、4716、84418、87564、8759。第一步响应和最后一包 3792 同档。本地解码没有 779020，也没有 117968。
- 9 月 28 日那条四步链（中间 798124，大包直接 6620）对不上今天的脚本。对照改用这一条。
- `experimentHygiene` 仍是 `stop-search`。这不是 `serverAccepted`。

## 2026-09-29 wire class

- 桥接只加了响应线长计数，没有新的宿主字段。三次新挑战的页面结果仍是 `forms` 0、`mapMax` 38、没有证书 document POST。
- 配对结果：`4706→584082`、`84098→88646`、`87319→5126`、`8716→2901`。第一步顶层正文 106872，协议是 h2；有头第一步是 h3，未压缩同为约 106876。
- 有头中间线长是 561995 和 86337。本地 584082 和 88646 是同一档。779020 / 117968 是有头解压后的正文，不是本地没收到的一档。
- 顶层 `atob` 只有 106872 和清关 3792。大包在 widget 文档里完成。清关包尺寸已经和有头相同，解开后仍不建表单。
- 这不是 `serverAccepted`。`bridge-1.json` 和 `bridge-2.json` 没有写。

## 2026-09-29 chain shape

- 有头顺序：证书文档 GET 403（h2）→ orchestrate（h2，带 cookie）→ Turnstile 脚本（h2，跨站，无 cookie）→ 页面 `/fo/` 2252（h3）→ Turnstile 子文档约 259484 字节（h3）→ 子文档三次 `/fo/` → 页面清关 `/fo/` 8727（h3，`cf_clearance`）→ 证书 document POST。jsd 在业务页之后。
- 本地走到清关为止。页面 `/fo/` 与 `cf` 主机 `/fo/` 的分工一致。子文档正文 247149 字节。中间线长同档。没有证书 POST。
- 请求形状：`/fo/` 都是 `text/plain`，`sec-fetch` 为 empty/cors/same-origin，带 `cf-chl` 和 `cf-chl-ra`。cookie 只在页面那两包上。证书 POST 是 `application/x-www-form-urlencoded`，document/navigate/same-origin。
- TLS：两边都是先 h2 再升 h3。有头的第一包页面 `/fo/` 已经是 h3，本地仍是 h2，正文同为约 106872。捕获里没有密码套件或 JA3。有头 UA 是 Firefox/155，长度 80；本地覆盖成 Firefox/135，长度也是 80。有头 `accept-encoding` 含 zstd。

## 2026-09-29 egress

- 有头捕获请求 `proxy.mode` 是 `direct`。抽到的包都是 `proxyUsed=false`、`proxyTransport=none`、`proxy=null`。本地 CLI 和挑战抓取脚本都没有设置 `HTTP_PROXY` / `HTTPS_PROXY` / `ALL_PROXY`。Windows 系统代理 `ProxyEnable=0`。应用层两边都是直连。
- 本机 Clash Verge 在跑，TUN `enable=true` 且 `auto-route=true`，模式 `rule`。`DOMAIN-SUFFIX,cloudflare.com` 和最终 `MATCH` 都进命名策略组，`GEOIP,CN` 才是 `DIRECT`。页面站和 Turnstile 主机都会进同一条透明出口，只要抓包当时 TUN 也开着。浏览器仍报直连，因为代理不在应用里。
- 同一天的有头对照在这台机器上走完了证书 document POST。本地同一出口也拿到了 `cf_clearance` 和同档线长。硬封禁或“请求太多整段被拒”对不上这两组结果。3792 解开后不建表单，仍然是两边客户端形状的差，不是出口有无代理的差。

## 2026-09-29 ua155 h3

- `general.useragent.override` 改成有头包上的 Firefox 155 发行串，长度仍是 80。请求头 `ua155` 为真。
- 页面主机预置 `h3=":443"`，`backup_timer_delay` 5000。第一包页面 `/fo/` 从 h2 变成 h3，`altUsed` 为真，请求长度 2252。后面四包 `/fo/` 也是 h3。
- 不带引号的 `h3=:443` 会把第一包协商成 HTTP/1.1，清关退到 3488 且当轮没有 `cf_clearance`。已换成带引号的映射。
- 带引号这一轮：站点分区里有 cookie 名 `cf_clearance`。清关解开后是 3488，不是之前 h2 上的 3792。`forms` 0，`mapMax` 38，没有证书 document POST。

## 2026-09-29 search notes

- 公开检索：`agent-notes/20260929-search-web.md`。`cf_clearance` 是边缘通行凭证，不是同页建表开关。UA 盖成 155 盖不住壳差异：135 的 HTTP/3 带后量子密钥交换，155 另有 QUIC v2 协商。
- 知识库：`agent-notes/20260929-search-kb.md`。`article/web-reverse/cloudflare-5s-v2-fo-pipeline.md` 把完成门写在 accepted 之后的 `form.submit`。有 cookie、无 form 是 `E_RUNTIME_NO_FORM_POST`。假 `window.turnstile` 会停在这一步。知识库没有 135 壳对 155 有头、或 h3 单独导致缺表单的归档。

## 2026-09-29 form branch

- 带 `cf-chl-out` 的 3488 包是纯 base64。`atob` 走了 3488→2616→1960。随后创建的是 `div/h2/p/ol/li`，不是 `form`。`forms` 0，`submits` 0，没有 `action`/`method`，没有 `replaceState`，也没有 `location` 跳转。
- Turnstile 已经 `render` 和 callback，消息里有 `complete` 与 `interactiveEnd`。不是假 `window.turnstile` 那条失败。初始页的 `md` 长 1215、`mdrd` 长 426，建表分支没有把它们抄进 hidden。

## 2026-09-29 fresh profile

- 新捕获 `rt_20260929103550`。没有 `profileSource`，没有 handoff，配置档是这次 run 自己的空目录。第一包证书 GET 没有 Cookie，只写下 `__cf_bm`。
- 清关 `/fo/` 响应仍是 3792，并写下 `cf_clearance`。随后证书 document POST 200，写下 `psa-locale` 和 `env`。干净配置档一样走完建表。残留 cookie 不是有头能提交的原因。

## 2026-09-29 behavior

- 这次有头是点击挑战，人手通过。事件分区记下 `pointermove` 6 次、`pointerover` 2 次，全部 `isTrusted` 且非合成。没有 `click` / `mousedown` / `mouseup` / `pointerdown` / `pointerup` 的 listener 调用；主文档采样可以漏掉验证按钮。
- 本地点击是窗体中心的一次 `mousemove`、`mousedown`、`mouseup`，没有 `pointer*`，也没有 `click`。widget 仍给出 `interactiveEnd` 与 `complete`，令牌长度 688，站点分区写下 `cf_clearance`。
- 有头清关请求长度 8780、正文 3792，随后建表。本地清关请求长度 8738、正文 3488，随后画出排障页。轨迹是还在的载荷形状差。它还不能单独证明跳过 `createElement("form")` 的原因，因为本地 widget 完成和清关 cookie 已经发生。第三个 hidden 仍不记成鼠标轨迹。`experimentHygiene` 仍是 `stop-search`。

## 2026-09-29 pointer trail

- 离线探针：`synthesizeMouseEvent("mousemove")` 已经派出可信 `pointermove`（`pointerType=mouse`）和可信 `mousemove`。这个运行时没有 `synthesizePointerEvent`，也没有 `sendPointerEvent`。
- 在线只加这一项：挑战开始后每 120ms 沿 8 个点重复移动，同一套合成参数，点击三连不变。`lookupRing` 有 `ptr:8`。站点分区仍有 `cf_clearance`。widget 仍是 `interactiveEnd,complete`，令牌长度 709。
- 清关请求长度 8770，正文仍是 3488，`chlOut` 仍是 `noform`，`forms` 0，`mapMax` 38，尾部仍是排障页。上一轮无轨迹时请求是 8738、令牌 688，用户激活本来就是 `0/1`。这段移动改变了清关请求长度，没有走进建表。

## 2026-09-29 blocker record

- 卡点记在 `docs/web/index.md`、`environment-patch.md` 和 `contracts/workflow-artifacts.v1.json` 的 limitations。
- 有头空配置档仍是正文 3792 加证书 POST。本地在 UA 155、h3 和可信指针轨迹之后仍是正文 3488、`forms` 0。
- `serverAccepted` 保持 false。不写 `bridge-1.json` / `bridge-2.json`。

## 2026-09-29 iv8 offline

- 社区版 0.1.4，上游 commit `950c9b937a510bb4c33909723ad3596807a44546`。只把当前挑战页和同一份 orchestrate 注入 `page.load`。没有真实 HTTP，没有回放别的会话的 `/fo/`。
- 页面 location 主机类是 page-host。可信 `pointermove` 在第一下抛 `TypeError`。
- orchestrate 进了定时器后抛 `TypeError`（缺函数）。`forms` 0，`submits` 0。netLog 里证书 GET 和 orchestrate GET 的 status 都是 0。
- `facts.iv8=diverged`。`experimentHygiene` 仍是 `stop-search`。这次不是 `localReproduced`，也不是 `serverAccepted`。

## 2026-09-29 iv8 real-request hold

- 离线 iv8 不作为 3488 和 3792 的对照。社区版没有 HTTP/TLS 栈，缺函数只能说明仿真缺口。
- 真实请求留在 RuyiDOM live。最近一轮五次 `/fo/` 都是 h3，清关请求长度 8770，线上正文 2676，解开后的类仍是 3488，`forms` 0，没有证书 document POST。
- 不把这批 `/fo/` 交给 Python HTTP 再注入 iv8。那会换成另一套 TLS，不再是当前 Firefox/155 + h3 会话。

## 2026-09-29 api.js pin

- 用户主线改成：解 `api.js`，读它对另一份脚本的完整性检测，再在同一 Firefox 会话里换脚本，对照 Worker 交进 `/fo/` 的结构。不补下一个宿主字段。`experimentHygiene` 仍是 `stop-search`。
- 有头 `rt_20260929103550` 单包索引：`/h/b/` 11，`/h/g/` 0。主站 `/fo/` 2，Turnstile 主机 `/fo/` 3。
- `api.js` 正文 86732 字节，sha256 `76763bb46224400a11af989831d62d06629aba6f67d50cac96afae4a590adf59`。gate profile `ast-safe`，另有 `function_constructor` 与 `dispatch_switch` 标记。

## 2026-09-29 api.js static read

- 安全 AST 输出 `diagnostics/live/turnstile-api-ast/final.js`，152617 字节。`chain_accepted=true`，范围只是 transform-only。字符串表、dispatcher、控制流平坦化没有解开。
- 可读控制流里没有对另一份 JS 做整文件 hash / SRI。`Ui()` 只在收到 iframe 的 `reloadApiJsRequest` 时，用原 `src` 换上自己的 script 标签，并带上升级查询参数。
- 它另外创建的是 widget iframe，不是 Worker。`/fo/` 的 blob Worker 不在这份 `api.js` 里。因此还不替换返回，也不在 Worker 边界插桩。
- 第二份脚本仍是 not-identified。若完整性在挑战脚本里，下一份要单独分类的是当轮 orchestrate，不把这份 Turnstile 结果当成已经解开。

## 2026-09-29 orchestrate classify

- 有头 `rt_20260929103550` 的 orchestrate 是 240267 字节，sha256 `06e1a7a4fea42ad35423c5535d4e76f331a50227fd901150174d0b3133849ab7`。live 目录那份是 237276 字节，sha256 `0bf4ecd1a8f809eb8efa42bb796cab6cd1aedbc15090bff2fd211387443ad684`。不是同一份。
- gate profile 仍是 `ast-safe`，同时有 `bytecode_container`、`dispatch_switch` 45、`function_constructor` 970。安全 AST 输出 373550 字节，`chain_accepted=true`，只是 transform-only。字符串表 changed=0，dispatcher 无变化。
- 变换后明文计数：`integrity` 0，`sha256` 0，`postMessage` 0，`Worker` 1，`Blob` 1，`createObjectURL` 1。这三个词在字符串表里，旁边有 `message`、`text/javascript`、`/api.js?onload=`。文件前部的 Check / JavaScript 是排障文案，不是完整性谓词。
- 谓词还看不见，所以不替换返回，也不在 Worker 边界插桩。不拆 opcode。
- 同一有头 run 的 eval 分区有 169 个文件、共 100321677 字节。75 个是 1337359 字节。这些文件里 `Worker`、`postMessage`、`createObjectURL`、`Blob`、`integrity`、`sha256`、`/fo/` 的子串总数都是 0，`atob` 一共 13。不能把这份 eval 分区当成 Worker 明文。摘要在 `diagnostics/live/headed-eval-summary.json`。

## 2026-09-29 flow compare hold

- 顺序停在完整性这一步：`api.js` 的可读谓词是 iframe 的 `reloadApiJsRequest`，不是第二份脚本的本地哈希。替换返回没有发生。明文插桩没有发生。
- 有头 trace 的子串扫描里，能对上阶段的是：第一次主站 `/fo/` 之前 1 次 Worker 提及；Turnstile 三次 `/fo/` 窗口里 51 条含 `postMessage` 的对象行；清关 `/fo/` 之前各 1 次 Worker 与 `postMessage`。这些行没有带上参数长度类。带长度类的字符串都在对不齐的行上，不放进 fo1/fo2/fo3。
- 本地 jsonl 里的 `postMessage` 是两条 `js-error`，名字 `Error`，消息长度 135，不是 Worker 明文。
- 脱敏对照在本轮 scratch 的 `flow-compare.json`。`serverAccepted` 仍是 false。
- 有头 orchestrate 字符串表里，Worker 的邻居是 `message`、`href`、`cRay`、`duration`；Blob 的邻居有 `/turnstile/v0/` 和 `DOMContentLoaded`；`createObjectURL` 的邻居有 `length` 和 `charAt`。四段邻域都没有 integrity / sha256 / digest。浏览器行和本地行都记 `secondScriptIntegrityCheck=absent`。替换和明文插桩仍是 not-done。
- 否定停点已接受：不执行这份字符串表，也不拆 opcode。第二份脚本的完整性谓词仍未标出。
- 本地行改成这次 `bridge-live.jsonl` 的实测：`/fo/` 子串 3623，长度类 18 条，没有按主站和 Turnstile 主机拆开。`forms` 与 `submits` 是 missing。不再把有头的 2 次和 3 次，或旧笔记里的 `forms=0`，写成这一行。

## 2026-09-30 live worker boundary

- 第二份脚本的完整性前提放下。不执行字符串表，不拆 opcode，不替换返回。观察留在当前 Firefox/RuyiDOM 会话。
- 顶层窗口两次真实请求都是：两个 blob Worker，构造参数键数 0，blob 尺寸类都小于 1 KB。第一个在第一次页面 `/fo/` open 之前，第二个在第一次 open 之后、第二次之前。`foSeen` 只数顶层 XHR，不含 iframe 里的 `/fo/`。
- 原型上的 `postMessage`、`onmessage`、`addEventListener('message')` 都是 0 次。实例上再包一层 `postMessage`，并自己挂 `message` 监听，父到 Worker、Worker 到父仍是 0。窗口消息来源只有 cf iframe，没有 blob。
- blob 脚本文本不落盘。只记固定词是否出现：第一份这些词都没有；第二份有 `postMessage` 和 `onmessage`，没有 `fetch`、`importScripts`、`WebSocket`、`/fo/`。
- 清关类仍是 `3488:u64:out0`，`forms` 0，`submits` 0，`chlOut` 无 form。widget 仍到 `interactiveEnd,complete`。形状在 `diagnostics/live/worker-live-shape.json`。
- 跨源 Turnstile iframe 里的 Worker 从页面钩子看不见。这次看到的是页面自己的两个 blob Worker。替换和明文插桩仍是 not-done。`serverAccepted` 仍是 false。

## 2026-09-30 worker and subtle probe

- 在真实 RuyiDOM 会话里插了两处边界。`crypto.subtle` 的 `encrypt`、`decrypt`、`sign`、`digest`、`importKey` 都挂上了，整轮调用数是 0。密文不走这五个 WebCrypto 方法。
- 第二个小于 1 KB 的 blob 在交给 Worker 之前同步读过，并前置了一段引导。引导发出 `boot`。随后自己的 `postMessage`、`onmessage`、`addEventListener('message')` 都没有被调用。原型上的 `postMessage` 不可配置，包不上。
- 第一份 blob 同步读到了，没有这些消息词，不注入。清关类仍是 `3488:u64:out0`，`forms` 0，`submits` 0。widget 仍到 `interactiveEnd,complete`。窗口消息仍只有 cf iframe。
- 没有记下密钥、明文或脚本正文。形状补在 `diagnostics/live/worker-live-shape.json` 的 `instrumentation`。`serverAccepted` 仍是 false。
