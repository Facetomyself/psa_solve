# 再次核验 d0d52ad，戳记仍不授权宿主修补

2026-10-21。`next` 会话 `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`，updatedAt `2026-10-21T16:50:05Z`，动作 `verify_host_execution`，`turnGate=blocked`。约束是 `tool-evidence-required`、`ai-notes-are-not-facts`、`no-new-host-surface`、`goal-incomplete-does-not-override`。原因是 baseline 工具未成功完成，不得用摘要推进。上一张 16:41:55Z 的诊断笔记已经落盘，这张是新戳记。本拍只调用已发布的 `load_scope`、`verify_ref`、`validate_execution`、`_host_evidence_gate`、`_injected_blank_security_error` 和 `doc_health`。没有改 helper，没有改采集器，没有重签 scope，没有重跑 baseline。

## 工具结果

`load_scope` 通过。state、scope、回执的 scopeId 都是 `cad998e64e5e73772ec42c3d32dd391e453d8c92b708a0107861d0db29ffa920`。scope 的 sessionId 是本会话。helper sha256 `dce0c26a11376011f3082f594f4c296d82e24d32984e363b8e3c463f4033839e`，与文件字节一致。采集器 sha256 仍是 `1bca9637b8c3be41933b6677b88659fd8a4229450a6b9703d9e21f8c1dfff6e4`。

baseline 仍是 `d0d52ad4073e4515b48f9d01c3d72c0c`：status failed，exitCode 1，timedOut false，pid 52420，`finishedAt - startedAt` 为 6671748000 纳秒，约 6.672 秒。回执 failure 与 `validate_execution` 抛出的原文都是 `execution did not complete successfully`。runner、runtime、input、source、config、raw、stdout、stderr 的 `verify_ref` 通过。`argvHash` 与当前 scope 命令一致。stdout、stderr 都是 0 字节。

回执没有 `side` 键。`submit-host-side.json` 仍不存在。目录文件仍是 `execution.json`、`raw.jsonl`、`stderr.txt`、`stdout.txt`、`submit-host-probe.js`。raw 仍是 47 字节，sha256 `b441668b639a2f5131505f3e9f487cc348c64e5bc5162cebe63f8cede6702d32`，事件只有 summary。没有 host-diagnostic，没有 host-observation，没有请求行。side 缺失的原因见 `agent-notes/20261021-verify-d0d52ad.md`：监听器只记录未捕获的非警告脚本错误。

`_injected_blank_security_error` 对空身份返回 false。`_host_evidence_gate` 仍返回 `verify_host_execution`，约束仍含 `no-new-host-surface`。这张戳记没有签发 `repair_submit_host_behavior`。

## 完成轴

没有证书 document POST，没有同租约回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 仍是 false。`experimentHygiene` 仍是 `ok`。facts revision 仍是 53。facts 字节在本次调用前后一致。`doc_health` 为 `[]`，index 仍是 80 行。缺的是带 side 的成功执行，以及证书 document POST 和同租约 HTTP 200 回读。失败 summary 不能写成这三项。
