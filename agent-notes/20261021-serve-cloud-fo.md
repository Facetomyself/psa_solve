# 投放 cloudflare /fo/ 明文

本拍先跑 `web_case.py next`。动作是 `repair_submit_host_behavior`，`turnGate=blocked`。在页面主机 `/fo/` 明文之外，只多投放观察轮 `rt_20261005125421_1d84c46dcd` 里下一条仍被挡住的正文。baseline 仍是 `blockUnmapped=true`。没有改 `ruyidom.js`，没有把 `form` 加进 Node `host-dom.js`，没有打开 `__watchEval`，没有改脚本预算，没有恢复 pad eval。

投放规则：POST，主机以 `cloudflare.com` 结尾，问号前斜杠数为 10，路径以 `/cdn-cgi/challenge-platform/h/b/fo/` 开头。正文是 `diagnostics/shadowroot-repair-20261020/fo-cloud-plain.txt`，sha256 `6947ce11be75a85fb13e66465fe1ebbe0f968dee87b28907d82d702362a2c37a`，798108 字节，`text/plain; charset=UTF-8`，truncated 为 false，最大字节 122。这是该形状在观察轮索引第 5 条。同形状更晚的 117968 字节明文和 6776 字节 HTML 没有投放。匹配不抄路径里的三段值。

这份正文大于单次 `read` 以前沿用的 262144 字节上限，所以同一处改动把 `readUtf8` 改成每段最多 65536 字节并拼到文件长度。更小的已投放文件仍整段读出。

发出的 `write_probe` 经 Node `--check` 通过。抽出的处理函数覆盖 15 个形状。cloudflare `/fo/` POST 命中这份明文，GET 返回空。页面主机 `/fo/`、编排脚本、`api.js`、`/cert` 和 iframe 规则仍命中。

scope 重签为 `7908e6c40b600a3648395d46c97a2be19fd58f43fe4bc3a1fe58554304f720c0`。runner 哈希已变，依赖增加 `foCloud`。Gecko 五份锁定哈希未变。上一回 `6ac768b641ed4a30aee4fcfd51c752e3` 和 scope `2827dd8dcdb91042ffe8e31029255445cc8d2f5edbc7c1113f798e2d0bf53a44` 留在 priorScope。`load_scope` 通过后才跑。

官方 baseline `da06f146a5734c08a52e1fd0ccf5c84e`：status failed，exitCode 1，timedOut false，墙钟约 22.7 秒。失败原因是执行未成功完成。raw 只有 `host-diagnostic` 和 `summary`。诊断行是第 1 行第 1337365 列，matched false，base 为 object。side 的 kind 是 `other`，class 是 `slow-script`，sourceClass 是 `other`，sourceForm 是 `token`。没有 `host-observation`。raw 里证书 document POST 是 0 行。这列没有写成观察。调用点仍是第 75507 列。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。
