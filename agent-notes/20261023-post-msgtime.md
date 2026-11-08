# 2026-10-23 message timing

这一拍只观察已发布的 runtime/run.js。没有改宿主，没有改 VM、opcode、bytecode 或 WASM。

页面 `node-postmsgtime-live-1`（02:28:11Z）。编排 200 / 256856，页面字节 5726，title length 16，cookie 文件 2 对。进程在 18 秒被切断，wall 18008 毫秒，没有同租约读回。第二次 blob worker 正常返回。随后页面 realm 的 Reflect.apply 大约 6600 万次，热函数里没有这些整词：createElement、submit、innerHTML、HTMLFormElement、postMessage、document。

challenge-fo 的 POST 在约 1001 毫秒完成且状态 200。这不是证书 document POST。证书 document POST 没有出现。

第二个 worker 在返回前把 onmessage 设过一次，flush 时队列是空的。父页 postMessage 是 0，worker 侧 postMessage 也是 0。同步送达、入队、不可克隆参数都是 0。没有消息被发出，所以消息任务时序不是这次观察到的出口。

createElement 49 和 innerHTML 6 都发生在第一个 worker 启动之前。form 是 0，submit 是 0。innerHTML 没有造出 form，也没有人调用 HTMLFormElement.submit。这一页没有表明表单构造面挡住了证书 document POST。没有点名宿主行为。

回执是 `diagnostics/post-msgtime-20261023/node-trace-receipt.json`。

完成事实没有写。run.js 的 ok 不是 serverAccepted。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。事实哈希仍是 `3440737267cfafd35667c1c836d4425a49ed46b409c8486e7e82fcd2473f44a9`，3540 字节。`next` 没有 factWrites。盖章 `2026-10-23T02:31:44Z` 仍是 `authorize_form_construction_surface` / `blocked`。
