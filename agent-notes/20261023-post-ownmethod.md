# 2026-10-23 实例自身方法

这一拍只观察已发布的 runtime/run.js。没有改宿主文件，没有改 VM、opcode、bytecode 或 WASM。
提前包装 createElement 的三页没有让第二个 blob worker 返回，不作为命名页。
命名页只在第二个 blob-worker.js 返回之后才走元素树、包上实例自己的 setAttribute / appendChild，并武装 Reflect.apply。

页面 `node-postownmethod-live-4`（03:06:51Z）。编排 200 / 258247，页面字节 5726，title length 16，cookie 文件 2 对。进程在 18 秒被切断，wall 18008 毫秒。没有同租约读回。
第二个 blob worker 已经返回。武装时已观察元素 34，自身方法快照 68。武装窗口里 setAttribute、appendChild、createElement、createElementNS、submit 都是 0。Reflect.apply 约 53000000 次。
被调名只按长度类计数：len1 36440704，len2 16559221，len3to8 72，len9plus 2。其他长名 74。不同调用身份 18。没有记下长度为 1 或 2 的函数名。错误名是空的。没有点名宿主行为。

challenge-fo 已完成且状态是 200。这不是证书 document POST，也不是 serverAccepted。证书 document POST 没有出现。

回执是 `diagnostics/post-ownmethod-20261023/node-trace-receipt.json`。

合同元数据的 currentHead 已对齐当前 HEAD，revision 10，caseClass 仍是 challenge。完成事实没有写。run.js 的 ok 不是 serverAccepted。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。事实哈希仍是 `3440737267cfafd35667c1c836d4425a49ed46b409c8486e7e82fcd2473f44a9`，3540 字节。`next` 没有 factWrites。盖章 `2026-10-23T03:11:47Z` 仍是 `authorize_form_construction_surface` / `blocked`。
