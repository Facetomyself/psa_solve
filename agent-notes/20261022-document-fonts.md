# 2026-10-22 document.fonts

已保存托管页上的 iframe 2、div 15、input 0、form 0、submit 0 不是 createElement 自旋。求解约 3504 毫秒结束 DOM 工作，随后停在轮询和约 5 秒的同租约读回。CPU 采样里绝大多数命中是 idle。允许名单上的热计数也不热：submit 0，attachShadow 0，XHR 回调抛错 0。

缺失的宿主读取是 `document.fonts` 3 次，`document.elementFromPoint` 3 次，`performance.getEntriesByType` 1 次。这两处名字不在已保存的 86732 字节 api.js 里，读取来自编排脚本。本拍只补 `document.fonts`。`elementFromPoint` 留着没补。

这一处只改 Node `host-dom.js`：页面文档的 `document.fonts` 是已加载的空 FontFaceSet。`status` 是 `loaded`，`size` 是 0，`ready` 解析到这个集合本身。`check` 对固定的 generic CSS 族和一份 Windows 字体名单返回 true，其余返回 false。`load` 解析空数组。`forEach` 和 `add` 是空操作，`delete` 和 `has` 返回 false。iframe 文档用 `Object.create` 继承同一对象。`createElement` 和 `HTMLFormElement.submit` 没有改。没有自动 submit，没有改写 Node `env.js`，没有改 helper，没有新的官方 baseline。

临时让 `appendChild` 写下 `parentNode` 和 `parentElement` 的试验，没有改变已保存页 challenge-fo 的 HTTP 状态或体长，已经撤回。`appendChild` 仍只把节点推进 `children`。

本地断言走已装载的 `runtime/code.js`，结果 `FONTS_OK`。`IFRAME_DOC_TREE_OK`、`IFRAME_FUNCTION_OK`、`SCRIPT_SRC_OK`、`FORM_MARKUP_OK` 在装上 fonts 的源上仍通过。

已保存回放的 challenge-fo 仍是 POST、HTTP 400、体长 2295、体长类 `1000-4999`。有 fonts 的体哈希是 `88a13b0d43e6932c5e4a3724143bccab22e0f83e7ee656cefbe7b7470a4de257`，没有 fonts 的体哈希是 `c4b04ecc261f1a3b375d59835985a7b1e5c94916a5df1ad92e7f0621b30af495`。长度相同，状态没有离开 400。读回 HTTP 403，title length 16，pageKind challenge，体长类 `5000-19999`。没有证书 document POST。`ebCall` 0。`solverReportedOk` 为 true，不是 `serverAccepted`。

新鲜编排会挡住事件循环。20 秒的定时器探针在有 fonts 时，以及暂时拿掉 fonts 之后，都只记到 tickCount 1，xhr 0，stdout 0。没有把 vm 的 60 秒上限当成宿主修复。

两次新鲜页由 Node https 取得，只接受编排 HTTP 200 且 title length 16。回执是 `diagnostics/iframe-fonts-20261023/node-rerun-receipt.json`。

- 20:40:36Z：页面 403 / 5726，title length 16，编排 200 / 250771，cookiePairs 1。45 秒切断，wallMs 45009，stdout 0，stderr 0，errorStages 只有 timeout。没有请求类，没有证书 document POST，没有读回。
- 20:41:23Z：页面 403 / 5726，title length 16，编排 200 / 264891，cookiePairs 1。wallMs 45008，同样 stdout 0，stderr 0。

本拍没有重跑官方 baseline。上一发绑定的 baseline 仍是 `7e39848290c24e83867be54eb6ed8fca`。

没有证书 document POST，也没有同租约 HTTP 200 读回。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。事实哈希仍是 `3440737267cfafd35667c1c836d4425a49ed46b409c8486e7e82fcd2473f44a9`，3540 字节。`next` 没有 factWrites。盖章 `2026-10-22T20:45:48Z` 仍是 `authorize_form_construction_surface` / `blocked`。
