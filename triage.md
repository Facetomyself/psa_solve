# Triage

> **更新注记（2026-11-07）**：下文阻塞点（yQYB9 / form.submit）与候选路线属 2026-10-05 快照，已被后续进展取代：ruyijs 线生产化（`runtime/solve_ruyijs.py`，clearance 跨引擎转移成立）；Node 桥定性 capture-only（同字节下死于 FO r1 后第二层键控解码，f8 无界自旋）。当前权威状态见 `docs/status-20261107.md`。本文件保留作流程历史。

Case: `psa-cf-5s-shield-20260815`

## 结论等级

- Case 等级：`partial`（缺口链定位完成，求解未闭合）
- 深度：L3（运行时定位——插桩 + 三环境对照 + 源码级偏移）
- 未声称：任何"已复现求解"或"serverAccepted"

## 阻塞点

| 阻塞 | 定性 | 位置 |
|------|------|------|
| `_cf_chl_opt.yQYB9` 非函数（object） | execution-boundary（yQYB9 函数注册段被引擎环境分支跳过） | orchestrate 180073 ID 状态机 case '5' |

## 已验证事实（不重做）

1. 挑战形态：managed 强制（cType managed / cTplV 5 / cvId 3），无感自动通过（Turnstile non-interactive）
2. 提交链：fo flow 六段 URL 模板（Reqable 实抓）
3. 引擎缺口阶梯：Node（DOM 面大）< iv8（createElementNS）< RuyiDOM（yQYB9 注册链）
4. 引擎层三修复：meta CSP / history.replaceState / storage 包装（均有证据）

## 候选路线（下一步决策）

| 路线 | 成本 | 说明 |
|------|------|------|
| A. 继续定位 yQYB9 注册点 | 中 | 同插桩法（搜 `_cf_chl_opt` 键的赋值序列）；预计数轮 |
| B. 浏览器求解器注入 | 中 | 浏览器池解挑战拿 cf_clearance → 注入采集器会话；工程可行，绕过纯算 |
| C. iv8 深挖 | 低 | iv8 静默退出点定位（错误不抛，需逐步插桩）；API 面小于 RuyiDOM |

## 证据索引

- 浏览器事实：evidence/web/ruyitrace/rt_20260815060651_eb196ed770/（receipt integrity pass）
- v8trace：evidence/web/v8trace/v8-20260815070607-0a39cz/、v8-20260815071000-g8sotl/、v8-20260815075849-x7h32q/
- iv8：evidence/web/iv8/iv8-cf-probe-{1..8}/result.json
- 材料：challenge-material/（403 页 ×2、orchestrate 229KB、jsd 21KB）
- 求解器：ruyidom_cf_shield_v1.js（含全部插桩）、ruyidom_cf_bisect.js、v8trace_orchestrate_runner.js、iv8_cf_shield_probe.py

## 风险与限制

- orchestrate 混淆代码的插桩只读诊断（未改控制流，除 switch 语法错误已回退）
- 挑战材料（cH/cN）时间敏感，续作需重抓 fresh 页
- RuyiDOM runtime 是 hash 锁的课程材料，引擎本体不可改

## 2026-10-03 trace-gap 复核

### 当前结论

- Firefox/RuyiTrace 主 run：`rt_20260929103550_341b734038`，receipt/index 完整性通过，已覆盖 `403 → orchestrate → 5×FO → cf_clearance 名 → cert document POST 200`。
- Chromium/V8Trace `headed-20261003`：只读内核对照，能看到 `5×FO → form → cert Document POST 200`；capture `partial`、`baselineEligible=false`，关键 page-host FO body 缺失，不能登记为 browser fact。
- 本地 RuyiDOM：`forms=0`、`submits=0`、`certDocumentPostObserved=false`，在最后一次 `cf-chl-out` 后进入 `h2/p/ol` 诊断分支。
- 当前事实保持 `localReproduced=false`、`requestBoundaryAligned=false`、`serverAccepted=false`。证书 document POST 200 与 `cf_clearance` 名称都不等于业务 readback。

### 卡点定性

这是“采集边界 + 语义/执行边界 + 最终验收”叠加：Chromium 的关键响应正文和字段因果没有保存，patched Node 在 TypeError 前连 FO boundary 都没到；真正阻塞 Firefox 主线的是 RuyiDOM 对第五跳响应/envelope、`KP` 回调或 session 绑定的解释与真实 Gecko 不同。现有证据不支持把根因归成点击、通用 `HTMLFormElement` 缺失或某个未对齐的 9 KB 差值。

### 调度阻塞

合同已按 `challenge` 显式迁移到 revision 2，`migrate-contracts --check` 返回 `ready`。当前 `web_case.py next --preview` 已回到 `refuse_host_enumeration / turnGate=blocked`；剩下的是实验卫生闸门，不是合同元数据问题。

### 下一步

1. 保持 RuyiTrace 为唯一 browser fact，不新增宿主枚举、不二次 claim、不登记 Chromium browser fact。
2. 纯 RuyiDOM 路线只允许 fresh、同一 session 的 `KP/最后 cf-chl-out → form/submit` 一刀窄因果诊断；若目标是生产恢复，切到 Firefox browser-worker 求解与采集会话分离。
3. 本地出现 cert document POST 后，沿同一 lease 等约 5 秒记录独立 `business-readback`；只有该 readback 200 才能把 `serverAccepted` 置为 true。

详细证据：

- `agent-notes/20261003-firefox-trace-gap.md`
- `agent-notes/20261003-chromium-trace-gap.md`

## 纯 Node 补环境专项复核

### 目标修正

最终交付是 Node 纯补环境；Firefox/RuyiTrace 只提供 browser fact 和行为 oracle，不能成为 collector 依赖。Chromium 也只保留对照价值。

### Node 现状

- `v8-20261003021537-lhw7em` 以及三个旧 `challenge-fast` run 都在 `Iw → IF → TypeError` 停止，request boundary 为 0。
- throw 前 `yQYB9` 被写成 `JSArray`，但 trace 没记录真实 property、receiver、descriptor、参数、返回值或注册来源；不能直接把它补成函数。
- `v8trace_orchestrate_runner.js` 是 stub：`window=self=global`、`createElement` 固定为 `SCRIPT`、XHR/fetch 没有真实 response 生命周期、Worker 直接抛错、动态 script/iframe/PerformanceObserver/resource entries/cross-realm message 都缺失。
- 39 个 miss 混有 `__ruyiXhr`、Node 环境变量、Node global leak 和算法名称噪声，不能逐项试 getter。

### 为什么现在不会完成

Node 尚未具备三个必要前提：同一 fresh challenge 的 canonical input；动态资源/跨 realm/异步 callback 的浏览器执行面；真实五段 FO 的 request→response→cookie→DOM 分支。RuyiDOM 的 `3488/noform` 只能说明响应/session 分支不同，不能给 Node 一个可回灌的 body 或 clearance。

### 下一刀

1. 用同一 fresh epoch 固定 HTML、orchestrate、Turnstile resource、URL/ray、UA、Cookie/Storage、clock/randomness 和输出规范。
2. Node 独立 `vm` realm，先恢复动态 script/iframe/Worker/message；不要把 Node `global` 直接暴露给 challenge。
3. 跑窄 `param-env` trace，围绕 `IF` 记录未知 receiver 的 property/descriptor/参数/返回/异常；若仍是 timer 黑洞，再单独跑 `callback-chain`。
4. 补齐 XHR/fetch response、cookie writer、redirect、timer/microtask、PerformanceObserver/resource entries 后，先让 Node 真实到达 FO boundary，再做单 surface patch。
5. Node 自然出现 form/document POST 后，才产出 parity 并跑独立 5 秒业务 readback。

`param-env` canary `v8-20261003093112-o9509m`（1411 records）与 `callback-chain` canary `v8-20261003093211-o37wfl`（1448 records）已复现同一边界；随后 `param-complete` run `v8-20261003100221-c54ooe`（33291 records）打开 `get/has/reflect/source/raw` 后捕获到：`_cf_chl_opt → yQYB9 → performance → getEntries → undefined → TypeError`。当前第一候选 external-host surface 已收敛为 `performance.getEntries`，但必须先按 RuyiDOM/Firefox 事实补齐 entry shape、时序和 descriptor。

当前不能做：硬改 `yQYB9`、回放 RuyiDOM 的 `fo` body、合成 `cf_clearance`、把 `3488/3792` 当分数、用 `eb/managed` 或相邻 getter 继续枚举。

## Performance 提取与 Node 重跑状态

- Firefox/RuyiTrace 已证实 `performance.getEntries()` 返回 Array，challenge 读取 ResourceTiming 字段，并使用 `PerformanceObserver`；原始 entry 值/options/descriptor 不可从脱敏 receipt 恢复。
- Node `v8-20261003111529-qeznxd` 的 `getEntries()` canary 实际调用一次并越过旧 TypeError；增加 `top=window`、challenge 容器 `classList`、动态 DOM 节点关系后，边界持续推进，但仍没有 FO request/response。
- 旧 runner source 与 RuyiDOM fresh source 不同：`229681` bytes vs `238694` bytes。旧 source 后续报 `WHtx4`，匹配 fresh source 后报 `PQak3`；两者都不能直接当 host API 补丁，先锁 source/context 并恢复动态资源/VM 输出。
- 所有 canary 都是独立副本，不改 `environmentPatchGate`、不写 `serverAccepted`。详细证据：`agent-notes/20261003-performance-entries-fact.md`、`agent-notes/20261003-node-performance-rerun.md`。

动态上下文结论：fresh source 的 `PQak3` 只有一次静态引用且无声明，旧 source 对应 `WHtx4`；Turnstile resource canary 已 `turnstileEval=ok`，因此不是单纯 resource export 或 Performance API 缺口。高置信下一面是 `runProgram/eval` 生成值与 Window/global mirror 的 realm 绑定；记录 source hash、eval/Function、return class、define/read 和 descriptor，禁止直接写 `window.PQak3`。

新增证据：RuyiTrace 的 Turnstile iframe HTML inline script（238636 bytes）本身包含 `PQak3/xdiN1/runProgram`。Node frame canary `v8-20261003152520-xgv5ln` 执行该脚本并把 `_cf_chl_opt` 从 21 推到 37，随后真实读取 `PQak3`，但 `framePqOwn=false`；补 `parent.postMessage`、`innerText/querySelector` 只改变后续 TypeError，不产生该 binding。当前卡点是 iframe 独立 realm、message/DOM 生命周期以及 FO response 驱动的动态上下文，不能继续按相邻 host getter 枚举。

## 2026-10-03 生产 iframe realm

- `runtime/run.js frame` 已用独立 iframe `vm.Context` 跑同一 script：`frameEval=ok`，`chlOptKeys=37`，`framePqOwn=false`，`throwName=TypeError`，`sendCount=0`。
- `boundary=boundary-unchanged`。`PQak3` 无真实 define。不要接着补 postMessage 投递或假元素。
- 阻塞：constructor TypeError 与 canary 的 DOM/状态 TypeError 同名，没有新异常名，也没有 FO。gate 保持 false。
- 证据：`agent-notes/20261003-node-iframe-realm.md`。

## 2026-10-05 Firefox receiver provenance

- 新鲜 run `rt_20261005125421_1d84c46dcd` 使用窄 `jscall-detail`/native detail，receipt integrity pass，395 artifacts，1,352,457 indexed records。
- 浏览器事实：Turnstile API 的 `attachShadow` receiver=`HTMLDivElement`；challenge iframe 的 receiver=`HTMLBodyElement`；没有 `HTMLScriptElement.attachShadow`。Node realm probe 的 `HTMLScriptElement` 记录不能映射为真实浏览器缺口。
- 同一 run 观察到 `HTMLFormElement.submit`，随后 cert document `POST 200`；这补齐了 browser-side submit boundary，但仍不是 `serverAccepted`。
- 继续保持 `localReproduced=false`、`requestBoundaryAligned=false`、`serverAccepted=false`。独立同 lease 约 5 秒业务 readback 仍缺；Chromium 不再重复采集普通 hooks。
- 证据：`agent-notes/firefox-receiver-provenance-20261005.md`。

对照修正：同 run body/div 来源 identity 链已证，但 iframe source hash 与历史 local 不同。iframe complete=false；JSCall dropped_gate=611，17函数达到1024阈值，sources_unavailable=3。submit 与 POST 是时序证据，POST 无 source context，不能升级为完整 correlation。只读对照见 `agent-notes/trace-compare-20261005.md`；保持 blocked，不执行 canary。
