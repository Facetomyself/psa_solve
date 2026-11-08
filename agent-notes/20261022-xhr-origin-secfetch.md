# 2026-10-22 XHR Origin 与 sec-fetch

上一拍补上 `text/plain;charset=UTF-8` 之后，`challenge-fo` 仍是 HTTP 400。改前探针里这条 POST 没有 `Origin`，也没有 `sec-fetch-*`。

这一处只改 Node `transport.js` 的同一次 `XMLHttpRequest.send`：调用方没设时补上 `Origin`（文档 origin），以及 `Sec-Fetch-Dest: empty`、`Sec-Fetch-Mode: cors`、`Sec-Fetch-Site`（同源 `same-origin`，同站 `same-site`，否则 `cross-site`）。调用方已设的头保持不动。没有改写 Node `env.js`，没有改 helper，没有改编排脚本，没有新的官方 baseline。

本地断言走已装载的 `transport.js`，结果 `ORIGIN_SECFETCH_OK`。同源字符串 POST 带文档 origin、`empty` / `cors` / `same-origin`，并仍是 `text/plain;charset=UTF-8`。调用方预设的 `Origin` 和 `Sec-Fetch-Site` 保持。跨站请求的 site 是 `cross-site`，origin 仍是文档 origin。同站主机的 site 是 `same-site`。已有的字符串 Content-Type 断言 `CTYPE_DEFAULT_OK` 仍通过。

两次新鲜 `runtime/run.js`：

- 17:45:17Z：页面 403 / 5683，编排 200 / 254747，cookiePairs 1，exit 0，elapsedMs 3502，stderr 0。POST `challenge-fo` 体长类 `1000-4999`，响应 400 / `1-999`。另有 POST `challenge-platform` 体长类 `0`。证书 document POST 没有出现。读回 403，titleLen 16，pageKind challenge，bodyLengthClass `5000-19999`。errorStages 空。`ebCall` 0。`solverReportedOk` true。
- 17:45:28Z：页面 403 / 5683，编排 200 / 253189，cookiePairs 1，exit 0，elapsedMs 3503，stderr 0。请求类、响应类和读回与上一发相同。`ebCall` 0。

`challenge-fo` 没有离开 HTTP 400。有头 oracle 是 clearance 交换之后的证书 document POST，status 200。这两发没有证书 document POST，同租约读回不是 HTTP 200。方法、URL 类、状态和体长类不对齐。

本拍没有重跑官方 baseline。上一发绑定的 baseline 仍是 `7e39848290c24e83867be54eb6ed8fca`。

`solverReportedOk` 不是 `serverAccepted`。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。`next` 没有 factWrites。盖章 `2026-10-22T17:46:08Z` 仍是 `authorize_form_construction_surface` / `blocked`。
