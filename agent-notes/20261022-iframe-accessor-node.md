# 2026-10-22 iframe 访问器

求解没有走到 `HTMLFormElement.submit`，是因为新鲜编排在 iframe 上做 `Reflect.getOwnPropertyDescriptor(iframe, "contentWindow")`。`host-dom.js` 原先给每个元素定义了自有访问器，描述符不是 `undefined`，脚本抛出空 `TypeError`（新鲜编排第 2 行第 3577 列）。这不是绑定脚本第 3 行第 544 列。

这一处只改 Node `host-dom.js`：`contentWindow` / `contentDocument` 改到 `HTMLIFrameElement.prototype`，同一个 iframe 共用一个子窗口和子文档，`defaultView`、`frameElement`、`document` 互指，子窗口带上普通构造器。没有改写 Node `env.js`，没有改 helper，没有改编排脚本。

本地 `runtime/code.js` 断言 `FRAME_SURFACE_OK`。同一份已保存编排的同步抛错离开第 3577 列，`vm.runInContext` 同步段跑完。

两次新鲜 `runtime/run.js`：

- 17:17:46Z：页面 403 / 5683，编排 200 / 253392，cookiePairs 1，exit 0，elapsedMs 3505，stderr 0。POST `challenge-fo` 体长类 `1000-4999`，响应 400 / `1-999`。另有 POST `challenge-platform` 体长类 `0`。证书 document POST 没有出现。读回 403，titleLen 16，pageKind challenge，bodyLengthClass `5000-19999`。errorStages 空。`solverReportedOk` true。
- 17:17:59Z：页面 403 / 5683，编排 200 / 262118，cookiePairs 1，exit 0，elapsedMs 3506，stderr 0。请求类、响应类和读回与上一发相同。

有头 oracle 是 clearance 交换之后的证书 document POST，status 200。这两发的 `challenge-fo` 是 400，没有证书 document POST，方法、URL 类、状态和体长类不对齐。

官方 baseline `7e39848290c24e83867be54eb6ed8fca`：pid 44212，exitCode 1，timedOut false，elapsed 25126073500 ns，failure `execution did not complete successfully`。诊断仍是源文件内第 3 行第 544 列，kind `other`，class `slow-script`，sourceForm `token`，sourceClass `other`。raw sha256 `3279db9672ab9473b7db77fa43888d05254a826d908eaa41bef9722573665bee`，side sha256 `00eaba2f96231c937406f8f1c9856de2b5c66a84721e0ec21c5c6cb99a1f7464`，与 `a5c33751e7a24338bd7dc2959c349599` 相同。Node 改动没有移动这个 Gecko 停点。

`solverReportedOk` 不是 `serverAccepted`。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。`next` 没有 factWrites。盖章 `2026-10-22T17:21:14Z` 仍是 `authorize_form_construction_surface` / `blocked`。
