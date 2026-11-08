# 2026-09-28 ruyidom_run 纠正轮

Case: `psa-cf-5s-shield-20260815`

## 入口

- 2026-08-15 到达 fo/eb 的记录在 `ruyidom_cf_shield_v1.js`，该文件含 opcode 插桩，本轮不跑。
- `ruyidom_min_debug.js` 不采集 wire，并写死 `tmp/pageHtml-repro.html`，不能当 fo 入口。
- 使用现有 `diagnostics/ruyidom_runner.js`。`codeJsPath` 设为不存在的 `diagnostics/NO_NODE_CODE_JS`（`codeJsPath_exists=false`）。runner 自己的 try/catch 把读失败当成空脚本，因此没有注入 `runtime/code.js`。没有改 runner 源码。
- CLI：`tools/ruyidom/run.ps1`，无 `-AllowNetwork`。未开浏览器，未 capture，未走 Node/v8trace。

## 输入

- 过期材料 `challenge-material/demo6-20260816-222208-3`
- html sha256/16 `e6a266a9d9b0d161`，orchestrate sha256/16 `437c1820aeaaba6f`
- 无 cookie。`pumpMs=15000`。页面 URL 只用 cert 路径。

## 观察（两件事分开）

- 未放行网络：exit `2147483651`，stdout 0 行。stderr 为 `FATAL ERROR: Non-local network connections are disabled`，连接目标是 `www.psacard.com`，不是 `/cdn-cgi/challenge-platform/`。
- 未观察到 fo/eb：stdout 没有 wire JSON；stderr 中 `/fo/`=0、`/eb/`=0。进程在 `print` 之前被页面源站连接打死，所以不能说求解器没有构造 fo，只能说本轮没有边界记录。
- 第一个外部错误：`about:blank line 1447 > injectedScript, line 2: SecurityError: The operation is insecure`。上一轮的 `require is not defined` 没有再出现。
- 过期材料，不是 fresh challenge，不能写成 serverAccepted。

## 结论

没有到达可引用的 fo/eb。缺口在外部文档上下文（about:blank 上的 SecurityError）以及未放行的页面源站连接，不是 VM opcode。
