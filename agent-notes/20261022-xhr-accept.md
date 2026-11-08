# 2026-10-22 XHR Accept

上一拍补上文档 Origin 和 sec-fetch-dest/mode/site 之后，`challenge-fo` 仍是 HTTP 400。改前探针里这条 POST 的方法是 POST，体长类 `1000-4999`，状态 400，响应体长类 `1-999`，响应 content-type 类 `application/json`。请求头名是 `cf-chl`、`cf-chl-ra`、`content-type`、`cookie`、`origin`、`referer`、`sec-fetch-dest`、`sec-fetch-mode`、`sec-fetch-site`、`user-agent`。`content-type` 是 `text/plain` 且带 charset。`Accept` 不在头名里。form submit 调用 0。

有头 oracle 的首页 FO 也是 POST，体长类同样是 `1000-4999`，但状态是 200。它的头名比这条多了 `accept`（值类 `*/*`）、`accept-language`、`accept-encoding`，以及协议层的 `alt-used`、`te`、`connection`、`content-length`、`host`。剩下仍可能挡住 400 的 XHR 默认头名是 `accept`。这一拍不补 `accept-encoding`、`accept-language`，也不在 HTTP/1.1 上伪造 `alt-used` 或 `te`。

这一处只改 Node `transport.js` 的同一次 `XMLHttpRequest.send`：调用方没设 `Accept` 时补上 `*/*`。调用方已设的 `Accept` 保持不动。`send(null)` 也补，但不因此补 Content-Type。没有改写 Node `env.js`，没有改 helper，没有改编排脚本，没有新的官方 baseline。

本地断言走已装载的 `transport.js`，结果 `ACCEPT_DEFAULT_OK`。未设时的 `Accept` 是 `*/*`，请求头里没有 `accept-encoding` 和 `accept-language`，Content-Type、Origin、sec-fetch 仍在。调用方预设的 `Accept` 保持。`send(null)` 有 `Accept`，没有 Content-Type。已有的 `ORIGIN_SECFETCH_OK` 和 `CTYPE_DEFAULT_OK` 仍通过。

两次新鲜 `runtime/run.js`：

- 17:53:51Z：页面 403 / 5662，编排 200 / 249755，cookiePairs 1，exit 0，elapsedMs 3502，stderr 0。POST `challenge-fo` 体长类 `1000-4999`，响应 400 / `1-999`。另有 POST `challenge-platform` 体长类 `0`。证书 document POST 没有出现。读回 403，titleLen 16，pageKind challenge，bodyLengthClass `5000-19999`。errorStages 空。`ebCall` 0。`solverReportedOk` true。
- 17:54:01Z：页面 403 / 5683，编排 200 / 253079，cookiePairs 1，exit 0，elapsedMs 3510，stderr 0。请求类、响应类和读回与上一发相同。`ebCall` 0。

`challenge-fo` 没有离开 HTTP 400。有头 oracle 是 clearance 交换之后的证书 document POST，status 200。这两发没有证书 document POST，同租约读回不是 HTTP 200。方法、URL 类、状态和体长类不对齐。

本拍没有重跑官方 baseline。上一发绑定的 baseline 仍是 `7e39848290c24e83867be54eb6ed8fca`。

`solverReportedOk` 不是 `serverAccepted`。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。`next` 没有 factWrites。盖章 `2026-10-22T17:55:50Z` 仍是 `authorize_form_construction_surface` / `blocked`。
