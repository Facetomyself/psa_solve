# 2026-10-22 iframe Function 独立 realm

两次已加载脚本都执行完成，正文长度类 `20000+`，没有抛错。同步执行期间只创建了一个 iframe，没有 submit，没有 form 或 input 标记，没有 document.write。这个 iframe 的 sandbox 类是 allow-same-origin。执行读取了 contentWindow 一次、contentDocument 一次、Function 一次，没有调用 contentWindow.eval。

第一条脚本的源码字面量是 div 5、iframe 2、input 2、script 1、其他 1。没有动态 createElement 参数，没有 `<form`，没有 `.submit(`，没有 requestSubmit，没有 HTMLFormElement。两处 createElement("input") 在这次同步执行里没有走到。第二条脚本没有这些字面量。编排脚本里也没有这些明文。

页面 iframe 的 contentWindow.Function 原来和页面 Function 是同一个对象。这一处只改 Node `host-dom.js`：iframe 的 Function 换成 vm context 里的独立 Function。编译出的函数使用该 iframe 文档。`HTMLFormElement.submit` 没有改。没有自动 submit，没有改写 Node `env.js`，没有改 helper，没有新的官方 baseline。

本地断言走已装载的 `runtime/code.js`，结果 `IFRAME_FUNCTION_OK`。contentWindow.Function 不同于页面 Function，也不同于 parent.Function。用它编译的函数可以 createElement("form")、放入 input，并调用已有 submit。捕获请求是 POST，URL 含证书路径，正文是控件名值。`SCRIPT_SRC_OK`、`FORM_MARKUP_OK`、`LANG_DEFAULT_OK`、`ACCEPT_DEFAULT_OK`、`ORIGIN_SECFETCH_OK`、`CTYPE_DEFAULT_OK` 仍通过。

两次新鲜 `runtime/run.js`：

- 19:08:57Z：页面 403 / 5683，编排 200 / 256777，cookiePairs 1，exit 0，elapsedMs 3504，wallMs 9160，stdout 6367，stderr 0。GET `orchestrate-script` 与 GET `other` 体长类 `0`，响应 200 / `20000+`。POST `challenge-fo` 体长类 `1000-4999`，响应 400 / `1-999`。另有 POST `challenge-platform` 体长类 `0`。证书 document POST 没有出现。读回 403，titleLen 16，pageKind challenge，bodyLengthClass `5000-19999`。errorStages 空。`ebCall` 0。`solverReportedOk` true。
- 19:09:50Z：页面 403 / 5662，编排 200 / 256777，cookiePairs 1，exit 0，elapsedMs 3503，wallMs 9157，stdout 6362，stderr 0。请求类相同。响应类相同，顺序不同。读回相同。`ebCall` 0。

独立 Function 没有让新鲜求解发出证书 document POST。

本拍没有重跑官方 baseline。上一发绑定的 baseline 仍是 `7e39848290c24e83867be54eb6ed8fca`。

`solverReportedOk` 为 true。它不是 `serverAccepted`。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。`next` 没有 factWrites。事实哈希仍是 `3440737267cfafd35667c1c836d4425a49ed46b409c8486e7e82fcd2473f44a9`。盖章 `2026-10-22T19:10:47Z` 仍是 `authorize_form_construction_surface` / `blocked`。
