# 2026-10-23 内建身份

这一拍只观察已发布的 runtime/run.js。没有改宿主，也没有改 VM、opcode、bytecode 或 WASM。
第二个 blob-worker.js 返回之前不包 document 方法，也不包 Reflect.apply。返回并记下页面 realm 之后才武装。

`node-postintrinsic-live-1` 不能点名。当时的身份表没有对上任何调用，nativeUnmatched 35，len9plus 35。
命名页是 `node-postintrinsic-live-2`（04:04:05Z）。编排 200 / 255317，页面字节 5726，title length 16，cookie 文件 1 对。第二个 blob worker 已返回，bootReturns 2。mapSize 256。进程在 18 秒被切断，wall 18009 毫秒。没有同租约读回。
表内命中只有 isArray 46 次，返回都是 boolean，没有抛错。bound 后缀不在表内的调用 77 次，后缀没有保存。nativeUnmatched 与 scriptUnmatched 都是 0。
Reflect.apply 69000000 次。长度类 len1 50999699，len2 18000174，len3to8 46，len9plus 77。没有记下长度为 1 或 2 的函数名。错误名是空的。可点名的内建没有失败。没有点名宿主行为。

challenge-fo 已完成且状态是 200。这不是证书 document POST，也不是 serverAccepted。证书 document POST 没有出现。

回执是 `diagnostics/post-intrinsic-20261023/node-trace-receipt.json`。

完成事实没有写。run.js 的 ok 不是 serverAccepted。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。事实哈希仍是 `3440737267cfafd35667c1c836d4425a49ed46b409c8486e7e82fcd2473f44a9`，3540 字节。`next` 没有 factWrites。盖章 `2026-10-23T04:05:56Z` 仍是 `authorize_form_construction_surface` / `blocked`。
