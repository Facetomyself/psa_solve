# 2026-10-22 form construction Node receipt

授权面是 `Document.createElement` 到 `HTMLFormElement.submit`。没有改写 Node `env.js`。没有改 helper，没有新的官方 baseline，没有改 `document-principal.js`，没有改编排脚本。

`runtime/lib/host-globals.js` 的 DOM 类增加 `HTMLFormElement`。`runtime/lib/host-dom.js` 把 `form` 映射到该构造器。`setAttribute` 反映 `name`、`value`、`type`、`action`、`method`。`HTMLFormElement.prototype.submit` 在调用时读取已有的 `XMLHttpRequest`。method 只有显式 POST 才发 POST，默认是 GET。POST 的 `Content-Type` 是 `application/x-www-form-urlencoded`。

本地断言加载真实 `runtime/code.js`，`CF_CAPTURE_ONLY=1`，不发网络。结果 `FORM_SURFACE_OK`：`createElement("form")` 的构造器名是 `HTMLFormElement`，`form.submit` 就是原型上的 `submit`，命名 input 进入 `elements` 和 POST 体，URL 类是 `cert-document`。`createElement("div")` 是 `HTMLDivElement`，没有 `submit`。未设 method 的表单记录为 GET。

两次新鲜 `runtime/run.js`，各自抓取一页挑战和编排脚本：

| | session 1 | session 2 |
| --- | --- | --- |
| started | 2026-10-22T16:35:29.687911Z | 2026-10-22T16:36:29.287873Z |
| page | 403, 5683 bytes | 403, 5662 bytes |
| orchestrate | 200, 254565 bytes | 200, 255148 bytes |
| exitCode | 0 | 0 |
| certDocumentPost | false | false |
| requestClasses | empty | empty |
| responseClasses | empty | empty |
| readback | 403, titleLen 16, challenge, 5000-19999 | 403, titleLen 16, challenge, 5000-19999 |
| errorStages | orchestrate, async | orchestrate, async |
| solverReportedOk | true | true |

两次一致。有头 oracle 先有 clearance 交换，然后是证书 document POST，方法 POST，状态 200。Node 没有这些请求类，方法、URL 类、状态和体长类都不对齐。

`solverReportedOk` 不是 `serverAccepted`。没有证书 document POST，也没有同租约 HTTP 200 回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 仍是 null。

回执：`diagnostics/form-construction-20261022/node-rerun-receipt.json`。

`next` 盖章 `2026-10-22T16:38:59Z`，action 仍是 `authorize_form_construction_surface`，turnGate 仍是 `blocked`。facts 哈希没有变，没有 factWrites。
