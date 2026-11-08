# 2026-10-21 合成 performance.now

`web_case.py next` 已是 `repair_submit_host_behavior`，`turnGate=blocked`。这一拍没有再跑 `next`。

同一 scope 只改了 `document-principal.js` 的合成 `performance`。平台对象是空的，原先只有 `getEntries` 和 `getEntriesByType`。先前同停住类探针只读过一次 `now`。这一处加上数字 `timeOrigin`，以及 `monotonicNow`：用 `Date.now` 减去安装时的原点，负差记为 0。脚本时限仍是 13。真 eval 保留。`__watchEval` 没有打开。pad eval 没有恢复。采集器、`ruyidom.js`、Node `host-dom.js` 没有改。

helper sha256 `9229a975c2bb99c2465d1b8a7e2e34620d37c86d12c968cd740a3efd675c55de`。scope `e2916aec1bfc487dceb350eccf1fa51514663882f67e71642bcb2c622af62e5d`。priorScope 是 `7908e6c40b600a3648395d46c97a2be19fd58f43fe4bc3a1fe58554304f720c0`，其中 baseline 是 `da06f146a5734c08a52e1fd0ccf5c84e`。Gecko 五份锁定哈希未变。`load_scope` 通过。

已发布测试 6 项通过：`monotonicNow` 从 helper 源码抽出，样本 `0,0,40,0,0`；真 eval 与源文件外慢脚本门仍在。

官方 baseline `92cee734930148c198f0cbc0f6f72def`：status failed，exitCode 1，timedOut false，墙钟约 22.7 秒。raw 只有 `host-diagnostic` 和 `summary`。诊断是第 1 行第 1337365 列，matched false，base 为 object。side 的 kind 是 `other`，class 是 `slow-script`，sourceClass 是 `other`，sourceForm 是 `token`。`getEntries` 仍是 function。没有 `host-observation`。证书 document POST 是 0。这列没有写成观察。调用点仍是第 75507 列。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。
