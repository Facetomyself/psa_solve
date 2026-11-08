# 2026-10-23 post second worker

这一拍只追踪第二次 blob Worker 返回之后的挂起，没有改宿主。

命名页在第二次启动返回之后才装上观察。更早一次在页面代码之前替换了 Reflect.apply，没有进入第二个 Worker，不用它点名。

challenge-fo 完成状态 200，体长类 `1000-4999`。第二个 blob Worker 启动且没有抛错，worker 作用域的 onmessage 是函数。页面接着给 window 注册 unhandledrejection 和 error，这两次 addEventListener 落到现有监听桶。然后页面进入同步内部 Reflect.apply 循环，计次走过 1、1000、100000。没有标准宿主函数名，也没有标准名的 undefined 读取或缺失描述符。没有父页 postMessage，没有给该实例赋值 onmessage，没有创建 form，第二次启动之后没有 tick。

这次新鲜页由 Node https 取得，只接受编排 HTTP 200 且 title length 16。回执是 `diagnostics/post-worker2-20261023/node-trace-receipt.json`。

- 00:08:38Z：页面 403 / 5726，title length 16，编排 200 / 255063，cookiePairs 1。20 秒切断，stdout 0，stderr 0。没有证书 document POST，没有读回。

challenge-fo 完成状态 200 不是 `serverAccepted`。本拍没有重跑官方 baseline，没有改写 Node `env.js`。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。事实哈希仍是 `3440737267cfafd35667c1c836d4425a49ed46b409c8486e7e82fcd2473f44a9`，3540 字节。`next` 没有 factWrites。盖章 `2026-10-23T00:11:03Z` 仍是 `authorize_form_construction_surface` / `blocked`。
