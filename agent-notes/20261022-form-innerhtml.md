# 2026-10-22 innerHTML 表单物化

请求头默认值已经证明带不走 `challenge-fo` 的 HTTP 400。已装载的 `Document.createElement("form")` 到 `HTMLFormElement.submit` 在新鲜求解里没有被调用。先前一次完整追踪里，createElement 落到排障标签，submit 调用是 0，`HTMLFormElement` 构造是 0，form 与 body 的 innerHTML 是 0，其他 innerHTML 写入 12 次。这 12 段不含 form 标签，也不含 input 标签。那次追踪不是本拍改动。

这一处只改 Node `host-dom.js` 的 `innerHTML`。赋值始终保存字符串。字符串含 form 或 input 标签时，才清空子节点，并用已有构造器建成 form 和 input。复制的属性只有 id、name、value、type、action、method。不含这些标签时，已有子节点保持不动。没有自动调用 submit。没有改写 Node `env.js`，没有改 helper，没有改编排脚本，没有新的官方 baseline。

本地断言走已装载的 `runtime/code.js`，结果 `FORM_MARKUP_OK`。含 form 的 innerHTML 得到 `HTMLFormElement`，`submit` 是原型方法，捕获请求是 POST，URL 类是证书 document，Content-Type 是 `application/x-www-form-urlencoded`。form 自身只含 input 的 innerHTML 也会把该控件交给同一次 `submit`。普通字符串不拆掉已有子节点。已有的 `LANG_DEFAULT_OK`、`ACCEPT_DEFAULT_OK`、`ORIGIN_SECFETCH_OK`、`CTYPE_DEFAULT_OK` 仍通过。

两次新鲜 `runtime/run.js`：

- 18:23:04Z：页面 403 / 5662，编排 200 / 244125，cookiePairs 1，exit 0，elapsedMs 3506，wallMs 9124，stderr 0。POST `challenge-fo` 体长类 `1000-4999`，响应 400 / `1-999`。另有 POST `challenge-platform` 体长类 `0`。证书 document POST 没有出现。读回 403，titleLen 16，pageKind challenge，bodyLengthClass `5000-19999`。errorStages 空。`ebCall` 0。`solverReportedOk` true。
- 18:23:15Z：页面 403 / 5662，编排 200 / 244125，cookiePairs 1，exit 0，elapsedMs 3503，wallMs 9110，stderr 0。请求类、响应类和读回与上一发相同。`ebCall` 0。

方法、URL 类和体长类与有头首页 FO 同级，状态不是 200。证书 document POST 没有出现，同租约读回不是 HTTP 200。这次物化没有在真实求解里发出证书 POST。

本拍没有重跑官方 baseline。上一发绑定的 baseline 仍是 `7e39848290c24e83867be54eb6ed8fca`。

`solverReportedOk` 为 true。它不是 `serverAccepted`。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。`next` 没有 factWrites。事实哈希仍是 `3440737267cfafd35667c1c836d4425a49ed46b409c8486e7e82fcd2473f44a9`。盖章 `2026-10-22T18:24:36Z` 仍是 `authorize_form_construction_surface` / `blocked`。
