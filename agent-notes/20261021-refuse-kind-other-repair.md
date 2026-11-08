# 未放行 kind=other 的宿主修补

对 scope `66687399f484a9e2` 再跑一次 `web_case.py next`。动作仍是 `verify_host_execution`，`turnGate=blocked`。约束含 `no-new-host-surface` 和 `goal-incomplete-does-not-override`。

回执 `bfd29989deb2429db7c4ad22b78a2ff5` 的侧记仍是 kind=`other`、sourceForm=`token`、第 1 行第 1337365 列。`sourceForm=token` 只说明警告来源不是空名、eval、about、null principal 或带 `://` 的 URL，不能把它当成编排脚本。

已发布 `_out_of_file_slow_script` 对这张回执返回空。`validate_execution` 仍是 `execution did not complete successfully`。exitCode=1，timedOut=false。

已发布测试 `test_in_file_or_summary_failure_stays_verify` 的默认 `script_kind=other`、列 5000 必须停在 `verify_host_execution`。`test_out_of_file_slow_script_authorizes_one_host_repair` 只在 kind=`orch` 时给出 `repair_submit_host_behavior`。这两项本拍 OK。门没有改。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 仍是 false。事实文件字节没有被这次核对改写。没有证书 document POST，也没有同租约回读。

随后一回合再次请求把同一回执放成 same-scope repair，或放宽 orch-only / `no-new-host-surface`。再跑一次 `web_case.py next`，动作仍是 `verify_host_execution`，`turnGate=blocked`，约束未变。没有改 `web_case.py`。计划验收的两次新鲜 Node 会话、证书 document POST 和约 5 秒后的同租约 HTTP 200 回读都不存在，完成轴保持 false。

再下一回合请求写成明确的计划或盖章例外。`web_case.py next` 仍是 `verify_host_execution`，`turnGate=blocked`，约束仍含 `no-new-host-surface` 与 `goal-incomplete-does-not-override`。没有写例外，没有改门，没有改 `auto-decision-facts.json`。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 仍是 false。

本回合同一请求再来一次。`web_case.py next` 仍是该动作和这两条约束。没有写例外，没有改门，没有写完成轴。

随后一回合把同一请求再说一遍，并写明在授权出现之前不得改门、不得写完成轴。`web_case.py next` 仍是 `verify_host_execution`，`turnGate=blocked`，约束未变。没有写例外，没有改门，没有写完成轴。
