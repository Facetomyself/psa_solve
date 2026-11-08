# 2026-10-22 blob Worker

新鲜页的 POST challenge-fo 到达完成且状态 200、体长类 `1000-4999` 之后，页面构造第二个 blob Worker，体长类 `1-999`。这段脚本读取 `self.trustedTypes.createPolicy`，随后把 `onmessage` 设成只在事件可信、origin 为空、source 为 null 时执行父页消息。父页没有调用 `postMessage`。事件循环心跳停在 1。改前的第一次 CPU 采样落在编排脚本里，没有宿主帧。列号没有记成观察。

这一处只改 Node `host-async.js`：记住 blob 文本，在自带 `trustedTypes` 的 worker realm 里执行，父页 `postMessage` 送出上述事件形状。页面全局没有 `trustedTypes`。`createElement` 和 `HTMLFormElement.submit` 没有改。没有改写 Node `env.js`，没有改 helper，没有新的官方 baseline。

本地断言 `WORKER_OK`。`GPU_OK`、`FONTS_OK`、`IFRAME_DOC_TREE_OK`、`IFRAME_FUNCTION_OK`、`SCRIPT_SRC_OK`、`FORM_MARKUP_OK` 仍通过。

已消耗页再跑 3503 毫秒结束：POST challenge-fo HTTP 400，响应体长类 `1-999`，读回 403，title length 16，pageKind challenge，没有证书 document POST。`solverReportedOk` 为 true，不是 `serverAccepted`。

一次新的新鲜页由 Node https 取得，只接受编排 HTTP 200 且 title length 16。回执是 `diagnostics/worker-realm-20261023/node-rerun-receipt.json`。

- 22:17:31Z：页面 403 / 5726，title length 16，编排 200 / 254719，cookiePairs 1。22 秒切断，stdout 0，stderr 0，errorStages 只有 timeout。求解器没有打印请求类，没有证书 document POST，没有读回。

本拍没有重跑官方 baseline。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。事实哈希仍是 `3440737267cfafd35667c1c836d4425a49ed46b409c8486e7e82fcd2473f44a9`，3540 字节。`next` 没有 factWrites。盖章 `2026-10-22T22:21:01Z` 仍是 `authorize_form_construction_surface` / `blocked`。
