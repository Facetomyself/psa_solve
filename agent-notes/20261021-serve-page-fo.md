# 投放页面主机 /fo/ 明文

本拍先跑 `web_case.py next`。动作是 `repair_submit_host_behavior`，`turnGate=blocked`。在已经投放的 `api.js`、`/cert` 和斜杠数 16 的 iframe 文档之外，只多投放观察轮 `rt_20261005125421_1d84c46dcd` 里第一条仍被挡住、并且排在 iframe 文档之前的正文。baseline 仍是 `blockUnmapped=true`。没有改 `ruyidom.js`，没有把 `form` 加进 Node `host-dom.js`，没有打开 `__watchEval`，没有改脚本预算，没有恢复 pad eval。

投放规则：POST，主机 `www.psacard.com`，问号前斜杠数为 10，路径以 `/cdn-cgi/challenge-platform/h/b/fo/` 开头。正文是 `diagnostics/shadowroot-repair-20261020/fo-page-plain.txt`，sha256 `a6cb98f21b563de898d6d296d5cb9c69cef6a398330da0565f74b269b740b4e8`，106880 字节，`text/plain; charset=UTF-8`，truncated 为 false，最大字节 122。这是该形状在观察轮索引第 3 条。cloudflare 主机上的 `/fo/` 以及后来的 `text/html` 响应没有投放。匹配不抄路径里的三段值。

发出的 `write_probe` 经 Node `--check` 通过。抽出的处理函数覆盖 14 个形状，页面 `/fo/` POST 命中这份明文，GET、斜杠数不足、cloudflare 主机返回空。先前的编排脚本、`api.js`、`/cert` 和 iframe 规则仍命中。

scope 重签为 `2827dd8dcdb91042ffe8e31029255445cc8d2f5edbc7c1113f798e2d0bf53a44`。runner 哈希已变，依赖增加 `foPage`。Gecko 五份锁定哈希未变。上一回 `18857b7aaa70419b8a37547841d02290` 和 scope `bbb6ae5e84a975adc9b49cf3f9212cf6574fc791bdf1baf0d4249a448849d225` 留在 priorScope。`load_scope` 通过后才跑。

官方 baseline `6ac768b641ed4a30aee4fcfd51c752e3`：status failed，exitCode 1，timedOut false，墙钟约 22.7 秒。失败原因是执行未成功完成。raw 只有 `host-diagnostic` 和 `summary`。诊断行是第 1 行第 1337365 列，matched false，base 为 object。side 的 kind 是 `other`，class 是 `slow-script`，sourceClass 是 `other`，sourceForm 是 `token`。没有 `host-observation`。raw 里证书 document POST 是 0 行。这列没有写成观察。调用点仍是第 75507 列。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。
