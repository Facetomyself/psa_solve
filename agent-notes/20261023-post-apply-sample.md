# 2026-10-23 post apply sample

这一拍要在第二次 blob Worker 返回之后，采样有界的 Reflect.apply 被调函数和它轮询的值。若点名一处宿主面，只补一处宿主行为。

两次新鲜页都没有启动第二个 blob Worker。采样没有发生，没有点名宿主面，没有改宿主。

challenge-fo 请求体长类 `1000-4999`，完成状态 200，响应体长类 `20000+`。求解 3500 毫秒和 3506 毫秒返回。请求类是 GET `orchestrate-script`、GET `other`、POST `challenge-fo`。三笔响应都是 200。同租约读回 HTTP 403，title length 16，pageKind challenge，体长类 `5000-19999`。没有证书 document POST。

回执是 `diagnostics/post-apply-20261023/node-trace-receipt.json`。

- 00:19:01Z：页面 403 / 5726，title length 16，编排 200 / 254839，cookiePairs 1。
- 00:20:13Z：页面 403 / 5726，title length 16，编排 200 / 257144，cookiePairs 1。

`solverReportedOk` 为 true，不是 `serverAccepted`。本拍没有重跑官方 baseline，没有改写 Node `env.js`。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。事实哈希仍是 `3440737267cfafd35667c1c836d4425a49ed46b409c8486e7e82fcd2473f44a9`，3540 字节。`next` 没有 factWrites。盖章 `2026-10-23T00:21:30Z` 仍是 `authorize_form_construction_surface` / `blocked`。
