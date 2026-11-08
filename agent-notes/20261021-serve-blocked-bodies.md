# 投放被挡脚本正文

本拍是 `repair_submit_host_behavior`，`turnGate=blocked`。只改了采集器的资源处理。baseline 仍是 `blockUnmapped=true`。其它 URL 继续返回空。没有把 `form` 加进 Node `host-dom.js`。没有打开 `__watchEval`，没有改 `dom.max_script_run_time`，没有恢复 pad eval。

投放两条：

- GET，主机以 `cloudflare.com` 结尾，路径以 `/api.js` 结尾，问号前斜杠数为 7。正文是 `diagnostics/live/turnstile-api.js`，sha256 `76763bb46224400a11af989831d62d06629aba6f67d50cac96afae4a590adf59`，86732 字节，`application/javascript`。与观察轮 `rt_20261005125421_1d84c46dcd` 的对应包哈希相同。
- GET，主机 `www.psacard.com`，路径 `/cert`，问号前斜杠数为 3。正文是 `diagnostics/shadowroot-repair-20261020/cert-root-extensionless.txt`，sha256 `e0c4492eb3128cbb0433cfa3554602bfb845bb75421efc0a791c3e94d201e4e0`，399 字节，`text/x-component`，truncated 为 false。这是该路径在同一观察轮里先出现的包。另一份 2036 字节、sha256 `43416b6f01ded155b8fc86b43d931b90fa9efb141944e1ad6dddc49b2b667e9b` 没有投放，区分它要抄查询值。

scope 重签为 `07cbb17b2b5b5f0135549f52bca6f7db00c92470da2d5f52843911f882cba2d4`。runner 哈希已变。Gecko 五份锁定哈希未变。上一回 `329f75aa9405418dbc6332d9af2780a8` 和更早的链留在 priorScope。`load_scope` 通过后才跑。

官方 baseline `9014e236de8844068e0f79723e16246a`：status failed，exitCode 1，timedOut false，墙钟约 22.7 秒。失败原因是执行未成功完成。raw 只有 `host-diagnostic` 和 `summary`。诊断行是第 1 行第 1337365 列，matched false，base 为 object。side 的 kind 是 `other`，class 是 `slow-script`，sourceClass 是 `other`，sourceForm 是 `token`。没有 `host-observation`。raw 里证书 document POST 是 0 行。这列没有写成观察。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。第 1337365 列的 eval 没有返回。
