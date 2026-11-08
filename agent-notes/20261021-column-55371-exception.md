# 2026-10-21 第 55371 列例外

本回合 `web_case.py next` 仍是 `verify_host_execution`，`turnGate=blocked`，约束含 `no-new-host-surface`。按放行只改了这一条门，没有改 helper，没有重跑 baseline，没有写完成轴。

`_out_of_file_slow_script` 仍要求失败的 submit baseline、唯一一条 matched false 的 host-diagnostic、没有 host-observation、slow-script 的行和列与诊断一致。源文件外的 `kind=orch`，以及源文件外的 `kind=other` 且 `sourceForm=token`，仍可做一处同 scope 宿主修补。其它源文件内的列仍停在 `verify_host_execution`。

唯一新增例外：诊断列等于 55371，并且该列落在源行内，并且 side 是 `kind=other`、`sourceForm=token`。同列的 `kind=orch`、其它 sourceForm、以及相邻列 55370，仍不放行。

对当前 scope `9776d304a14379f1` 的 baseline `1adb8824` 调用这个函数，动作是 `repair_submit_host_behavior`。原因写明第 1 行第 55371 列，调用点仍是第 75507 列。这不是新的官方执行，也不是证书 document POST。

完成轴仍是 localReproduced false、serverAccepted false、requestBoundaryAligned false，experimentHygiene 为 ok。
