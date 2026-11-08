# 2026-10-22 XHR Accept-Language

上一拍补上 `Accept: */*` 之后，`challenge-fo` 仍是 HTTP 400。有头首页 FO 是 POST，状态 200，体长类 `1000-4999`，`Accept-Language` 是两段：主语言没有 q，基础语言是 `q=0.9`，逗号后没有空格。宿主 `navigator.language` 已是 `en-US`，`languages` 只有这一项。当时的请求没有这个头。

这一处只改 Node `transport.js` 的同一次 `XMLHttpRequest.send`：调用方没设 `Accept-Language` 时，用 `navigator.languages`，否则用 `navigator.language`。只有一个带地区的主语言时，再补它的基础语言，质量 `q=0.9`。调用方已设的头保持不动。没有补 `accept-encoding`，没有伪造 `alt-used` 或 `te`。没有改写 Node `env.js`，没有改 helper，没有改编排脚本，没有新的官方 baseline。

本地断言走已装载的 `host-globals.js` 和 `transport.js`，结果 `LANG_DEFAULT_OK`。发出的值是 `en-US,en;q=0.9`。调用方预设的语言头保持。`send(null)` 也带这个头，并且仍不带 Content-Type。已有的 `ACCEPT_DEFAULT_OK`、`ORIGIN_SECFETCH_OK`、`CTYPE_DEFAULT_OK` 仍通过。

两次新鲜 `runtime/run.js`：

- 18:03:30Z：页面 403 / 5662，编排 200 / 251659，cookiePairs 1，exit 0，elapsedMs 3508，stderr 0。POST `challenge-fo` 体长类 `1000-4999`，响应 400 / `1-999`。另有 POST `challenge-platform` 体长类 `0`。证书 document POST 没有出现。读回 403，titleLen 16，pageKind challenge，bodyLengthClass `5000-19999`。errorStages 空。`ebCall` 0。`solverReportedOk` true。
- 18:04:07Z：页面 403 / 5683，编排 200 / 252211，cookiePairs 1，exit 0，elapsedMs 3506，stderr 0。请求类、响应类和读回与上一发相同。`ebCall` 0。

方法、URL 类和体长类与有头首页 FO 同级，状态不是 200。`challenge-fo` 没有离开 HTTP 400。有头 oracle 在 clearance 交换之后还有证书 document POST，status 200。这两发没有证书 document POST，同租约读回不是 HTTP 200。

本拍没有重跑官方 baseline。上一发绑定的 baseline 仍是 `7e39848290c24e83867be54eb6ed8fca`。

`solverReportedOk` 不是 `serverAccepted`。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。`next` 没有 factWrites。盖章 `2026-10-22T18:04:50Z` 仍是 `authorize_form_construction_surface` / `blocked`。
