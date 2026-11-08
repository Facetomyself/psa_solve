# 请用户放行 web_case 门

`web_case.py next` 仍是 `verify_host_execution`，`turnGate=blocked`。约束含 `no-new-host-surface` 和 `goal-incomplete-does-not-override`。`humanRequired` 为 false。

当前 baseline 是 `329f75aa9405418dbc6332d9af2780a8`，scope `66687399f484a9e2`。exitCode=1，timedOut=false。kind=`other`，sourceForm=`token`，第 1 行第 1337365 列。已发布 `_out_of_file_slow_script` 返回空。只有 kind=`orch` 且列在源文件之外才授权一处同 scope 宿主修补。

本拍没有改门，没有开新宿主面，没有写完成轴。证书 document POST 和同租约 HTTP 200 回读都不存在。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 仍是 false。

需要用户明确选择其一：放行这次失败 baseline 的同 scope 宿主修补；或明确授权新宿主面。在此之前门保持原样。
