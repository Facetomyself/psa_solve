# PQak3 / xdiN1 受限 RuyiDOM 事实（2026-10-03）

## 运行边界

- 复用了既有 `diagnostics/ruyidom_bridge.js`，未修改 orchestrate、bridge 源码或业务合同；fresh input 固定为 `rt_20260928061614_ee71af43b2` 的 HTML/orchestrate，并映射已落盘 Turnstile API。
- `liveNetwork=false`、无 `foResponseManifest`、未导入 Cookie；RuyiDOM `run.ps1` 未使用 `-AllowNetwork`。运行输入：`agent-notes/20261003-pqak3-input.json`，SHA-256 `b087fd3da312df157e1f7ed18ae2c267212c118c99f959e3f79d29d6127e7c0e`。
- bridge trace：`agent-notes/20261003-pqak3-bridge.jsonl`，SHA-256 `8d8b326bfa7e414dd211f24286f2bf15152e51168dc8b07cd0666c92a8678a6b`；既有 bridge SHA-256 `ce5bfbeecc44a70fa1d6e435084b1cf1e229ec1ea6e67dce7cbf8ac6b8f25e70`。
- 本轮 `counts.orchestrate=1`、Turnstile script served、`fo=0`、`eb=0`、`errors=[]`；页面因离线资源/`SessionStoreFunctions.sys.mjs` 处于不完整执行态，不能把退出/无错误当作 solve 通过。

## 实际观测

| 对象 | 能证明的事实 | 未证明的事实 |
|---|---|---|
| `xdiN1` | bridge summary `probe.xdi="function"`、`probe.xdiWin="function"`；即 target global lookup 与 `window.xdiN1` lookup 都拿到 function 类别 | `hasOwnProperty`、descriptor、prototype/constructor、跨 realm SameObject、`xdiN1.toString()` 原文/Native hash 均未输出；`probe.srcToString=true` 只针对 `HTMLScriptElement.src` getter，不是 xdiN1 |
| `PQak3` | 本轮没有 `PQak3` error、define、get 或 call 记录 | 未到 `eY`/PQak3 路径，故 type、own-property、descriptor、producer、return shape 全部未知 |
| `eY` | 现有 bridge 没有 eY enter/return hook | 无法证明 eY 调用前后是否发生 PQak3 define/read |
| `KP` 对照 | `probe.kp="undefined"`、`kpOwn=false` | 不能用 KP 结果代替 PQak3 事实 |

`lookupRing` 仅有 `remote:0`、`fission:0`、`proc:0`、`principal:about:blank`、`dbg-type:function`、点击/指针等待；没有 `globalHas`/`sameWin`/`isGlobal`/`winProp` 行。`debugThrow` 的现有实现只在旧的 `K7` + 固定 column `88637` 条件命中时读取 `KP/Kz/xdiN1` descriptor；该条件不适配 fresh source，本轮没有进入。

## 结论

这轮只确认了 bridge 已见的 `xdiN1` function 类别和 target/window 两个 lookup 结果，**没有**确认 PQak3 动态定义或 eY 读写。阻塞不是“PQak3 不存在”，而是现有 bridge 的调试点绑定旧 source/function，且本轮离线执行在进入 challenge 动态路径前停住；不能据此硬编码 `window.PQak3` 或把 `xdiN1` 的 function 类型当成完整跨 realm 合同。

## 最小可行观测位置（不改目标脚本）

1. **Gecko/RuyiDOM**：复制 bridge 仅改诊断 hook，不改页面 HTML/orchestrate。把 `debugThrow` 的旧 `K7/column` 改为 fresh source SHA + `eY`/PQak3 source-offset 区间；`Debugger.onNewGlobalObject` 为每个 realm attach，`onEnterFrame/onPop` 记录 eY caller、`PQak3` lexical/global lookup、return/throw。
2. 每次 eY frame 只输出脱敏字段：`realmId`、`scriptHash/sourceSite`、`PQak3` `hasOwn`、descriptor key/flags、value `typeof/class/constructor`、`Function.prototype.toString` hash/length、`eO` arg shape、return `typeof/class/length`；不落源码、密文、cookie 或原始 byte。
3. 对 `xdiN1` 在每个 global 读取 `getOwnPropertyDescriptor`，并记录 `global===window`、value class、descriptor flags、toString hash；在 mirror assignment 前后各记一行。只有出现 define→eY/PQak3 read→继续执行才算 discriminator。
4. **Node 最小对照**：沿同 fresh source 的 canary 记录 eval/Function source hash+return class、runProgram call/return class、global define events 和 realm identity；没有 define 就查闭包/VM return，不换相邻 host getter。

## 证据路径

- 本轮 trace/input：`agent-notes/20261003-pqak3-bridge.jsonl`、`agent-notes/20261003-pqak3-input.json`
- fresh material：`challenge-material/rt_20260928061614_ee71af43b2/`
- 既有 source-aligned Node 结论：`agent-notes/20261003-node-dynamic-context.md`、`agent-notes/20261003-node-performance-rerun.md`
- 既有 RuyiDOM bridge mirror 事实：`agent-notes/20260928-ruyidom-bridge.md`
