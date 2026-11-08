# 2026-10-22 iframe own descriptor

监听器接收者改完之后，这一拍只追踪一张新鲜页，没有第二处宿主改动。

页面先创建 iframe，再构造 SharedArrayBuffer。下一笔标准读取是该 iframe 元素自己的 `contentWindow` 属性描述符，结果是 undefined。紧接着是同一元素自己的 `contentDocument` 描述符，结果也是 undefined。`HTMLIFrameElement.prototype` 上这两个访问器都在。直接读取 `contentWindow` 能回到该 frame 的窗口，`contentDocument` 是这个窗口的文档。元素自身没有这两项描述符。

页面没有因此停住。它继续发出 challenge-fo，完成状态 200，体长类 `1000-4999`。第二个 blob Worker 启动且没有抛错。之后没有新的 undefined 读取，也没有 tick。求解器没有打印请求类。

这次新鲜页由 Node https 取得，只接受编排 HTTP 200 且 title length 16。回执是 `diagnostics/post-iframe-20261023/node-trace-receipt.json`。

- 23:56:01Z：页面 403 / 5726，title length 16，编排 200 / 250538，cookiePairs 1。12 秒切断，stdout 0，stderr 0。没有证书 document POST，没有读回。

challenge-fo 完成状态 200 不是 `serverAccepted`。本拍没有重跑官方 baseline，没有改写 Node `env.js`。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。事实哈希仍是 `3440737267cfafd35667c1c836d4425a49ed46b409c8486e7e82fcd2473f44a9`，3540 字节。`next` 没有 factWrites。盖章 `2026-10-22T23:57:26Z` 仍是 `authorize_form_construction_surface` / `blocked`。
