# 2026-10-23 深度 0 的直接子调用

这一拍只观察已发布的 runtime/run.js。没有改宿主，也没有改 VM、opcode、bytecode 或 WASM。
第二个 blob-worker.js 返回之后才转发 Reflect.apply。深度 0 的身份计数和它的直接子计数都发生在调用返回之前。

命名页 `node-postd0child-live-1`（06:29:28Z）。编排 200 / 251477，页面字节 5726，title length 16，cookie 文件 2 对。第二个 blob worker 已返回，bootReturns 2。进程在 18 秒被切断，wall 18083 毫秒，exit 1。没有同租约读回。求解 stdout 未解析。
challenge-fo 在武装时已经是 200。这不是证书 document POST，也不是 serverAccepted。
Reflect.apply 34000000 次。深度 0 进入 55 次，返回 54 次。深度 1 进入 236 次。深度 2 及以上 33999709 次。
最热深度 0 一行 28 次，份额 ge50，非原生，元数 3plus，名字长度类 len1，接收者 undefined，首参 number，参数个数 3plus，返回 number 且稳定，未抛。它与 form.submit、createElement、createElementNS、requestSubmit、setAttribute、getAttribute、appendChild、Date.now、performance.now、setTimeout、postMessage 都不是同一函数。源码宿主记号全否。
该被调的直接子表是 0 行，溢出 0。没有子被调。form.submit、createElement、createElementNS 的身份计数都是 0。没有点名宿主读取。

证书 document POST 没有出现。

回执是 `diagnostics/post-d0child-20261023/node-trace-receipt.json`。

完成事实没有写。run.js 的 ok 不是 serverAccepted。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。事实哈希仍是 `3440737267cfafd35667c1c836d4425a49ed46b409c8486e7e82fcd2473f44a9`，3540 字节。`next` 没有 factWrites。盖章 `2026-10-23T06:33:13Z` 仍是 `authorize_form_construction_surface` / `blocked`。
