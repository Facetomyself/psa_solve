# 2026-10-22 event target

`document.currentScript` 已经返回 null。新鲜页仍把 challenge-fo 送到完成状态 200。页面接着给 document 注册 keydown、pointermove、pointerover、touchstart、mousemove、wheel 和 click，给 window 注册 error 和 message。第二个 blob Worker 启动且 onmessage 为函数之后，window 再注册 unhandledrejection 和 error。这些 `addEventListener` 原来是空函数，监听器被丢掉。没有 postMessage，也没有 element.click。事件循环随后停住。

这一处只改 Node `host-globals.js` 和 `host-dom.js`：window 与 document 共用按 `this` 分桶的 `addEventListener`、`removeEventListener` 和 `dispatchEvent`。`dispatchEvent` 调用该目标上的监听器。`createElement` 和 `HTMLFormElement.submit` 没有改。没有改写 Node `env.js`，没有改 helper，没有新的官方 baseline。

本地断言 `EVENT_TARGET_OK`。`CURRENT_SCRIPT_OK`、`WORKER_OK`、`GPU_OK`、`FONTS_OK`、`EFP_OK`、`IFRAME_DOC_TREE_OK`、`IFRAME_FUNCTION_OK`、`SCRIPT_SRC_OK`、`FORM_MARKUP_OK` 仍通过。

一次新的新鲜页由 Node https 取得，只接受编排 HTTP 200 且 title length 16。回执是 `diagnostics/event-target-20261023/node-rerun-receipt.json`。

- 23:04:06Z：页面 403 / 5726，title length 16，编排 200 / 251402，cookiePairs 1。22 秒切断，stdout 0，stderr 0，errorStages 只有 timeout。求解器没有打印请求类，没有证书 document POST，没有读回。

改前同一条新鲜路径上 challenge-fo 完成状态 200、体长类 `1000-4999` 不是 `serverAccepted`。本拍没有重跑官方 baseline。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。事实哈希仍是 `3440737267cfafd35667c1c836d4425a49ed46b409c8486e7e82fcd2473f44a9`，3540 字节。`next` 没有 factWrites。盖章 `2026-10-22T23:05:21Z` 仍是 `authorize_form_construction_surface` / `blocked`。
