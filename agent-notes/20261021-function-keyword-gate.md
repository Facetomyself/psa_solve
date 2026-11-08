# 第 2 行第 3028 列放行同 scope 修补

2026-10-21。`verify_host_execution` 带着 `no-new-host-surface` 停住。本拍只加一条门放行，不写完成轴。

放行条件同时成立才返回 `repair_submit_host_behavior`：

- 诊断行在绑定源文件内，行号 2，列号 3028。
- 这一列是关键字 `function` 的最后一个字符。
- side 的 class 是 `other`，kind 是 `other`。
- side 没有 `sourceForm`，也没有 `sourceClass`。

列号不是 55371 的其它行内位置、慢脚本、kind 不是 `other`、或者带了 `sourceForm` / `sourceClass`，仍返回空，动作仍是 `verify_host_execution`。

测试走 `next_command`。`test_in_file_function_keyword_authorizes_one_host_repair` 得到修补动作。`test_in_file_function_keyword_other_shapes_stay_verify` 覆盖列 3027、行 1、kind `orch`、class `slow-script`、`sourceForm=url`、`sourceClass=helper`、关键字被改掉、以及第 5000 列 url。原有 55371、1439、行内慢脚本和源文件外慢脚本测试仍通过。

对已绑定回执直接调用 `_out_of_file_slow_script`，动作是 `repair_submit_host_behavior`，`turnGate=blocked`，约束里没有 `no-new-host-surface`。随后 `web_case.py next` 给出同一张盖章。

这张盖章允许一处宿主行为。side 的 `scriptError` 只有 kind、class、line、column，没有错误名。第 3028 列位于属性冒号之后、参数列表之前。没有点名缺哪个宿主 API。本拍没有改 helper，没有重签 scope，没有重跑 baseline。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 仍是 false。
