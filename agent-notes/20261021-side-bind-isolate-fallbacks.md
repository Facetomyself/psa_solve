# side 绑定、接收者未知、隔离无依据兜底

2026-10-21。晚间审计指出三处未闭合：执行回执不哈希 side、`receiverId="null"` 是采集占位、Location / contentWindow / window 兜底仍在默认路径。本拍只处理这三处，不新增宿主行为，不写完成轴。

## 代码

- `host_evidence.execute` 在 `submit-host-side.json` 存在时写入 `execution.side` 的路径和 sha256。`validate_execution` 在回执带 side 时核对它就是 raw 旁边的那份文件。
- 门通过 `_bound_collector_side` 读取 side。没有引用，或字节与 sha256 不一致，不能用这份 side 授权修补。
- `describeScriptError` 不再写死 `receiverId="null"`。未采集时是 `receiverState=unknown`、`receiverId=uncollected`。`_receiver_observation` 只在 `receiverState=empty` 且 `receiverId=null` 时返回 empty；历史占位返回 unknown。
- 源文件第 2 行第 3028 列只要带了 sourceForm / sourceClass，就留在 `verify_host_execution`。未知接收者和已观测的空接收者都不放行 `repair_null_receiver_identity`。
- `document-principal.js` 的默认安装不再调用 `installSandboxIdentity`、`installPageLocationPrimitive`、`installFrameWindowPrimitive`、`installWindowPrimitive`。函数体还在文件里，调用点没有了。临时 Debugger 探针已撤。

## 重签与官方基线

helper sha256 `d73e3c0f686c61d7011abacbe84b3cded724d318aaddeee65693c0739394badc`。runner sha256 `1bca9637b8c3be41933b6677b88659fd8a4229450a6b9703d9e21f8c1dfff6e4`。scope `201ebcb1f13417f0e334bbbc6d57ff5aaa15e0836c59e24c65d210e12573682e`。`665de0ce…` 与 baseline `69cede48e67541ce9b3590ffc0d72316` 在 priorScope。`load_scope` 通过。

`next` 会话 `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`，动作 `run_host_baseline`，`turnGate=blocked`，约束含 `no-new-host-surface`。

官方 baseline `ca950504b7124f57ad468e0893e93830`：failed，exitCode 1，timedOut false，pid 57228，约 9.077 秒。failure 是 `execution did not complete successfully`。诊断第 2 行第 3028 列，matched false，base object。事件只有 host-diagnostic 和 summary。raw 222 字节，sha256 `534609ca23a0472c035bc74092454398420761e448eb632583db28adac35ac2c`，与 `69cede48` 相同。side sha256 `a2dcacf288a0940edbfe533e60332a67ea4947ff38512eefea7f178ef1f3bcc1`，回执含 side 引用。scriptError：injected / about-blank-injected / SecurityError / parentLine 1447 / sourceLineLength 0 / stackShape other / receiverState unknown / receiverId uncollected。

隔离兜底没有改变这条 raw。第 3028 列的 SecurityError 不是这几处默认兜底造成的可观察差异。没有 host-observation，没有请求行，没有证书 document POST，没有同租约回读。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 仍是 false。`experimentHygiene` 仍是 `ok`。

## 回归

`test_receiver_observation_splits_unknown_from_empty`、`test_identity_column_does_not_authorize_host_behavior`、`test_unbound_or_tampered_side_does_not_authorize_repair`、`test_historical_3028_side_is_unbound_placeholder`、`test_default_path_isolates_unproven_identity_fallbacks`、`test_shipped_collector_script_error_records_identity_without_message_text`、`test_out_of_file_slow_script_authorizes_one_host_repair`、`test_in_file_function_keyword_authorizes_one_host_repair`、`test_in_file_function_keyword_other_shapes_stay_verify`、`test_null_receiver_injected_security_error_nearby_shapes_stay_verify`、`test_helper_url_line_1439_authorizes_one_host_repair`、`test_in_file_column_55371_token_authorizes_one_host_repair` 通过。
