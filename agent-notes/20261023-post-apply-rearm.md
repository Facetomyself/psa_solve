# 2026-10-23 apply sample after second worker

这一拍只在第二次 blob Worker 实际返回之后装上有界 Reflect.apply 采样。没有改宿主。

该 Worker 启动且没有抛错。采样看到 8 个不同被调函数，计次走过 1、1000、100000。它们都不是宿主 API，也不是 native。最热的是非宿主数值函数，this 为 undefined，参数和返回值都是数。10 万次调用里唯一的宿主调用是一次已有的 `Date.now`。这没有点名一处缺失的宿主面。

这次新鲜页由 Node https 取得，只接受编排 HTTP 200 且 title length 16。回执是 `diagnostics/post-apply-rearm-20261023/node-trace-receipt.json`。

- 00:25:16Z：页面 403 / 5726，title length 16，编排 200 / 250258，cookiePairs 1。20 秒切断，stdout 0，stderr 0。没有证书 document POST，没有读回。

本拍没有重跑官方 baseline，没有改写 Node `env.js`。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。事实哈希仍是 `3440737267cfafd35667c1c836d4425a49ed46b409c8486e7e82fcd2473f44a9`，3540 字节。`next` 没有 factWrites。盖章 `2026-10-23T00:26:33Z` 仍是 `authorize_form_construction_surface` / `blocked`。
