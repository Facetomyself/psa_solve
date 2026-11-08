# 2026-10-22 currentScript

已装上的 blob Worker 把第二个 blob 跑起来，没有抛错，也没有父页 postMessage。随后页面监听 unhandledrejection 和 error。challenge-fo 发出之后、完成状态 200 之前，页面在回调轮次读了一次 `document.currentScript`。这个属性当时不存在，读到的是 undefined。没有脚本在执行时，浏览器返回 null。

这一处只改 Node `host-dom.js`：页面文档的 `currentScript` 是数据属性 null。iframe 文档继承 null。脚本 src 的 onload 仍会在执行期间改写并恢复。`createElement` 和 `HTMLFormElement.submit` 没有改。没有改写 Node `env.js`，没有改 helper，没有新的官方 baseline。

本地断言 `CURRENT_SCRIPT_OK`。`WORKER_OK`、`GPU_OK`、`FONTS_OK`、`IFRAME_DOC_TREE_OK`、`IFRAME_FUNCTION_OK`、`SCRIPT_SRC_OK`、`FORM_MARKUP_OK` 仍通过。

一次新的新鲜页由 Node https 取得，只接受编排 HTTP 200 且 title length 16。回执是 `diagnostics/current-script-20261023/node-rerun-receipt.json`。

- 22:41:20Z：页面 403 / 5726，title length 16，编排 200 / 257258，cookiePairs 1。22 秒切断，stdout 0，stderr 0，errorStages 只有 timeout。求解器没有打印请求类，没有证书 document POST，没有读回。

改前同一条新鲜路径上 challenge-fo 完成状态 200、体长类 `1000-4999` 不是 `serverAccepted`。本拍没有重跑官方 baseline。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。事实哈希仍是 `3440737267cfafd35667c1c836d4425a49ed46b409c8486e7e82fcd2473f44a9`，3540 字节。`next` 没有 factWrites。盖章 `2026-10-22T22:45:37Z` 仍是 `authorize_form_construction_surface` / `blocked`。
