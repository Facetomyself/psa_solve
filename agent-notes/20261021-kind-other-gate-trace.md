# 第 2 行第 3028 列为什么停在 kind other 且修补门为空

2026-10-21。本拍 `next` 仍是 `verify_host_execution`，`turnGate=blocked`，约束含 `no-new-host-surface`。同一份 baseline 回执不再复述。下面是已交付代码里的两条路径。

监听器在 `host_submit_collector.py` 里丢掉带 `warningFlag` 的控制台消息，再用 `sourceName` 写 `kind`：含 `chl_page` 或 `orchestrate` 为 `orch`，含 `performance-host-probe` 为 `probe`，含 `submit-challenge` 为 `page`，其余为 `other`。`class` 只看错误文本里有没有 `submit`、`getEntries`、`is null` 或 `undefined`，否则为 `other`。这份 side 的 `scriptError` 只有 `kind`、`class`、`line`、`column`。收集器全文没有 `sourceForm` 或 `sourceClass`，也不保存 `sourceName`。所以 `kind=other` 只说明当时的 `sourceName` 没有那四个片段。

`collect_rows` 写进诊断行的 `sourceSha256` 永远是绑定的 `submit-orchestrate.js`，不能用来证明抛错脚本就是这个文件。`attributable` 只在第 1 行第 75507 列给出 `matched true`。第 2 行因此是 `host-diagnostic`。

绑定源文件 3 行，第 2 行长度 23576。第 3028 列在行内，所在标识符是关键字 `function`，列号落在该词最后一个字符。helper 第 2 行长度 31，容不下这一列。

`_out_of_file_slow_script` 先判断这一列在绑定源文件内，并且列号不是 55371，然后直接返回空。`slow-script`、`kind` 和 `sourceForm` 都还没读到。把 `kind` 改成 `orch` 也过不了这一行。`validate_execution` 仍要求 status `completed` 且 exitCode 0，当前回执过不了，`classify` 也要求另一份 patched 执行。

本拍盖章没有放行同 scope 宿主改动。helper、收集器和门都没有改。没有证书 document POST，也没有同租约回读。完成轴保持 false。
