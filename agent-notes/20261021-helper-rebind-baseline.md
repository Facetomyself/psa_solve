# helper 重绑后的正式 baseline

2026-10-21。本拍盖章是 `verify_host_scope`，`turnGate=blocked`，约束含 `no-new-host-surface`。没有改 helper、采集器、`web_case.py` 或 Node 环境。没有调用 `create_scope`。

磁盘上的 helper 摘要已是 `faff9c5239ffd0a1fd821f201a8a18f3c9a474712ae4135ce6db29d5efe70891`，scope 里仍写着 `2d1afb24f9708bb6`。重签时其余 runner、runtime、input、source、config 和依赖的路径与摘要都没有漂。helper 路径不变，只换成活文件摘要。新 scopeId 是 `2ff1f07db69c1c1179d38107dfc83404c8bcfd9812b0d721da06a187ba7e513c`。旧 state 整份嵌进 `priorScope`：scope `089d6963ae6a5bae61d7fca6c9b5baab6127b3fabcc2649459a0e50a084ef93c`，baseline `d3ec59e2583f4bd1ab800fdaca77792c`，execution sha `1ac7ebb0afc31c7c33895a0e80ce81c0eee76e2771496cd2059b07d240338140`。再往下仍是 scope `5ec1558628e5f8014ec1b9ccfe11f052648120fcaa9ce7b5b4aebef456621b69`。`load_scope` 通过，状态是 `issued`、执行表为空。

随后同一 scope 跑了官方 `host run --variant baseline --timeout 90`，没有 `--allow-network`。回执 `7e9d471ac9a34d5293ca66a8b58b448a`：status `failed`，exitCode 1，timedOut false，墙钟 22.712 秒。失败原因是进程没有成功完成。raw 225 字节，只有一条 `host-diagnostic`（matched false，第 1 行第 1337365 列）和一条 summary，`ok` 为 true。没有 `host-observation`，没有 wire、necko、resp 行。`submit-host-side.json` 245 字节已写出。`scriptError` 是 slow-script，kind `other`，sourceForm `token`，sourceClass `other`，行和列与 diagnostic 相同。stderr 里 FATAL 计数为 0。

绑定的 `submit-orchestrate.js` 第 1 行长 120793。第 1337365 列不在这行里面。按已装的门，源文件外且 sourceForm 为 token 的慢脚本会授权一次同 scope 修补。本拍约束仍是 `no-new-host-surface`，没有做那一处宿主行为。

没有证书 document POST，也没有同租约回读。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。
