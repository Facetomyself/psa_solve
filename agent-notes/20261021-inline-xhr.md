# 2026-10-21 XHR 在 send 返回前完成

`web_case.py next` 对回执 `92cee734930148c198f0cbc0f6f72def` 仍是 `repair_submit_host_behavior`，`turnGate=blocked`。这一拍没有再跑 `next`。

编排脚本里 `XMLHttpRequest` 出现 1 次。资源加载器对命中和被挡的 XHR 都用 `setTimeout(0)` 才把 `readyState` 写成 4。同一次脚本里的等待看不到这个回调，看门狗会停在脚本末列。这一处只改 helper：`installInlineXHR` 在 `send` 返回前调用已有的资源处理，并用 `xhrCompletion` 写 readyState、status 和正文。有处理结果且状态大于 0 时保留该状态，缺状态时用 200；空结果时状态为 0。已安装的 `onreadystatechange`、`onload`、`onerror` 会在返回前被调用。脚本时限仍是 13。真 eval 保留。`__watchEval` 没有打开。采集器、`ruyidom.js`、Node `host-dom.js` 没有改。

helper sha256 `9952fc4e39464c8da2e6adccfa2cd21811259b6d74f725d64aba881c4e12eba7`。scope `c9650afd06bd8048aa51d5419504e7fa95f6f6f7813e662b5f18e7bde08285c2`。priorScope 是 `e2916aec1bfc487d`，其中 baseline 是 `92cee734930148c198f0cbc0f6f72def`。Gecko 五份锁定哈希未变。`load_scope` 通过。

已发布测试 6 项通过：`xhrCompletion` 从 helper 源码抽出，6 个样本与预期状态一致；`performance.now`、真 eval 和源文件外慢脚本门仍在。

官方 baseline `8232a2dac3cd46b8a795d876420ce020`：status failed，exitCode 1，timedOut false，墙钟约 22.7 秒。raw 只有 `host-diagnostic` 和 `summary`。诊断是第 1 行第 1337365 列，matched false，base 为 object。side 的 kind 是 `other`，class 是 `slow-script`，sourceClass 是 `other`，sourceForm 是 `token`。`getEntries` 仍是 function。没有 `host-observation`。证书 document POST 是 0。这列没有写成观察。调用点仍是第 75507 列。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。
