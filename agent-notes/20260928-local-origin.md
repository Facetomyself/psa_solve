# 2026-09-28 页面源站本地应答

Case: `psa-cf-5s-shield-20260815`

## 改动

- CLI 没有离线资源开关。`blockUnmapped` 只会拦截，不会把挑战页 HTML 交回去。
- 只改 `diagnostics/ruyidom_runner.js` 一处：请求路径去掉 query 后若等于内存里的 `challengeUrl` 路径，返回已读入的 `challengeHtml`（`text/html`，200）。
- wire 只记去掉 query 的路径。没有放行 `-AllowNetwork`，没有注入 Node `runtime/code.js`，没有改 opcode。

## 跑法

- `tools/ruyidom/run.ps1`，`pumpMs=15000`，`codeJsPath` 不存在。
- 材料：过期 `challenge-material/demo6-20260816-222208-3`。

## 观察

- exit `2147483651`。stdout 0 行，没有 wire JSON，所以看不到 `local-html` 是否命中。
- fo 计数：0（stderr `/fo/`=0）。eb 计数：0（stderr `/eb/`=0）。
- 下一跳仍是未放行外联。引擎只给出主机名 `www.psacard.com`，没有路径，也没有 query。路径模板只能记到主机，不能编造 path。
- 挑战页 HTML 里的绝对 URL 模板只有 `challenges.cloudflare.com`，不是这次 FATAL 的主机。因此打死进程的连接不是「与 challengeUrl 路径完全相同」的那一条，资源 handler 没机会把它留在本地。
- 不能写 serverAccepted。没有打开全网。

## 结论

本地 HTML 应答已加上，但这一轮仍在打印 wire 前死于 `www.psacard.com`。fo/eb 未落盘。
