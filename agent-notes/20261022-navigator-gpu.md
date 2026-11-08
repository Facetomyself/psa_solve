# 2026-10-22 navigator.gpu

已保存的新鲜页会在 POST challenge-fo 之前读一次 `navigator.gpu`，当时这个属性不存在。`performance.getEntriesByType("resource")` 发生在那次 FO 返回之后。13 字节的 blob Worker 没有碰到宿主调用。

这一处只改 Node `host-globals.js`：`navigator.gpu` 提供 `requestAdapter` 和 `getPreferredCanvasFormat`。`requestAdapter` 解析出一个 adapter，`requestDevice` 解析出一个 device。`createElement` 和 `HTMLFormElement.submit` 没有改。没有改写 Node `env.js`，没有改 helper，没有新的官方 baseline。

本地断言 `GPU_OK`。`FONTS_OK`、`IFRAME_DOC_TREE_OK`、`IFRAME_FUNCTION_OK`、`SCRIPT_SRC_OK`、`FORM_MARKUP_OK` 仍通过。

改完之后，旧的已保存页再跑仍是 3507 毫秒结束：POST challenge-fo HTTP 400，体长类 `1000-4999`，读回 403，没有证书 document POST。`solverReportedOk` 为 true，不是 `serverAccepted`。

两次新的新鲜页由 Node https 取得，只接受编排 HTTP 200 且 title length 16。回执是 `diagnostics/navigator-gpu-20261023/node-rerun-receipt.json`。

- 21:34:14Z：页面 403 / 5726，title length 16，编排 200 / 259337，cookiePairs 1。45 秒切断，wallMs 45011，stdout 0，stderr 0，errorStages 只有 timeout。求解器没有打印请求类，没有证书 document POST，没有读回。
- 21:35:00Z：页面 403 / 5726，title length 16，编排 200 / 250151，cookiePairs 1。wallMs 45009，同样 stdout 0，stderr 0。

只包了 XHR 状态的计数器在第一页 12 秒内看到 POST challenge-fo 体长类 `1000-4999` 进入完成，状态 200。进程没有从编排返回，stdout 仍是 0。没有证书 document POST，没有同租约读回。这个状态不是 `serverAccepted`。更宽的计数在这次完成之后还看到第二个 blob Worker，源里有 postMessage 和 onmessage，本拍没有改 Worker。

本拍没有重跑官方 baseline。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。事实哈希仍是 `3440737267cfafd35667c1c836d4425a49ed46b409c8486e7e82fcd2473f44a9`，3540 字节。`next` 没有 factWrites。盖章 `2026-10-22T21:40:01Z` 仍是 `authorize_form_construction_surface` / `blocked`。
