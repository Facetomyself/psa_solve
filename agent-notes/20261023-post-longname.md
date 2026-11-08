# 2026-10-23 长名观察

这一拍只观察已发布的 runtime/run.js。没有改宿主，也没有改 VM、opcode、bytecode 或 WASM。
第二个 blob-worker.js 返回之前不包 document 方法，也不包 Reflect.apply。返回并记下页面 realm 之后才武装。

命名页 `node-postlongname-live-1`（03:30:02Z）。编排 200 / 255368，页面字节 5726，title length 16，cookie 文件 1 对。第二个 blob worker 已返回，bootReturns 2。进程在 18 秒被切断，wall 18008 毫秒。没有同租约读回。
固定宿主名单命中 0。证书构造路径上的调用都是 0，没有抛错，也没有不能提交的返回类。Reflect.apply 49000000 次。
被调名只按长度类计数：len1 25789601，len2 23210334，len3to8 38，len9plus 26。其他长名 64。不同调用身份 28。没有记下长度为 1 或 2 的函数名。错误名是空的。没有点名宿主行为。

challenge-fo 已完成且状态是 200。这不是证书 document POST，也不是 serverAccepted。证书 document POST 没有出现。

回执是 `diagnostics/post-longname-20261023/node-trace-receipt.json`。

完成事实没有写。run.js 的 ok 不是 serverAccepted。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。事实哈希仍是 `3440737267cfafd35667c1c836d4425a49ed46b409c8486e7e82fcd2473f44a9`，3540 字节。`next` 没有 factWrites。盖章 `2026-10-23T03:32:15Z` 仍是 `authorize_form_construction_surface` / `blocked`。
