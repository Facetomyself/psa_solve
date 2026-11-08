# 补环境完成规划（web-reverse 方法论）

Case: `psa-cf-5s-shield-20260815`

当前阻塞：`_cf_chl_opt.yQYB9` 应为求解回调函数，RuyiDOM 引擎里为 object
（ID 状态机 case '5' 调用 `yQYB9?.call(IG)` 失败，orchestrate 源码 180073）。

按 SKILL.md 纪律：每轮一个明确缺口、双条件依据（browser fact 证明真实使用
+ local fact 证明缺失）、environmentPatchGate 只允许外部宿主面、禁止
VM/opcode/bytecode 内部 patch、禁止字节集 diff。RuyiDOM 引擎执行层优先
（第 0 步已采用）。

## Phase 1：yQYB9 赋值历史捕获（1-2 轮）

**方法**：wrapper 在 403 页 init 之前对 `window._cf_chl_opt` 定义赋值观测
（defineProperty setter 记录每次整体赋值与字段级赋值）。

- 403 页 init 设置 18 字段（首次赋值）
- orchestrate line 1 补充到 33 字段（二次字段赋值）
- **观测 yQYB9 的赋值次数与类型**：若只有一次 object 赋值 → 函数注册段
  从未执行；若两次 → 注册段执行但被覆盖/回退。

**判定**：`window._cf_chl_opt` 是外部宿主面（window 全局）——setter 观测
属外部宿主面插桩，合规。

**证据**：赋值时间线（次数/类型/调用栈近似位置）写入 analysis-progress.md。

## Phase 2：yQYB9 函数注册段定位（2-3 轮）

**方法**：静态定位 orchestrate 内给 `_cf_chl_opt` 赋值的全部代码段。

- 已知 T 表 919 键 = "_cf_chl_opt"（插桩解码已确认）
- 搜 `T[rf(...)][rf(...)]=function` 模式（180073 之前的字段补充/注册段）
- 与 403 页 init 的 18 字段对照：33 字段中哪些是 orchestrate 补充的

**判定**：注册段是否在环境条件分支内。若分支条件依赖宿主探测（如
performance/画布/音频某项返回值）→ 该条件是"外部宿主面可补"缺口；
若依赖引擎不可复现状态 → 记录穷尽性证据（SKILL.md 判据），转路线。

## Phase 3：单变量补丁 + 复跑（1-2 轮）

按 SKILL.md：一次只补一个缺口，补后重跑 RuyiDOM 观察推进。

- 每轮：改 wrapper → ruyidom_run → 记录 case '5' 前后状态变化
- native toString 保护（如补的是函数形态）
- 不补 VM/opcode/WASM 内部（runProgram 的字节码不动）

## Phase 4：提交链闭合（2-3 轮）

case '5' 通过后：

1. 提交请求出现（XHR 或 navigation——bXxEG="navigation" 提示是导航提交）
2. 导航提交在 RuyiDOM 里：allowNetwork=true 时真实导航（location 赋值
   或 form submit）→ CF 服务器验证
3. 观测 cf_clearance 下发 → 引擎内闭环

## Phase 5：交付验收

- 引擎成功 ≠ serverAccepted：vanilla test.py 用引擎生成结果真实请求验证
- 落地方式按 `docs/web-reverse-landing.md` 矩阵声明（纯算/补环境/V8 RPC）
- 更新 landing/method.json + parity 记录

## 决策门（Phase 2 之后）

若 Phase 2 证明 yQYB9 注册依赖引擎不可复现的宿主状态（穷尽性证据）→
转 triage 路线 B（浏览器求解器注入 cf_clearance）。判定标准：
具体缺口项 + 对应接口 + 为什么外部宿主面不可表达。

## 执行顺序与预计轮次

| Phase | 轮次 | 工具 |
|-------|------|------|
| 1 赋值历史 | 1-2 | RuyiDOM wrapper setter |
| 2 注册段定位 | 2-3 | 静态搜索 + 插桩解码 |
| 3 单变量补丁 | 1-2 | RuyiDOM 复跑 |
| 4 提交闭合 | 2-3 | allowNetwork + 观测 |
| 5 验收 | 1 | vanilla test.py |

预计 7-11 轮可收敛或触发决策门。

## 2026-10-03 通过当前卡点的执行顺序

合同层已修复：`migrate-contracts --case-class challenge` 已到 revision 2，RuyiTrace pointer 已切到 `rt_20260929103550_341b734038`，`web_case.py validate` 通过。当前 `next` 仍返回 `refuse_host_enumeration / turnGate=blocked`，这是有意保留的实验卫生闸门。

### 推荐路线：先恢复生产采集

1. 由真实 Firefox browser-worker 打开 fresh challenge，让页面自然完成 `form → cert document POST`；RuyiTrace 只作为 browser fact 和验收记录，不作为生产 collector 的运行时输入。
2. 求解会话与采集会话分离。只在同一 IP、UA、TLS 画像下交接经过验收的 cookie 状态，禁止回放另一 run 的 `/fo/` body、token 或 `Set-Cookie` 中间态。
3. 沿同一 lease 等待约 5 秒，记录独立业务 readback 200；只有这个结果才写 `serverAccepted=true`。

### 研究路线：继续 RuyiDOM 纯补环境

1. 先拿新的、同一 session 的外部边界证据，不能重复 causal-observer claim，也不能继续枚举相邻 getter。
2. 诊断面只保留 `window._cf_chl_opt` / `KP` 注册、最后一次 `cf-chl-out` 消费和 `form/submit` 分支；不改 VM/opcode/bytecode，不重放历史响应。
3. 只有 browser fact 证明某个外部宿主行为、本地事实证明该行为缺失时，才把 `environmentPatchGate` 置为 `ready`，一次只补一个 surface；必须看到 request boundary 移到 cert document 后再做 parity 与 readback。

没有新的 boundary evidence 前，继续试 `__clickTs`、9 KB 差值、`eb/managed` 或相邻 host getter 都不会越过闸门。

## 纯 Node 交付专项

当前 Node trace 的事实边界是 `Iw → IF → TypeError`；它没有 FO request/response，所以这不是“缺一个 form API”的阶段。下一轮应先做 runtime 设施和 trace 能力补齐：独立 `vm` realm、动态 script/iframe/Worker/message、XHR/fetch response 生命周期、cookie writer、timer/microtask、PerformanceObserver/resource entries。Node `global` 不得继续直接暴露给 target。

设置审计已完成：前三轮确实漏开了 `get/has/reflect/source/raw`。`param-complete` run `v8-20261003100221-c54ooe` 已捕获 `_cf_chl_opt → yQYB9 → performance → getEntries → undefined → TypeError`，因此第一单变量候选是 `performance.getEntries`。先从 RuyiDOM/Firefox 事实提取 entries 的字段、对象身份、时序和 descriptor，再做 Node native-like patch；不能直接返回空数组。只有该 patch 让 IF 越过并继续到新的 boundary，才进入下一个 surface；看到五段 FO 和 response callback 后再进入 form/document 和 parity。

当前性能与资源 canary 已证明：同 fresh source 下 `getEntries()`、`top`、`classList`、动态 selector/insert，以及真实 `turnstile-api.js` 执行都能逐层推进；`getEntriesByType` 也已接通。下一刀不是再补 DOM，而是建立 source-aligned cross-realm mirror 观测，确认 `runProgram/eval` 是否生成 `PQak3`，以及它是否写入 Window/global。禁止将 `PQak3` 直接补成函数。

### 新增：iframe realm 证据后的下一刀

RuyiTrace 的 Turnstile iframe HTML inline script 不是 API 壳的同义词：它有 238636 bytes，并包含 `PQak3/xdiN1/runProgram`。Node frame canary 已能执行这段脚本并触发 `PQak3` 读取，但仍没有 define；下一阶段必须迁移独立 iframe `vm.Context`、`parent/postMessage`、真实 DOM query/innerText、XHR response callback 与 FO response 驱动的动态脚本。禁止把 iframe 的 `PQak3` 读取直接补成 `window.PQak3`，也禁止回放 RuyiTrace 的 opaque FO body。验收仍保持 `requestBoundaryAligned=false`、`serverAccepted=false`。

本轮已把独立 iframe `vm.Context` 放进生产 `runtime/run.js frame`（离线）。结果 `frameEval=ok`、`chlOptKeys=37`、`framePqOwn=false`、`framePqType=undefined`、`throwName=TypeError`、`sendCount=0`、`boundary=boundary-unchanged`。`PQak3` 仍无真实 define。下一步不是 postMessage 投递或假 DOM，而是停在这个 TypeError，直到有新的 constructor 或 response 边界事实。验收布尔不改。证据：`agent-notes/20261003-node-iframe-realm.md`。

## 2026-10-05 trace decision update

fresh Firefox provenance run `rt_20261005125421_1d84c46dcd` 已提供所需 browser fact：Turnstile `attachShadow` receiver 为 `HTMLDivElement`，challenge iframe receiver 为 `HTMLBodyElement`，并观察到 `HTMLFormElement.submit → cert document POST 200`。因此不再把 Node 诊断中的 `HTMLScriptElement.attachShadow` 当作补丁目标。

Chromium 暂不重复采集。当前允许的下一步是从已有新 run 做窄 detail 解码和 source/identity receipt，先解决 source hash 与旧 local 不一致及 trace 覆盖限制；不自动进入 Node canary、baseline 替换或浏览器 readback。Node 求解链完成后才做同 lease 独立验收。详细限制见 `agent-notes/trace-compare-20261005.md`。
