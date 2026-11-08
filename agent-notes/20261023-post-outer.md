# 2026-10-23 外层轮询

这一拍只观察已发布的 runtime/run.js。没有改宿主，也没有改 VM、opcode、bytecode 或 WASM。
第二个 blob-worker.js 返回之后才包 Reflect.apply，并按进入前的深度计数。轮询也在这次武装时包到页面全局上，原样转发。run.js 在求解返回之后的轮询不计入宿主读取。

命名页 `node-postouter-live-1`（05:25:57Z）。编排 200 / 254157，页面字节 5726，title length 16，cookie 文件 2 对。第二个 blob worker 已返回，bootReturns 2。进程在 18 秒被切断，wall 18081 毫秒，exit 1。没有同租约读回。求解 stdout 未解析。
challenge-fo 在武装时已经是 200。这不是证书 document POST，也不是 serverAccepted。
Reflect.apply 75000000 次。深度 d0 155 次，返回 154 次，有一次未返回。d1 9 次。更深一档 74999836 次。
Date.now、performance.now、setTimeout、setInterval、requestAnimationFrame、queueMicrotask、postMessage、Atomics.wait、Atomics.waitAsync 在 d0、d1 和更深一档都是 0，没有抛错。调用者函数对象没有取到。
form.submit、createElement、createElementNS 的身份计数都是 0。没有点名宿主读取。

证书 document POST 没有出现。

回执是 `diagnostics/post-outer-20261023/node-trace-receipt.json`。

完成事实没有写。run.js 的 ok 不是 serverAccepted。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。事实哈希仍是 `3440737267cfafd35667c1c836d4425a49ed46b409c8486e7e82fcd2473f44a9`，3540 字节。`next` 没有 factWrites。盖章 `2026-10-23T05:29:08Z` 仍是 `authorize_form_construction_surface` / `blocked`。
