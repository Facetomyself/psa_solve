# 2026-10-21 verify_host_execution

`web_case.py next` 盖章 action `verify_host_execution`，turnGate `blocked`，updatedAt `2026-10-21T19:41:38Z`，session 本会话。约束是 `tool-evidence-required`、`ai-notes-are-not-facts`、`no-new-host-surface`、`goal-incomplete-does-not-override`。

`host_evidence.load_scope` 成功。scope `246b609f31e204a4ce73c04d5b64144ff26b099b66ca4c9efa7a42d1cba70267`。state status `failed`。baseline 回执 `e5aa21bfdb224d9a95f6c2d4ffad0ed7`，execution ref sha256 `8cc23532fb7597c389bc20e1f2e928878486a1d0422e312ad82e223cadbb53db`。

`validate_execution` 抛出 `execution did not complete successfully`。回执 status 是 `failed`，exitCode 1，timedOut false，pid 43432，elapsedNs 9280662600。failure 字段同一句。runner、runtime、input、source、config、raw、stdout、stderr、side 的 `verify_ref` 通过，绑定哈希没有变。

raw sha256 `d650d3aa3073d5f9d686d9c013ce6eff0d2c367905024ecb76e77abe515b0ee0`，223 字节。side sha256 `8713e6e34f37c7669da3f5e52735e31b024d6fda47cdb50a0918e2d410af409f`，479 字节。事件只有 `host-diagnostic` 和 `summary`。没有 `host-observation`，没有 wire、necko、resp。

scriptError：第 1 行第 98085 列，errorName `TypeError`，kind `other`，class `null-receiver`，sourceForm `other`，sourceClass `other`，insecure false，parentLine 1900，sourceLineLength 0，keywordAtColumn false，stackShape `other`，flags 0，categoryClass `content-javascript`，receiverState `unknown`，receiverId `uncollected`。class 名不是观察到的空接收者。调用点仍是第 1 行第 75507 列。源第 1 行长度不少于 98085，所以这一列在文件内，但 sourceLineLength 0，不是标识符。

`_turnstile_in_file_error` 为 false。`_out_of_file_slow_script` 返回空。直接 `_host_evidence_gate` 仍是 `verify_host_execution` / `blocked` / `no-new-host-surface`，没有 `one-host-behavior`，也不改写磁盘盖章。

facts：`localReproduced` false，`serverAccepted` false，`requestBoundaryAligned` false，`experimentHygiene` `ok`，`hostProbe` null，revision 53。没有证书 document POST，没有同租约回读。这一拍没有改 helper，没有重跑 baseline，没有写完成轴。
