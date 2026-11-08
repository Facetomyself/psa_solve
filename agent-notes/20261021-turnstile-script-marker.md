# 2026-10-21 脚本标记后的官方 baseline

盖章仍是 `2026-10-21T19:04:16Z` 的 `repair_submit_host_behavior`，`turnGate=blocked`。这一拍按那张印做了一处宿主行为并重跑绑定的官方 baseline，没有再 `next`。

宿主行为在 `document-principal.js` 的 `installTurnstileScriptMarker`。页面脚本之前写入一个 async 脚本标记。资源加载器把 `src` 挪到 data 属性后，原生读取会变成空，所以 `src` 读取在原生值为空时回落到 data 属性。标记能被页面查找表达式接受，斜杠数不是采集器提供脚本正文的那一档。身份 URI 等待和 history 包装仍在。没有 `processNextEvent`。

helper sha256 `75a3a9487b61a462ddf83ddd7c33ea0f1670651f505a84192993f717fdc69b85`。scope `246b609f31e204a4ce73c04d5b64144ff26b099b66ca4c9efa7a42d1cba70267`。`load_scope` 通过。priorScope 是 `f3d00067390e9a45dfb22a86c79d7402e3dcf51556d5659f4a08b7beb828fa92`，baseline `3b27b10032c4488ea5716bdd3326017f`。

官方 baseline `e5aa21bfdb224d9a95f6c2d4ffad0ed7`。执行引用 sha256 `8cc23532fb7597c389bc20e1f2e928878486a1d0422e312ad82e223cadbb53db`。status failed，exitCode 1，timedOut false，pid 43432，elapsedNs 9280662600。failure `execution did not complete successfully`。raw sha256 `d650d3aa3073d5f9d686d9c013ce6eff0d2c367905024ecb76e77abe515b0ee0`，223 字节。side sha256 `8713e6e34f37c7669da3f5e52735e31b024d6fda47cdb50a0918e2d410af409f`，479 字节。事件只有 `host-diagnostic` 和 `summary`。matched false。base `object`。finished true。没有 `host-observation`，没有请求行。

脚本错误已离开第 2 行第 16322 列的 `TurnstileError`。现为第 1 行第 98085 列，kind `other`，class `null-receiver`，sourceForm `other`，sourceClass `other`，errorName `TypeError`，insecure false，parentLine 1900，sourceLineLength 0，keywordAtColumn false，stackShape `other`，flags 0，categoryClass `content-javascript`，receiverState `unknown`，receiverId `uncollected`。class 名来自采集器对消息形状的分类，不是已经观测到的空接收者。源行长度是 0，这一列不是标识符。不是 `HTMLFormElement.submit` 的第 1 行第 75507 列。

`_out_of_file_slow_script` 对这张回执返回空。`_host_evidence_gate` 返回 `verify_host_execution`，`turnGate=blocked`，约束含 `no-new-host-surface`，没有 `one-host-behavior`。直接调用门没有改磁盘盖章。

回归 7 个测试，4.586 秒，通过。完成轴未写。facts revision 53。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 仍是 false。`experimentHygiene` 仍是 `ok`。没有证书 document POST，也没有同租约回读。
