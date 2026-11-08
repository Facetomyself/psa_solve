# 投放 turnstile iframe 文档

本拍是 `repair_submit_host_behavior`，`turnGate=blocked`。在已经投放的斜杠数 7 的 `api.js` 和斜杠数 3 的 `/cert` 之外，只多投放一条早期 iframe 文档。baseline 仍是 `blockUnmapped=true`。其它 URL 继续返回空。没有改 `ruyidom.js`，没有把 `form` 加进 Node `host-dom.js`，没有打开 `__watchEval`，没有改 `dom.max_script_run_time`，没有恢复 pad eval。

投放规则：GET，主机以 `cloudflare.com` 结尾，问号前斜杠数为 16，路径以 `/cdn-cgi/challenge-platform/h/b/turnstile/` 开头并以 `/new/normal` 结尾。正文是 `diagnostics/shadowroot-repair-20261020/turnstile-iframe.html`，sha256 `4f73fec288f4e19c44ea54403ff35f95443e9ed28a15d184e04b1a0e6e5446d0`，258319 字节，`text/html; charset=UTF-8`。来自观察轮 `rt_20261005125421_1d84c46dcd` 的早期包，truncated 为 false。匹配不抄查询值。

发出的 `write_probe` 经 Node `--check` 通过。抽出的处理函数覆盖 10 个形状：编排脚本、带查询的 `api.js`、过短的 `api.js`、`/cert`、证书文档路径、斜杠数 16 的 iframe、斜杠数不足的近邻、该 iframe 的 POST、favicon。命中分别是对应正文或空。

scope 重签为 `bbb6ae5e84a975adc9b49cf3f9212cf6574fc791bdf1baf0d4249a448849d225`。runner 哈希已变，依赖增加 `turnstileFrame`。Gecko 五份锁定哈希未变。上一回 `9014e236de8844068e0f79723e16246a` 和 scope `07cbb17b2b5b5f0135549f52bca6f7db00c92470da2d5f52843911f882cba2d4` 留在 priorScope。`load_scope` 通过后才跑。

官方 baseline `18857b7aaa70419b8a37547841d02290`：status failed，exitCode 1，timedOut false，墙钟约 22.7 秒。失败原因是执行未成功完成。raw 只有 `host-diagnostic` 和 `summary`。诊断行是第 1 行第 1337364 列，matched false，base 为 object。side 的 kind 是 `other`，class 是 `slow-script`，sourceClass 是 `other`，sourceForm 是 `token`。没有 `host-observation`。raw 里证书 document POST 是 0 行。这列没有写成观察。调用点仍是第 75507 列。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。
