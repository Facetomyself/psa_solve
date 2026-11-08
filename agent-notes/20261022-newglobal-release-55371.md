# 2026-10-22 清掉新全局调试器后仍停在第 55371 列

2026-10-21T22:15:40Z 的决定是 `repair_submit_host_behavior`，`turnGate=blocked`。约束是 `tool-evidence-required`、`ai-notes-are-not-facts`、`same-scope`、`submit-callsite-only`、`one-host-behavior`、`no-completion-facts`、`goal-incomplete-does-not-override`。原因点名源文件内第 1 行第 55371 列，调用点仍是第 1 行第 75507 列。

这一列是解释器 `for` 头上的 1 字母局部量。循环体 1381 个记号里，名单上的名字只有 `return` 1 次和 `break` 68 次。循环里 71 处调用指向同一个别名，顺着赋值走四层没有落到名单上的宿主名，也没有函数体。没有把这个局部量装成全局，没有改 13 秒时限，没有改 helper，没有改 VM。

已经放开的调试器仍留着 `onNewGlobalObject`，那个钩子会把之后新建的全局再加成 debuggee。这一处只在 `j5` 与 `jj` 的观察都结束后清掉这个钩子，再 `removeAllDebuggees`。helper sha256 仍是 `6ad5ffb19ea7d746588f7ac4a8e604c8bb9c5bb8b98895f62455b4822eed0a0d`。runner sha256 `97b70fb57f0ca6cdd5496c4b70fd7fef8f2378973ca28a96b9ae13c0b3079ce4`。scope 重签为 `614ff6bf72def2d56c26e6f5e3d992dfb0ed75eaf204d6fb9d034ded03037f8f`。上一张 `60e8a133a4f912d098d3422113413d315940e20f5ac9ce41724f673e7aa8c5a5` 与 baseline `bf38ae972145403d83164eae108e4bf3` 留在 priorScope。

官方 baseline `a11a7f0a2c1c4b8290fd25d9b2f57048`：pid 26812，耗时 22722460000 ns，exitCode 1，timedOut false。执行 sha256 `cd47b8c4f60d84dee10757f9e9ebb110874bbd6d586178b81711077766306e87`。诊断仍是第 1 行第 55371 列，kind `other`，class `slow-script`，sourceForm `token`，sourceClass `other`。`debuggee`=`released`，`j5Entries`=2，`jjEntries`=2。raw sha256 `731459ca7fda730ce26ddc27e4f3ef3736d0a3128466f0f987eb3c994773f2b9`，223 字节。side sha256 `ca42cb1f2f5e1f4b580c8b2c47052778518131c836d755800f8eb5421d8f22b3`，640 字节。这两份哈希与 `bf38ae97` 相同。事件仍是 `host-diagnostic` 和 `summary`，matched false。没有证书 document POST，也没有同租约回读。完成轴保持 false。写这条时磁盘盖章仍是 `2026-10-21T22:15:40Z`。随后对这张回执跑了 `next`，新盖章是 `2026-10-21T22:35:48Z`。那一拍的记录在 `agent-notes/20261022-55371-no-callee.md`。
