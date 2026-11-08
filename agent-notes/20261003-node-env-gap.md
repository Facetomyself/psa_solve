# Node / V8Trace 首个执行边界与补环境缺口

日期：2026-10-03  
Case：`psa-cf-5s-shield-20260815`  
目标：按“最终纯 Node、RuyiDOM 仅中间态”重新核对已有 Node 诊断证据。本轮只读，没有执行网络、没有改 runner、合同或业务事实。

## 输入与状态

- 当前 run：`v8-20261003021537-lhw7em`，`challenge-fast`，1421 records / 1679 events，trace index complete，目标退出码 1；`run.json` SHA-256：`9003cb44f263389daf1ace6d75b1ab0015393d7fa1d73e9766a78db169954fcf`。
- runner：`v8trace_orchestrate_runner.js`，SHA-256：`ae79d86334eac4ad78d1e9f4ed8d8aa5ece7e922add3704bf0806260a9686b13`。
- 当前合同 `contracts/workflow-artifacts.v1.json` 状态为 `blocked`；`environmentPatchGate.status=not-ready`、`patchCoverageIds=[]`、scope 仍是 `external-host-only`。`dynamicFields`、clocks/randomness、cookie/storage、resourceHash、output canonicalization 均未落合同。

## 首个真实执行边界

同步主函数没有失败，stdout 是 `{ok:true, chlOptKeys:21, xhrCount:0, xhrUrls:[]}`。真正的首个边界是 **异步 timer**：stderr 给出 `Timeout.Iw` → `IF`，随后抛出一次 `TypeError: T[rv(...)][rv(...)] is not a function`；堆栈没有进入 `XMLHttpRequest.open/send`、`fetch` 或任何 response/callback/resource 阶段。

throw 前最后一小段 target-side 写入是：对象槽 `yQYB9` 被设成一个数组，随后建立含 `navigation` 字符串的 obfuscated helper，紧接着抛错。`yQYB9` 是匿名内部对象上的数组属性，trace 没有给出它的宿主类型、descriptor 或调用关系；它不能被当成“缺少 `window.yQYB9`”或独立 external-host API，也不能直接拿来补。

静态 source 中同一 `IF` 函数的形状是 `T[obfuscated][obfuscated]()`，再 `new T[obfuscated](callback)`，最后对实例调用带 `entryTypes` 的方法；这看起来像 performance/observer/resource-timing 初始化，但名称映射和实际 receiver 没有被当前 trace 解析，故只能标为 **candidate**，不能把 `performance.getEntries` / `PerformanceObserver` 写成已证实的 first divergence。`request_summary.json` 明确是 `call_rows=0`、`send_count=0`、`reached_request_boundary=false`。

三个旧 run（`v8-20260815070607-0a39cz`、`v8-20260815071000-g8sotl`、`v8-20260815075849-x7h32q`）都在同一 TypeError 形态终止：1415/1418/1421 records，37/37/39 miss，1 throw，14 call，0 request boundary；不是一次偶发网络失败。

## runner 先天制造的 stub 边界

`v8trace_orchestrate_runner.js` 不是浏览器 runtime，而是把 challenge material 放进 Node 后注入一组极简对象：

- `window=self=global`，直接把 Node global 暴露给 target；`document`、`navigator`、`location`、`history`、storage、screen、timer、observer 等均为普通 JS stub。
- `document.createElement` 无论 tag 都返回同一种 `SCRIPT` 形状；query/getter 返回 `null` 或空数组，element 的 append/remove/event/style 行为基本 no-op；`submit` 只写一个全局 flag，不做 navigation。
- `XMLHttpRequest` 只有 `open/send/setRequestHeader/addEventListener/abort` 的本地记录器，没有 readyState、status、response、responseText、responseURL、事件时序、response headers 或异步回调；`fetch` 直接返回空 body 的假 200。
- `performance` 仅有 `now/timing`，没有 resource entries/observer；`Worker` 直接 throw；`Blob`、`FileReader` 没有可用行为；crypto、URL、atob/btoa 和 Node timers 混在同一 realm。

所以当前 run 能证明“这套 stub + Node realm 在异步 callback 处终止”，不能证明某一个真实浏览器 API 的 descriptor、prototype、toString、异常面或返回值已经对齐。

## trace 是否漏掉决定补环境的宿主行为

是。profile 虽然写了 `envcall/request/throw`，但实际 envcall 只有 `*`、`Object.keys`、`performance.now`、`setInterval`、`setTimeout` 等极少数记录；没有 `Document.createElement`、XHR/fetch response、DOM callback、observer/resource entry、Worker message、realm/prototype 或 descriptor 级的 call/return。`callback-chain`、`worker-message`、source-level host call 也没有形成可用证据。

可见的 miss 不能直接当补丁清单：`__ruyiXhr` 是 runner 在打印结果时读取自己尚未创建的数组；`USERPROFILE`、`NODE_PATH`、`FORCE_COLOR`、`TIMER` 和大量算法名称是 Node 内部模块噪声；`global` leak 反而证明 runner 把 Node 特征暴露给了 target。trace 没有记录 `T[rv(...)][rv(...)]` 的真实 property 名、receiver 类型、参数或返回值，因此没有足够证据决定是 performance observer、某个 DOM method，还是其他内部分支。

## external-host 与不可推断项

**可以列为 runner 明确欠建模的 external-host 面（待浏览器事实确认）**：DOM/element shape 与 realm、XHR 完整生命周期和 response、fetch Promise/response、timer/microtask 与异步 callback、performance entries/observer、Worker/Blob/FileReader、history/location/cookie/storage、crypto subtle 的参数/返回/异常面。这是“stub 形状不足”的目录，不等于本次 trace 已证明每一面被访问。

**当前 trace 不能推断**：`yQYB9` 的真实语义；TypeError 对应的解码 property 名；哪一个 host surface 是 first divergence；`eb`、`cf_clearance`、FO body 或 form data；任何 VM handler/opcode/bytecode/WASM 内部逻辑；以及是否能由 Node 直接完成最终 server acceptance。没有 request boundary，也没有 response/callback/resource realm 证据，不能从 39 个 miss 里挑一个值硬补。

## 纯 Node 下一刀（最小 trace 配置）

1. 复用同一 fresh material，但把下一轮从宽泛 `challenge-fast` 收窄到 **`param-env`**，保留 `throw_detail/context` 和 source/stack；先不扩 host 面、不打开 network。若 timer 后仍只有异步黑洞，再单独跑一轮 **`callback-chain`**，不要把两轮合成一个大 trace。
2. 只围绕 `IF` 的未知 receiver 建一份 call/return/throw 事实：记录 property 名（脱敏 hash 即可）、receiver 的 constructor/prototype/descriptor、参数签名、返回类型和异常；候选的 performance/observer 只在这份事实与 browser evidence 对齐后才可补。
3. 目标 host adapter 每轮只做一个 surface，并保留 native-like `toString`、descriptor 和 exception parity。第一轮不要补 `yQYB9`、Node `global`、crypto algorithm 名或任何 VM/解释器 handler；也不要把 XHR/fetch 当成“已到达”，因为本轮明确没有 request boundary。
4. 只有 Node runner 真正产生 FO request/response、异步 callback 和 form/document boundary 后，才进入 Python/TLS parity 与业务 readback；当前合同的 `environmentPatchGate` 仍未 ready，纯 Node 最终 runtime 目标需要后续单独更新交付合同，不能由本诊断 run 越过。

## 证据路径

- `D:\reverse_ENV\workspace\psa_solve\v8trace_orchestrate_runner.js`
- `D:\reverse_ENV\workspace\psa_solve\evidence\web\v8trace\v8-20261003021537-lhw7em\run.json`
- `D:\reverse_ENV\workspace\psa_solve\evidence\web\v8trace\v8-20261003021537-lhw7em\analysis\round_summary.json`
- `D:\reverse_ENV\workspace\psa_solve\evidence\web\v8trace\v8-20261003021537-lhw7em\analysis\request_summary.json`
- `D:\reverse_ENV\workspace\psa_solve\evidence\web\v8trace\v8-20261003021537-lhw7em\v8trace\index.jsonl`
- `D:\reverse_ENV\workspace\psa_solve\contracts\workflow-artifacts.v1.json`

结论：Node 当前首个真实边界是 `Iw → IF` 的异步 TypeError，`yQYB9` 只是抛错前的内部数组写入；trace 在决定性 host call/return、response、callback 和 realm 事实处存在盲区。现阶段最多能提出“external-host stub 形状不足”的候选目录，不能从现有 run 选出一个可验收补丁或宣称纯 Node 已接近 FO。

## 2026-10-03 本地 canary 复核

按 `web-reverse/references/v8trace-fact-driven-patching.md` 的闭环，只用仓库 CLI、锁定 patched Node 和现有 runner；没有 `allowNetwork` 或外部连接。

### `param-env`

命令（PowerShell，exit 0；目标脚本仍以 targetExitCode 1 收口）：

```text
& "D:\reverse_ENV\tools\node\node.exe" "D:\reverse_ENV\mcp\v8trace-mcp\dist\cli.js" run --project "D:\reverse_ENV\workspace\psa_solve" --case "psa-cf-5s-shield-20260815" --script "D:\reverse_ENV\workspace\psa_solve\v8trace_orchestrate_runner.js" --profile param-env --allow-failure --cwd "D:\reverse_ENV\workspace\psa_solve"
```

run `v8-20261003093112-o9509m`：1411 records / 1669 events，runtime verification 和 patched-node diagnostic gate 通过，`request call_rows=0`、`send_count=0`、worker=0、callback=0。首个 blocker 仍是 `TypeError`，raw index 行 1386；envcall 只有 Node `net.open`、`*`、`Object.keys`、`now`、`setInterval`、`setTimeout`。它没有给出 IF 未知 receiver 的 property、参数或返回值。

### `callback-chain`

命令同上，profile 改为 `callback-chain`；PowerShell exit 0，目标脚本仍以 targetExitCode 1 收口。

run `v8-20261003093211-o37wfl`：1448 records / 1706 events，raw index 行 1423 仍是同一 TypeError。`callback` 事实只确认 timer callback `callback#2` 已 register+enter（execution sites `85:48963` 与 `85:138447`），没有 callback exit/throw、没有 request/worker/response/resource 事实；另外 3 个 callback 只注册未进入。该轮证明了异步入口，但没有补上 IF 内的 host call boundary。

结论：两轮 canary 都能安全复现同一失败，第一补丁仍不可选。`param-env` / `callback-chain` 只把 timer 进入点定位得更清楚，不能把 `yQYB9`、Node `net.open` 或 crypto algorithm miss 提升成 external-host patch。下一刀需要在不改当前 runner 的前提下，另取同版本 browser fact 对照未知 `T[...]` receiver 的真实 API/descriptor；否则继续加 Node stub 仍是猜测。

新增证据：

- `D:\reverse_ENV\workspace\psa_solve\evidence\web\v8trace\v8-20261003093112-o9509m\analysis\round_summary.json`（SHA-256 `e733685f0e440584605eaff0a5a7da5b1f61f3807dd65eaa63fa2584f22a4491`）
- `D:\reverse_ENV\workspace\psa_solve\evidence\web\v8trace\v8-20261003093112-o9509m\analysis\ai_facts.md`
- `D:\reverse_ENV\workspace\psa_solve\evidence\web\v8trace\v8-20261003093211-o37wfl\analysis\round_summary.json`（SHA-256 `42eb591cc3ea38359f14ef7105dbf658713917a48ee71af6e3d6c9a1c7216173`）
- `D:\reverse_ENV\workspace\psa_solve\evidence\web\v8trace\v8-20261003093211-o37wfl\analysis\ai_facts.md`
