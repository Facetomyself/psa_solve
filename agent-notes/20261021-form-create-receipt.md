# 2026-10-21 提交前的 createElement 回执

`web_case.py next` 仍是 `repair_submit_host_behavior`，`turnGate=blocked`。本拍没有改 helper、runner、scope 或 Node 元素表，也没有写完成轴。

浏览器 run `rt_20261005125421_1d84c46dcd` 的 `evidence/web/ruyitrace/rt_20261005125421_1d84c46dcd/raw/domtrace/trace_process_51372.ndjson`：

- 第 90684 行是 `Document.createElement`，标签 `form`。同进程该成员还有 `input` 4 次、`div` 18 次。
- 第 90855、90869 行是 `HTMLFormElement` `set action`。第 90882 行是 `get elements`。第 90886 行是 `call submit`。

这是提交前的浏览器事实。它点名的属性是 `Document.createElement`，标签 `form`，随后才是 `HTMLFormElement.submit`。

Node `runtime/lib/host-dom.js` 的 `elementConstructors` 没有 `form`。该标签会落到 `HTMLElement`，对象上没有 `HTMLFormElement.submit`。

当前失败的官方 baseline 不是这条 Node 元素表。它跑在 Gecko 上，Gecko 已有 `Document.createElement` 和 `HTMLFormElement`。回执 `329f75aa9405418dbc6332d9af2780a8` 仍停在源文件外慢脚本第 1 行第 1337365 列，没有 host-observation。把 Node 的 `form` 补进元素表不会让这份 Gecko 脚本走到第 75507 列，所以这一处行为没有花在这条映射上。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。
