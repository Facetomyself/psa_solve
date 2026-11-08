# 2026-10-23 after worker inbound delivery

这一拍在 Worker 入站排队之后，用一页新的 `runtime/run.js` 看父页为什么还是到不了证书 document POST。没有再改宿主。

01:24:59Z 和 01:26:05Z 两页没有启动第二个 Worker。求解分别在 3503 毫秒和 3504 毫秒返回。01:26:05Z 的 challenge-fo 响应体长类是 `20000+`，同租约读回 403。没有证书 document POST。不用它们点名。

主页是 01:21:04Z。第二个 Worker 把 onmessage 设成函数，postMessage、定时器和 Atomics 都是 0，没有抛错。随后父页停在一次内部调用里。父页 postMessage、createElement、form、submit 都是 0。16 秒切断时 stdout 0，stderr 0。

宿主调用抽样页是 01:26:21Z。第二个 Worker 同样返回。超时窗口里 Reflect.apply 约 4000 万次，和直接调用计数相同。热路径没有长宿主名。唯一的长 native 名只有 54 次。createElement、form、submit 和父页 postMessage 仍是 0。12 秒切断时 stdout 0，stderr 0。

因此没有点名一处能发出证书 document POST 的宿主行为。入站队列没有被这条派发调用。表单 submit 也没有被调用。

回执是 `diagnostics/post-inbound-20261023/node-trace-receipt.json`。

本拍没有重跑官方 baseline，没有改写 Node `env.js`。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。事实哈希仍是 `3440737267cfafd35667c1c836d4425a49ed46b409c8486e7e82fcd2473f44a9`，3540 字节。`next` 没有 factWrites。盖章 `2026-10-23T01:27:25Z` 仍是 `authorize_form_construction_surface` / `blocked`。
