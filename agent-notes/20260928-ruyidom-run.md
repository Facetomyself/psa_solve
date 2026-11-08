# 2026-09-28 ruyidom_run（一轮）

Case: `psa-cf-5s-shield-20260815`

## 入口

- `ruyidom-mcp` 不在本会话已连接工具里（非冷启动）。没有调用 v8trace / Node。
- 同一 Gecko 引擎 CLI：`D:\reverse_ENV\tools\ruyidom\run.ps1 -Health -Json` → `ok=true`，`fatal=[]`，`runtimeProcessCount=0`，marker 存在。不是 engine-bound。
- 脚本：`diagnostics/ruyidom_runner.js`。`ruyidom_cf_shield_v1.js` 含 orchestrate opcode 插桩，本轮禁止执行。`runtime/run.js` 是 Node，未用。

## 输入（无 cookie）

- 材料目录：`challenge-material/demo6-20260816-222208-3`（2026-08-16，过期挑战页）
- html sha256/16 `e6a266a9d9b0d161`，5801 bytes
- orchestrate sha256/16 `437c1820aeaaba6f`，227853 bytes
- 注入 `runtime/code.js` sha256/16 `cdc85a2419c3927a`，3127 bytes
- `challengeUrl` 只用站点 cert 路径，`pumpMs=20000`，未加 `-AllowNetwork`

## 观察

- exit `2147483651`；stdout 0 行，没有 `{ok:...}`。
- fo 计数：未记录。eb 计数：未记录。请求边界未落盘。
- 第一个外部宿主/入口错误：`injectedScript` line 24 `ReferenceError: require is not defined`，对应 `runtime/code.js` 的 Node `require("./lib/config.js")`。
- 下一则：line 92 `SecurityError: The operation is insecure`。
- 随后 stderr：`FATAL ERROR: Non-local`（截断）。在禁止非本地连接时，runner 对 `challenge-platform` 返回 null（放行真实网络），进程在打印 wire 前被引擎打死。不能把这次 fatal 当成 fo/eb 已到达。
- 未写 cookie、token、指纹或代理。不能计 solve 成功或失败。

## 结论

材料过期，且这一轮没有可引用的 fo/eb 边界。第一个明确缺口是把 Node CJS `code.js` 注入 Gecko，不是 VM 内部 opcode。
