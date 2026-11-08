# 2026-10-22 listener receiver

上一拍把 window 和 document 的 `addEventListener` 改成按目标保存监听器。接收者不是对象时，`WeakMap` 抛出 TypeError。编排脚本被这个异常停住，没有发出 challenge-fo。事件循环仍有 tick。`document.currentScript` 仍是 null。

这一处只改 Node `host-globals.js`：`addEventListener`、`removeEventListener` 和 `dispatchEvent` 在接收者是 null 或非对象时，改用页面 window 的监听桶。对象接收者仍用自己的桶。`createElement` 和 `HTMLFormElement.submit` 没有改。没有改写 Node `env.js`，没有改 helper，没有新的官方 baseline。

本地断言 `BARE_LISTENER_OK`。`EVENT_TARGET_OK`、`CURRENT_SCRIPT_OK`、`WORKER_OK` 仍通过。

一次新的新鲜页由 Node https 取得，只接受编排 HTTP 200 且 title length 16。回执是 `diagnostics/post-event-20261023/node-rerun-receipt.json`。

- 23:46:59Z：页面 403 / 5726，title length 16，编排 200 / 252809，cookiePairs 1。22 秒切断，stdout 0，stderr 0，errorStages 只有 timeout。求解器没有打印请求类，没有证书 document POST，没有读回。

改前没有 challenge-fo 完成状态，这不是 `serverAccepted`。本拍没有重跑官方 baseline。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。事实哈希仍是 `3440737267cfafd35667c1c836d4425a49ed46b409c8486e7e82fcd2473f44a9`，3540 字节。`next` 没有 factWrites。盖章 `2026-10-22T23:49:46Z` 仍是 `authorize_form_construction_surface` / `blocked`。
