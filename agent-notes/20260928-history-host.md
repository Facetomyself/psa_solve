# 2026-09-28 history 宿主包装

Case: `psa-cf-5s-shield-20260815`

## 改动

- 文件：`diagnostics/ruyidom_runner.js`
- 只注入 2026-08-15 已有的外部宿主包装：`history.replaceState` / `history.pushState` 在 SecurityError 时返回 `undefined`。
- 原包装没有 `toString` 保护，本轮不加。
- history 包装不调用 Storage，所以没有复制 Storage 原型包装。
- 没有复制 opcode、UpvLO0、ZHfDS6、日志或字节码重建。没有改 `runtime/code.js`。没有跑 `ruyidom_cf_shield_v1.js`。

## 跑法

- CLI `tools/ruyidom/run.ps1`，无 `-AllowNetwork`。
- `codeJsPath` 指向不存在的 `diagnostics/NO_NODE_CODE_JS`，Node `code.js` 未注入。
- 材料：过期 `challenge-material/demo6-20260816-222208-3`。无 cookie。`pumpMs=15000`。

## 观察

- exit `2147483651`。stdout 0 行，没有 wire JSON。
- fo 计数：未记录（stderr `/fo/`=0）。eb 计数：未记录（stderr `/eb/`=0）。
- 上一轮的 `SecurityError: The operation is insecure` 这次 stderr 里没有。
- 未放行网络是另一件事：`FATAL ERROR: Non-local network connections are disabled`，目标是 `www.psacard.com`，不是 challenge-platform。进程在 `print` 之前退出。按约束没有打开全网。
- 不能写 serverAccepted。

## 结论

history 包装已装上，SecurityError 不再出现在本轮 stderr。请求边界仍未落盘，因为页面源站连接先杀死了进程。
