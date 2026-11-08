# 2026-10-23 bound 后缀

这一拍只观察已发布的 runtime/run.js。没有改宿主，也没有改 VM、opcode、bytecode 或 WASM。
第二个 blob-worker.js 返回之前不包 document 方法，也不包 Reflect.apply。返回并记下页面 realm 之后才武装。

命名页 `node-postbound-live-1`（04:23:42Z）。编排 200 / 251521，页面字节 5726，title length 16，cookie 文件 1 对。第二个 blob worker 已返回，bootReturns 2。进程在 18 秒被切断，wall 18008 毫秒。没有同租约读回。
bound 调用 48 次。后缀都是 call，没有抛错：number 5，string 1，object 42。非宿主后缀 0。多层 bound 0。
form.submit、createElement、createElementNS 的身份计数都是 0。Reflect.apply 57000000 次。没有点名宿主行为。

challenge-fo 已完成且状态是 200。这不是证书 document POST，也不是 serverAccepted。证书 document POST 没有出现。

回执是 `diagnostics/post-bound-20261023/node-trace-receipt.json`。

完成事实没有写。run.js 的 ok 不是 serverAccepted。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。事实哈希仍是 `3440737267cfafd35667c1c836d4425a49ed46b409c8486e7e82fcd2473f44a9`，3540 字节。`next` 没有 factWrites。盖章 `2026-10-23T04:25:09Z` 仍是 `authorize_form_construction_surface` / `blocked`。
