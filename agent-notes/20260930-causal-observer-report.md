# Response → DOM causal observer（静态准备）

## 状态

`static-verified-not-authorized`。本轮未访问目标、未执行 RuyiDOM 目标脚本、未创建 claim、未修改 facts / receipt / 既有 runner。产物从锁定 clean bridge 派生，不复用已经消耗的 v2 claim，也不建立 v3 action/profile。

## 当前 active 候选：transport-fixed

后续主线默认候选已切到已审查的 stable transport source：

- source：`diagnostics/clean-baseline-20260930/ruyidom_bridge.stable-transport.js`
- source SHA-256：`a6f0e51a8b8c99019678a508385cc21f66fd3205e08c512d3ccc8888a32433d6`
- output：`diagnostics/causal-observer-transport-fixed/ruyidom_bridge.causal-observer.transport-fixed.js`
- output SHA-256：`52503fd09a64b307cc6fdae7a8417a096cd2b4df9ff2c47ce8e72e00f8d6f5d9`
- independent receipt：`agent-notes/20260930-causal-observer-transport-fixed-receipt.json`
- independent fixture：`agent-notes/20260930-causal-observer-transport-fixed-fixtures.json`

生成器新增 `--baseline`，allowlist 仅含 stable transport 与原 clean 两个已审查 hash；默认 stable 的 mode 为 `active-transport-fixed`。原 clean 必须显式传入，mode 固定为 `historical-synthetic-comparison-only`，不能作为 active fallback。未审查路径/hash 会直接拒绝。

transport-fixed source 到新 observer 仍严格是原来的 9 项诊断变换；`network.proxy.type=0` 在 source/output 中均恰好出现一次。新旧 causal observer 的全文 diff 只有这一行 proxy pref，证明 observer 合并没有删掉已验证修补，也没有夹带第二个 transport 变化。

新 active candidate 验证：outer / embedded / helper `node --check`、SHA-256 KAT、redaction fixture 均通过；source 86278 bytes，output 91202 bytes，仍只增加 4924 diagnostic bytes。该结果是静态组合验收，不等于 `stable-transport + causal observer` 已经 live 跑过目标。

## 产物

- 生成器：`agent-notes/20260930-causal-observer-build.py`
- observer：`diagnostics/causal-observer-20260930/ruyidom_bridge.causal-observer.js`
- 嵌入脚本静态展开：`diagnostics/causal-observer-20260930/ruyidom_bridge.causal-observer.embedded-syntax.js`
- 合成 helper fixture：`diagnostics/causal-observer-20260930/synthetic-helper-test.js`
- 机器回执：`agent-notes/20260930-causal-observer-receipt.json`
- fixture 摘要：`agent-notes/20260930-causal-observer-fixtures.json`

本节列出的 `causal-observer-20260930` 是保留的历史 clean 对照；当前 active 指针以上一节 transport-fixed 产物为准。

## 最小观察差异

保持原有顶层 `XMLHttpRequest`、`Document.write`、`innerHTML`、`Document.createElement`、`HTMLFormElement.submit` 包装及全部返回路径，只在调用原实现前后追加 bounded metadata：

1. clearance FO request：method、path class、body length、SHA-256。
2. 带 `cf-chl-out` 的 response：status、path class、response length、SHA-256。
3. `Document.write` / `innerHTML`：相对时刻、caller script class/function/line/column、参数 length/SHA-256/tag shape。
4. `createElement(form|h2|p|ol)` 与 `form.submit`：相对时刻和 caller。
5. pump 结束：最终 title / visible text 的脱敏文本、原文 length/SHA-256。URL、email、长 token、长数字序列在输出前替换；事件中不保存 request/response/DOM 参数原值。

所有事件最多 64 条，写入原 summary 的 `probe.causalTrace` / `probe.causalFinal`，因此真实 handoff 必须把既有 `tracePath` 绑定到 restricted evidence 目录。observer 本身不新增网络请求，不提供 body replay 或替换入口。

## 字节与 diff 证明

- clean source：86229 bytes，SHA-256 `32cef74e67164611750ac2870546a2a4283f8b519ec4756e3a8f949fa3c0cd94`
- output：91153 bytes，SHA-256 `9403ccc17eb77f5abca813582371c4927f66e51e334a77a93a29f5b4974acfb1`
- source 构建后 hash 不变；输出仅新增 4924 bytes。
- exact transform receipt 共 9 项：8 个单一 anchor replacement + 1 组 9 个 helper insertion；每项均记录 anchor/replacement SHA-256 与 bytes。
- unified diff：17 added / 8 removed lines，diff SHA-256 `51d8bf9400c30fec53edc92f085bdac8b05afc31895ef42c5fdd17dd59ed7c38`。
- diff 新增区已拒绝 `foResponseManifest`、foreign replay、`runProgram(`、opcode、debugger 标记；没有新增环境 getter、VM handler 或业务 patch。

机器真源以 `20260930-causal-observer-receipt.json` 为准；不要手工改 output 后沿用该 hash。

## 静态与合成验证

- Python generator `py_compile`：pass。
- outer runner `node --check`：pass。
- 展开的 page-realm embedded script `node --check`：pass。
- helper fixture `node --check` + 执行：pass；没有网络或目标代码。
- SHA-256 KAT：`sha256("abc")` 命中标准值。
- 合成序列：`request → response → document.write → createElement(h2)`，顺序/相对时间/caller/length/hash/tag shape 全部存在。
- 敏感 fixture 检查：URL、email、长 token 未出现在序列化结果；最终文案输出为 `{url}` / `{email}` / `{token}` / `{number}` 占位形式。

## 原生导航复用与执行入口缺口

observer 是 page-realm 观察逻辑，和材料由 urllib handoff 还是 RuyiDOM 原生 `fromURL/loadURI` 无绑定；可以复用到原生导航 baseline。若采用 direct navigation，必须由主线程把 exact observer hash 注入同一个 windowless browser 的 page realm，并保证 observer 先于目标 clearance branch 生效，不能重新引入 material/orchestrate response substitution。

当前没有合法执行入口：尚缺 reviewed claim / fixed argv、direct-navigation session provenance、observer 安装时序 receipt、restricted `tracePath` 绑定、expected facts revision 和一次性预算归属。若 governance 把入口差异归为 `session-state`，可走现有 `fix_session_provenance` 路由；不能借本产物绕过 `stop-search`，也不能把它登记成 v2 已授权 runner。

## 主线程审查清单

1. 对照 machine receipt 审查 9 个 exact edits 和 output SHA-256。
2. 决定使用 clean bridge 现有导航还是原生 `fromURL/loadURI`；后者不得再 fetch/replay challenge material。
3. claim 必须绑定 runtime hashes、observer hash、fresh session provenance、restricted trace path、固定 argv 和启动前 facts revision。
4. 只验收 causal chain：`FO request hash → response hash → first DOM branch → form/submit 或脱敏排障文案 → document POST`；没有业务 readback，仍不得写 `serverAccepted=true`。
