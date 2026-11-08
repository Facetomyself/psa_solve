# 2026-10-22 XHR 字符串 Content-Type

`challenge-fo` 返回 HTTP 400，`HTMLFormElement.submit` 仍没有发出证书 document POST。改前一发新鲜会话的请求头分类：POST `challenge-fo` 已带 `cf-chl` 和 `cf-chl-ra`，还有 cookie、referer、user-agent。正文长度 2252。`Content-Type`、`Origin`、`sec-fetch-*` 都不在。响应 400，正文 121 字节，content-type 类 `application/json`，响应头名含 `cf-chl-out`。form submit 调用次数是 0，`ebCall` 是 0。

这一处只改 Node `transport.js`：`XMLHttpRequest.send` 收到字符串且调用方没有设置 `Content-Type` 时，补上 `text/plain;charset=UTF-8`。已有的 Content-Type 保持不动。`send(null)` 不补。没有改写 Node `env.js`，没有改 helper，没有改编排脚本，没有新的官方 baseline。

本地断言走已装载的 `transport.js`，结果 `CTYPE_DEFAULT_OK`。未设置时发出的类型是 `text/plain;charset=UTF-8`；调用方已设 `application/json` 时保持；`send(null)` 不带 Content-Type。

两次新鲜 `runtime/run.js`：

- 17:37:08Z：页面 403 / 5662，编排 200 / 253117，cookiePairs 1，exit 0，elapsedMs 3507，stderr 0。POST `challenge-fo` 体长类 `1000-4999`，响应 400 / `1-999`。另有 POST `challenge-platform` 体长类 `0`。证书 document POST 没有出现。读回 403，titleLen 16，pageKind challenge，bodyLengthClass `5000-19999`。errorStages 空。`ebCall` 0。`solverReportedOk` true。
- 17:37:18Z：页面 403 / 5683，编排 200 / 252211，cookiePairs 1，exit 0，elapsedMs 3505，stderr 0。请求类、响应类和读回与上一发相同。`ebCall` 0。

有头 oracle 是 clearance 交换之后的证书 document POST，status 200。这两发的 `challenge-fo` 仍是 400，没有证书 document POST，方法、URL 类、状态和体长类不对齐。补上的 Content-Type 没有让这一跳离开 400。

本拍没有重跑官方 baseline。上一发绑定的 baseline 仍是 `7e39848290c24e83867be54eb6ed8fca`。

`solverReportedOk` 不是 `serverAccepted`。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。`next` 没有 factWrites。盖章 `2026-10-22T17:39:54Z` 仍是 `authorize_form_construction_surface` / `blocked`。
