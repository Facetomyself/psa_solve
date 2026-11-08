# 2026-10-22 iframe 文档自有空树

已保存的 api.js 是 86732 字节，哈希与现场转储字节数一致。源码没有 `.Function`，没有方括号形式的 Function，也没有 contentDocument。两处 Function 标识符分别是 `Function.bind.apply` 和 `Function.toString.call`。`.contentWindow` 有 3 处。`.body` 有 6 处，`.documentElement` 有 1 处，`.head` 有 1 处，离 contentWindow 的距离类分别是 mid、mid、far。两处 `createElement("input")` 仍在嵌套函数里，源码没有 `.submit(`，没有 form 标记。

页面 iframe 文档原来用 `Object.create` 继承父文档，所以 body 和 head 就是父页面的节点。这一处只改 Node `host-dom.js`：allow-same-origin iframe 文档拥有自己的空 html、head 和 body。`createElement` 和 `HTMLFormElement.submit` 仍是原来的构造器。没有自动 submit，没有改写 Node `env.js`，没有改 helper，没有新的官方 baseline。

本地断言走已装载的 `runtime/code.js`，结果 `IFRAME_DOC_TREE_OK`。iframe 的 body、head、documentElement 都不同于父文档，documentElement 的子节点是该 head 和该 body。独立 Function 仍能编译出证书路径的 POST。`IFRAME_FUNCTION_OK`、`SCRIPT_SRC_OK`、`FORM_MARKUP_OK` 仍通过。形状探针里 `bodyShared` 和 `headShared` 都是 false。

Python urllib 这一拍拿到的都是 5844 字节、title length 32、带 jsd 且没有 orchestrate 的页，没有当作求解会话。两次新鲜页改由 Node https 取得。

- 19:53:04Z：页面 403 / 5726，title length 16，编排 200 / 255408，cookiePairs 1。求解在 120 秒时仍未退出，stdout 0，stderr 0。没有请求类，没有证书 document POST，没有同租约读回。
- 19:55:06Z：页面 403 / 5726，title length 16，编排 200 / 259837，cookiePairs 1。同样在 120 秒时切断，stdout 0，stderr 0。

同一份已取回的托管页在 5 秒和 15 秒的计数相同，说明进程不是还在建节点：eval 5，script 2，iframe 2，html/head/body 各 2，div 15，其他 9，input 0，form 0，submit 0。空文档树让执行越过了原先只建一个 iframe 就返回的位置，然后停在不再创建节点的同步自旋。vm 的 60 秒上限没有把这次自旋收回来。

本拍没有重跑官方 baseline。上一发绑定的 baseline 仍是 `7e39848290c24e83867be54eb6ed8fca`。

没有证书 document POST，也没有同租约 HTTP 200 读回。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 保持 null。`next` 没有 factWrites。事实哈希仍是 `3440737267cfafd35667c1c836d4425a49ed46b409c8486e7e82fcd2473f44a9`。盖章 `2026-10-22T20:04:40Z` 仍是 `authorize_form_construction_surface` / `blocked`。
