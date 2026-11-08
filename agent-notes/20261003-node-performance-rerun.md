# Node performance entries 提取与重跑

日期：2026-10-03  
目标：验证 `performance.getEntries` 是否为 Node 首个可补宿主面，并沿单变量 canary 观察下一个边界。所有运行均 no-network、使用 `param-complete`，没有改基线 `v8trace_orchestrate_runner.js`、没有写 `serverAccepted`。

## 提取事实

来自 `agent-notes/20261003-performance-entries-fact.md` 和 Firefox 主 run：

- challenge orchestrate 调用 `Performance.getEntries()`，无参数，返回 Array。
- challenge 随后读取 `entryType`、`name`、`duration`、`requestStart`、`responseStart`、`responseEnd`、`transferSize`、`encodedBodySize`。
- `PerformanceObserver.observe(Object)` 与 `PerformanceObserverEntryList.getEntries() -> Array` 也真实发生。
- entry 元素、长度、timing 值、observer options、descriptor 和 prototype flags 未从脱敏 trace 恢复。

## Canary 顺序

| run | runner 增量 | 结果 |
|---|---|---|
| `v8-20261003111529-qeznxd` | `performance.getEntries() -> []`，`top` 未补 | `performanceGetEntriesCalls=1`；旧 `getEntries is not a function` 消失；下一边界为 `window.top.location`，之后 `null.classList` |
| `v8-20261003112439-lvq58g` | 加 `top = window` | `top.location` 错误消失；下一边界为 `.main-content/.main-wrapper` 查询结果的 `classList.add` |
| `v8-20261003112947-brzwm4` | 从 fresh HTML 提供 challenge 容器、`classList.contains` | `classList.add` 成为下一缺口 |
| `v8-20261003113333-kf3aaj` | 加 `classList.add` | 推进到动态 script/DOM 路径；缺 `insertBefore` / `firstElementChild` |
| `v8-20261003113705-ozl2lh` | 加 element insertion/selector 面 | 推进到 element `querySelectorAll` 返回空数组后的 `parentNode.insertBefore` |
| `v8-20261003114712-z4l6s5` | 加 element-level `querySelector/querySelectorAll` | 同一 parentNode 边界；表明 source 还会查询运行时生成的文案节点 |
| `v8-20261003115013-erm6yx` | 给所有 element 和查询节点加 `parentNode.insertBefore` | 仍有动态节点关系差异；不继续扩展通用 DOM |

以上 canary 的空 `getEntries` 只证明“方法存在后能越过首个 TypeError”，不是 parity 实现。未产生 FO/XHR/document boundary。

## Source 对齐发现

原始 Node runner 使用 `challenge-material/chl-page-orchestrate-fresh.js`，sha256 前缀 `CDC46F...`、229681 bytes；已有 RuyiDOM fresh 材料是 `challenge-material/rt_20260928061614_ee71af43b2/chl-page-orchestrate.js`，sha256 前缀 `AA2B09A...`、238694 bytes。旧 source canary 在 DOM 推进后抛 `WHtx4 is not defined`；切换到同一 fresh source 后对应变成 `PQak3 is not defined`。这证明 free identifier 结果受 source/runtime 版本影响，不能把 `WHtx4/PQak3` 直接当 host API 补丁。

## 当前判定

- V8Trace 配置和 `get` 通道正常；`performance.getEntries` 的首个缺口已被实跑验证。
- RuyiDOM/Firefox 证据支持 ResourceTiming/Observer 的行为合同，但不提供可直接回灌的 entry 数值。
- Node runner 仍缺真实页面 bootstrap、动态资源/VM 输出和完整 DOM realm；source 不锁同一 fresh material 时，后续 free identifier 结论无效。
- 当前仍无 FO request/response、cookie writer、form/document boundary；不可写 parity 或 server acceptance。

## 下一步

1. 将 Node 诊断输入固定为与 RuyiDOM browser fact 同一 fresh material/hash。
2. 不补 `WHtx4/PQak3` 常量或函数；先确认其是否由动态 `runProgram`/Turnstile 资源生成。
3. 纯 Node 运行时下一阶段应补资源加载/独立 realm/Worker 或动态 eval 证据，再回到 `performance` entries 的真实 resource ledger，而不是继续合成 selector 节点。

证据目录：

- `evidence/web/v8trace/v8-20261003111529-qeznxd/`
- `evidence/web/v8trace/v8-20261003112439-lvq58g/`
- `evidence/web/v8trace/v8-20261003112947-brzwm4/`
- `evidence/web/v8trace/v8-20261003113333-kf3aaj/`
- `evidence/web/v8trace/v8-20261003113705-ozl2lh/`
- `evidence/web/v8trace/v8-20261003114712-z4l6s5/`
- `evidence/web/v8trace/v8-20261003115013-erm6yx/`
- `evidence/web/v8trace/v8-20261003121849-1ykah1/`

## Continuation: source-aligned rerun

The matched-material runner uses:

- `challenge-material/rt_20260928061614_ee71af43b2/challenge-page.html` (`030a1607...`, 5798 bytes)
- `challenge-material/rt_20260928061614_ee71af43b2/chl-page-orchestrate.js` (`aa2b09a4...`, 238694 bytes)

Run `v8-20261003121849-1ykah1` used that source and still reached no FO boundary. Its later free identifier was `PQak3`, whereas the old 229681-byte source reported `WHtx4`; neither name appears as a declared symbol in the static source. This is source/context drift evidence, not authorization to invent a function. The RuyiDOM bridge records that the corresponding browser flow loads the orchestrate resource, Turnstile API resource, and mirrors cross-realm/window function registration before reaching three `/fo/` request shapes; the Node runner currently does none of those resource evaluations.

The latest canary copies also revealed a forced-exit artifact: the short async guard is only a diagnostic stop, so `targetExitCode=0` does not mean solve success. Those runs remain canary evidence only; no `localReproduced`, parity, or server acceptance was recorded.

## Continuation: Turnstile resource canary

`v8-20261003130747-4pwon9` evaluated the exact fresh `turnstile-api.js` resource after orchestrate. Its first resource-context failure was `HTMLScriptElement is not defined`; adding a minimal `HTMLScriptElement` realm type and a `document.currentScript.src` identity moved the resource to `turnstileEval=ok`.

`v8-20261003131931-dbzjwx` added `performance.getEntriesByType() -> []`; the first `getEntriesByType` failure disappeared. The canary still had no FO boundary and stopped in the same fresh orchestrate path at `PQak3 is not defined` (with the expected Worker canary error). This is now evidence that the resource API can execute in Node, while the remaining name is produced by a missing dynamic execution/context stage rather than by a missing `performance` method.

The canary remains diagnostic-only. It uses an explicit short async exit and an empty performance ledger, so `targetExitCode=0` is not solve success.

## Continuation: source-aligned Turnstile resource

- `v8-20261003130747-4pwon9`: evaluating the exact fresh `turnstile-api.js` first failed at `HTMLScriptElement is not defined`.
- After adding `HTMLScriptElement` and a current-script `src`, `v8-20261003131028-kt767g` reached `turnstileEval=ok`; the next failure was `performance.getEntriesByType is not a function`.
- After adding the same empty performance ledger method, `v8-20261003131931-dbzjwx` no longer failed on `getEntriesByType`; source execution still stopped at `PQak3 is not defined`.

The resource canary therefore proves Turnstile resource evaluation is possible in Node once its script identity is modeled. It does not prove the current `PQak3` value. RuyiDOM bridge evidence shows the missing next behavior is cross-realm/window mirror (`xdiN1`-style registration) before its three FO boundaries; do not hardcode `PQak3`.
