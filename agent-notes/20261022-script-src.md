# 2026-10-22 script src 执行

新鲜求解没有调用 `createElement("form")`，也没有写入 form、input、button、select 或 textarea 标记，没有 `document.write`，没有 `HTMLFormElement.submit`。安全追踪里，createElement 落到 script、iframe 和排障标签，然后给 script 设置 src。其中一条是相对的 challenge-platform 脚本，另一条是绝对的 other 脚本。img 也设置了 src。两个 iframe 没有设置 src。随后画出排障 DOM。那次追踪不是本拍改动，也没有替换 `document`。

这一处只改 Node `host-dom.js`。`HTMLScriptElement` 的 src（属性或 `setAttribute("src")`）按 `location.href` 解析成绝对地址。结果是 http(s) 时，用已有 `XMLHttpRequest` 取一次，调用方带上 `Sec-Fetch-Dest: script` 和 `Sec-Fetch-Mode: no-cors`。HTTP 200 且正文非空时，在页面 realm 执行，执行期间 `document.currentScript` 是该元素。失败被吞掉。img 和非 http(s) 不取。同一个元素不重复加载。没有自动调用 submit，没有硬编码证书 POST。没有改写 Node `env.js`，没有改 helper，没有改编排脚本，没有新的官方 baseline。

本地断言走已装载的 `runtime/code.js`，结果 `SCRIPT_SRC_OK`。交付的脚本自己创建 form 并调用 submit 时，捕获请求是 POST，URL 含证书路径，正文是控件名值。相对地址会解析成 http(s) GET。404 正文不执行。`FORM_MARKUP_OK`、`LANG_DEFAULT_OK`、`ACCEPT_DEFAULT_OK`、`ORIGIN_SECFETCH_OK`、`CTYPE_DEFAULT_OK` 在这次改动之后仍通过。

解析相对地址之前的两发只取到绝对 other 脚本（18:46:31Z、18:46:41Z），不是正式重跑。正式两发是解析之后的：

- 18:48:07Z：页面 403 / 5662，编排 200 / 256700，cookiePairs 1，exit 0，elapsedMs 3505，wallMs 9186，stdout 6365，stderr 0。GET `orchestrate-script` 体长类 `0`，响应 200 / `20000+`。GET `other` 体长类 `0`，响应 200 / `20000+`。POST `challenge-fo` 体长类 `1000-4999`，响应 400 / `1-999`。另有 POST `challenge-platform` 体长类 `0`。证书 document POST 没有出现。读回 403，titleLen 16，pageKind challenge，bodyLengthClass `5000-19999`。errorStages 空。`ebCall` 0。`solverReportedOk` true。
- 18:48:43Z：页面 403 / 5662，编排 200 / 250279，cookiePairs 1，exit 0，elapsedMs 3504，wallMs 9151，stdout 6376，stderr 0。请求类相同。响应类相同，顺序不同。读回相同。`ebCall` 0。

两个外部脚本都是 HTTP 200，正文非空，因此具备执行条件。求解仍然没有发出证书 document POST。不能把这次执行写成已经创建了 form。

方法、URL 类和体长类与有头首页 FO 同级，状态不是 200。证书 document POST 没有出现，同租约读回不是 HTTP 200。

本拍没有重跑官方 baseline。上一发绑定的 baseline 仍是 `7e39848290c24e83867be54eb6ed8fca`。

`solverReportedOk` 为 true。它不是 `serverAccepted`。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。`next` 没有 factWrites。事实哈希仍是 `3440737267cfafd35667c1c836d4425a49ed46b409c8486e7e82fcd2473f44a9`。盖章 `2026-10-22T18:52:49Z` 仍是 `authorize_form_construction_surface` / `blocked`。
