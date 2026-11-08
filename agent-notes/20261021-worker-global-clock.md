# Worker 全局装上挑战 Date

2026-10-21。`repair_submit_host_behavior`，`turnGate=blocked`。同一 scope 只改了一处宿主行为：没有 document、并且带 `importScripts` 的全局，调用已有的 `installSandboxClock`。没有改页面 `performance`，没有再给文档沙箱装 `performance.now`。没有改 XHR、脚本时限、采集器或 `ruyidom.js`。时限仍是 13。真 eval 仍在。`__watchEval` 没有打开。没有写完成轴。

上一回官方 baseline `b841fe67bcbd47f8982e21bfbfbdcc02` 把沙箱 `performance` 对齐后，诊断仍是第 1 行第 1337365 列，raw 与 `b882fe520cb24afeaebd7bae4649a1ed` 字节相同。填充 eval 的文本本身不调用宿主 API。探针里每次大 eval 旁边有一次 `Date.now`。Worker 全局没有 document，原先在装挑战 `Date` 之前返回。

`test_shipped_worker_global_date_uses_challenge_clock` 从已发布 helper 抽出 `installWorkerGlobalClock` 并调用它。有 `importScripts` 的对象在页面选项出现后，`Date.now` 锚到秒字段；没有 `importScripts` 的对象不换 `Date`。已有 `sandbox-installed` 标记在安装失败时保留。输出 `worker-date-ok 13`。`test_shipped_sandbox_date_constructor_uses_challenge_clock` 仍是 `sandbox-date-ok 20`。

helper sha256 `2d1afb24f9708bb6c27baff7807e40c97d129b9fc2c40c07283403116fb1039a`。scope `089d6963ae6a5bae61d7fca6c9b5baab6127b3fabcc2649459a0e50a084ef93c`。priorScope 是 `5ec1558628e5f801`，其中 baseline 是 `b841fe67bcbd47f8982e21bfbfbdcc02`。runner sha256 仍是 `31746c03fd9890d48317faec1e2aa5ff5f99c7d63e0ce27c87b0956a5fa54d8a`。geckoLib 仍是 `9f21705d909f5e5c11bcf06af2187be7446b2112974090a3981e04a3cd11ce61`。`load_scope` 通过后才跑。

官方 baseline `d3ec59e2583f4bd1ab800fdaca77792c`：status=failed，exitCode=1，timedOut=false，墙钟约 19.708s。失败原因是执行未成功完成。stdout 与 stderr 长度都是 0。raw 只有一行 `summary`，ok 为 false，47 字节。与上一回 225 字节不同。执行目录没有 `submit-host-side.json`。诊断目录里的 iframe 侧记时间早于这次运行，不是这次写出的。因此这次没有慢脚本列，也没有 `perfAligned` 或 `clockAnchor` 的新侧记。没有 host-diagnostic，没有 host-observation。

没有证书 document POST 行，也没有同租约回读行。调用点仍是第 75507 列。这次不能把列号写成 1337365，也不能写成已经离开填充 eval。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。
