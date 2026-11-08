# 2026-10-21 sourceForm baseline

慢脚本 warning 增加 `sourceForm`，取值只限 empty、eval、about、principal、url、token。不保存原始脚本名。门没有改：`kind=other` 仍不能授权宿主修补。

- 现有 helper 测试：`node --check` 通过；`test_slow_script_source_class_uses_shipped_helper`、`test_shipped_submit_helper_uses_real_eval`、`test_in_file_or_summary_failure_stays_verify` 共 3 项 OK。
- helper 变更后 scope 重签为 `66687399f484a9e279bc35c7199cd43e1499bc339f380c22706503c72bf40210`。`load_scope` 通过。执行槽清空。上一回 `35d601aa61ba43c0acc68b16eec6daa3` 留在 priorScope（scope `963fff7353f4deda`）。Gecko 锁哈希未变。runner、runtime、input、source、config 未变。
- `web_case.py next` 一次：`run_host_baseline`，`turnGate=blocked`，带 `no-new-host-surface`。
- 官方 baseline `bfd29989deb2429db7c4ad22b78a2ff5`：status=failed，exitCode=1，timedOut=false，约 22.718s，failure=`execution did not complete successfully`。raw 事件是 host-diagnostic 然后 summary。没有 host-observation。diagnostic matched=false，第 1 行第 1337365 列，列在源文件该行长度之外。
- side.scriptError 只有 kind、class、sourceClass、sourceForm、line、column。kind=`other`，class=`slow-script`，sourceClass=`other`，sourceForm=`token`，行 1，列 1337365。
- 发布的 `_out_of_file_slow_script` 对这张回执返回空。没有授权 repair。
- `serverAccepted`、`localReproduced`、`requestBoundaryAligned` 仍是 false。`experimentHygiene` 仍是此前的 `ok`，本拍没有改事实文件。没有证书 document POST，也没有同租约回读。
