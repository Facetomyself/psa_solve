# 2026-10-22 document.elementFromPoint

上一拍两次新鲜会话在 45 秒时 stdout 为 0，所以没有请求类。把当时取回的一页再跑，求解 3505 毫秒就结束：POST challenge-fo 仍是 HTTP 400，体长类 `1000-4999`，读回 HTTP 403，没有证书 document POST。前 5 秒采样几乎是 idle，事件循环在走定时器和网络，不是 createElement 自旋。这页上 `document.elementFromPoint` 读了 3 次，`performance.getEntriesByType` 读了 1 次。

这一处只改 Node `host-dom.js`：`document.elementFromPoint` 在坐标是有限非负数、并且落在已有正 viewport 内时返回该文档的 body；负数、非数值或越出 viewport 返回 null。iframe 文档继承同一个函数，没有 viewport 时不按 0 宽高裁掉。`createElement` 和 `HTMLFormElement.submit` 没有改。没有改写 Node `env.js`，没有改 helper，没有新的官方 baseline。

本地断言 `EFP_OK`。`FONTS_OK`、`IFRAME_DOC_TREE_OK`、`IFRAME_FUNCTION_OK`、`SCRIPT_SRC_OK`、`FORM_MARKUP_OK` 仍通过。

新取的两页不是这条已结束的回放。5 秒采样里热样本在编排脚本的算术上，热窗口没有标准宿主名。两次新鲜页由 Node https 取得，只接受编排 HTTP 200 且 title length 16。回执是 `diagnostics/element-from-point-20261023/node-rerun-receipt.json`。

- 21:05:17Z：页面 403 / 5726，title length 16，编排 200 / 257222，cookiePairs 1。45 秒切断，wallMs 45009，stdout 0，stderr 0，errorStages 只有 timeout。没有请求类，没有证书 document POST，没有读回。
- 21:06:03Z：页面 403 / 5726，title length 16，编排 200 / 256516，cookiePairs 1。wallMs 45010，同样 stdout 0，stderr 0。

本拍没有重跑官方 baseline。没有证书 document POST，也没有同租约 HTTP 200 读回。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。事实哈希仍是 `3440737267cfafd35667c1c836d4425a49ed46b409c8486e7e82fcd2473f44a9`，3540 字节。`next` 没有 factWrites。盖章 `2026-10-22T21:09:25Z` 仍是 `authorize_form_construction_surface` / `blocked`。
