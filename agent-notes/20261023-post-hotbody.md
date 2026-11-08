# 2026-10-23 热调用参数

这一拍只观察已发布的 runtime/run.js。没有改宿主，也没有改 VM、opcode、bytecode 或 WASM。
第二个 blob-worker.js 返回之前不包 document 方法，也不包 Reflect.apply。返回之后才武装。

命名页 `node-posthotbody-live-1`（05:03:18Z）。编排 200 / 255755，页面字节 5726，title length 16，cookie 文件 2 对。第二个 blob worker 已返回，bootReturns 2。进程在 18 秒被切断，wall 18076 毫秒，exit 1。没有同租约读回。求解 stdout 未解析。
三条热调用都是非原生脚本，接收者 undefined，返回 number，未抛。hot1 28505031 次，份额 ge50，三个参数都是 number。hot2 11397948 次，份额 p10to50，参数个数众数 1，第一参 number。hot3 5698965 次，份额 p1to10，三个参数都是 number。
三条都没有字符串参数，没有对象原型桶，源码里的宿主令牌为否，彼此没有互调。form.submit、createElement、createElementNS 的身份计数都是 0。Reflect.apply 57000000 次。bound 前缀跳过 57 次。没有点名宿主行为。

challenge-fo 已完成且状态是 200。这不是证书 document POST，也不是 serverAccepted。证书 document POST 没有出现。

回执是 `diagnostics/post-hotbody-20261023/node-trace-receipt.json`。

完成事实没有写。run.js 的 ok 不是 serverAccepted。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。事实哈希仍是 `3440737267cfafd35667c1c836d4425a49ed46b409c8486e7e82fcd2473f44a9`，3540 字节。`next` 没有 factWrites。盖章 `2026-10-23T05:07:56Z` 仍是 `authorize_form_construction_surface` / `blocked`。
