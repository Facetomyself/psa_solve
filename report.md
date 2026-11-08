# PSA Cloudflare 5s 盾无感求解 — 逆向分析报告

> **更新注记（2026-11-07）**：本报告为 2026-08-15 快照（`partial`：缺口链定位完成、求解未闭合）。此后状态已两次跃迁：ruyijs 线生产化（clearance 跨引擎转移成立，`partial` → 生产线可用）；Node 桥定性 capture-only（不收敛根因 = FO r1 后第二层键控解码，详见 `docs/status-20261107.md` §3）。本文保留作历史里程碑，结论以 `docs/status-20261107.md` 为准。

## 基本信息

| 项目 | 值 |
|------|-----|
| 目标 | PSA（www.psacard.com）Cloudflare managed challenge（5s 盾）无感求解 |
| 目标形态 | 403 challenge 页 + orchestrate 混淆 JS（229KB）+ 内嵌 VM（runProgram） |
| 分析时间 | 2026-08-15 |
| 分析深度 | L3（运行时定位） |
| 状态 | `partial`（缺口链定位完成，求解未闭合） |

## 目标概述

PSA 站点对无 cf_clearance 的客户端强制 Cloudflare managed challenge（"Just a
moment..." 5s 盾），采集器（curl_cffi）无 JS 求解能力导致 91-92% 请求被
mitigation。本 case 目标：在真实 Gecko 引擎（RuyiDOM）中执行 challenge 求解
JS（orchestrate），自动生成挑战提交并获取 cf_clearance，不触发交互式
Turnstile。

## 关键发现

### 发现 1: 挑战链完整形态（Reqable 真实浏览器抓包）

- **位置**: 浏览器访问 cert 页全请求序列
- **描述**: 当前 PSA 无感挑战 = Turnstile non-interactive 自动通过。提交链：
  403 挑战页 → orchestrate 加载 → 两次 `fo` POST（psacard.com +
  challenges.cloudflare.com）→ POST /cert 带求解结果 → 200 真实页。
- **证据**: 提交 URL 模板 `/cdn-cgi/challenge-platform/h/g/fo/{id}:{ts}:{hash}/{ray}/{token}`；`__cf_bm` 两段刷新；`cf_clearance` 求解后下发
- **置信度**: `high`

### 发现 2: 三环境缺口阶梯

- **位置**: Node（v8trace）/ iv8 / RuyiDOM 三环境执行 orchestrate 对照
- **描述**: 同一缺口链在三环境的不同深度断裂：
  - Node：`document.createElementNS` 等 DOM 缺口面过大（逐桩补齐不现实）
  - iv8：实测 `document.createElementNS`=undefined，修桩后静默退出
  - RuyiDOM：走最远（createElementNS ×3 + createElement ×41），崩于
    `_cf_chl_opt.yQYB9?.call(IG)`
- **证据**: iv8 domPanel 实测；RuyiDOM wrapper hook 计数；v8trace throw_context
- **置信度**: `high`

### 发现 3: IG.call 精确定位（插桩解码）

- **位置**: orchestrate 源码 180073（ID 状态机）case '5'
- **描述**: `T['_cf_chl_opt']['yQYB9']?.['call'](IG)`——yQYB9 应为求解回调
  函数，引擎里为 object（注册步骤被更早的环境分支跳过）
- **证据**: 用混淆器自身解码函数 rv 插桩输出 `_cf_chl_opt,yQYB9`；引擎
  实测 `typeof yQYB9 === "object"`；CDP 实测真实浏览器挑战后
  `_cf_chl_opt` 整体清除（求解期临时状态）
- **置信度**: `high`

### 发现 4: CF 规则升级时间线

- **位置**: 8 月 9 日（旧 trace）×5 vs 8 月 15 日（新 trace）
- **描述**: 8 月 9 日主文档全部直接 200、零 cf-mitigated 标记；8 月 15 日
  强制 managed challenge。同出口浏览器能过（1.1s 求解）、curl 被硬拦——
  判定维度是客户端 JS 求解能力，不是出口 IP
- **证据**: rt_20260809* 5 个 run 的 http_packet 全 ABSENT vs 新 trace 的
  cf-mitigated 响应
- **置信度**: `high`

## 架构概览

```
403 challenge 页（_cf_chl_opt 配置：cH/cN/cRay/cType=managed/cTplV=5）
  └─ init script（内联，nonce）
       └─ 动态加载 orchestrate（challenge-platform/h/g/orchestrate/chl_page/v1?ray=...）
            ├─ 字段初始化（_cf_chl_opt 18→33 字段）
            ├─ Pv：SVG 指纹元素创建（createElementNS + setAttribute cx/cy/r=15 + path d）
            ├─ IF：performance.getEntries 遍历 + PerformanceObserver 注册
            ├─ ID：entry 处理状态机（switch 字节码）
            │     case '5'：_cf_chl_opt.yQYB9.call(entry)
            └─ runProgram：内嵌 VM 执行器（加密字节码求解核心）
```

## 核心逻辑分析

### 求解链各阶段（RuyiDOM 插桩实测）

| 阶段 | 引擎状态 | 证据 |
|------|---------|------|
| 字段初始化 | ✅ 33 字段 | cfChlOptKeys |
| Pv SVG 指纹 | ✅ ×3 createElementNS | lastTag="path" |
| IF 性能采样 | ✅ getEntries/PerformanceObserver/ID 均 function | 插桩解码 |
| ID case '5' | ❌ yQYB9 为 object 非函数 | yqType="object" |
| 提交 | ❌ 未到达 | xhr=[] |

### 缺口根因假设

yQYB9 的函数注册（orchestrate 内部 `_cf_chl_opt[键]=函数` 的赋值段）在引擎
环境被更早的分支条件跳过。注册点未定位（下一步工作）。

## 环境与工具

- 浏览器证据：RuyiTrace 2.5.5 / Firefox 155（rt_20260815060651_eb196ed770，
  index/receipt integrity pass）
- 引擎执行：RuyiDOM gecko-xpcshell（Firefox 135 base，hash 锁）
- 本地诊断：v8trace patched Node 20.19.0（challenge-fast，1415 records）
- 快速验证：iv8 Community Edition 0.1.4（离线 V8 + DOM 仿真）
- 抓包对照：Reqable（用户浏览器真实提交链）
- CDP：js-reverse-mcp（调试 Chrome 9222，断点窗口不足未用）

## 结论

- `localReproduced` / `transportAdmission` / `serverAccepted`: 均未达
- 落地方式候选：浏览器求解器注入 cf_clearance（工程可行路径）
- 剩余工作：定位 yQYB9 函数注册点（orchestrate 内部，同插桩法可继续）

## 2026-10-03 Chromium / Firefox trace 卡点复核

本轮把 Chromium/V8Trace 和 Firefox/RuyiTrace 分开核对。两条 trace 都证明了挑战链的部分外部形状，但没有形成可交付的“求解器闭环”：浏览器侧的 HTTP 200、`cf_clearance` cookie 名称和证书页 POST 200，都不能替代同一 lease 的业务 readback 200。

### Firefox / RuyiTrace：采集完整，执行语义仍断

主证据 `rt_20260929103550_341b734038` 的 runtime、index、receipt 均通过，且完整记录了 `cert GET 403 → orchestrate GET 200 → 5×FO POST 200 → 最后 page-host FO 出现 `cf-chl-out`/`cf-chl-out-s` 与 `cf_clearance` 名 → cert document POST 200`。这说明 Firefox 真实浏览器能够进入 form/证书导航分支，卡点不在 trace 丢包。

本地 RuyiDOM 对同类响应仍落到 `noform` 诊断分支：`forms=0`、`submits=0`、`certDocumentPostObserved=false`，当前 `localReproduced=false`、`requestBoundaryAligned=false`、`serverAccepted=false`。因此根因定性为响应/envelope、`KP` 回调或 session 绑定相关的语义/执行边界，不能再把它简化成缺少 `HTMLFormElement` 或点击事件。

`eb/managed=0` 是本轮 Firefox 事实，当前 h/b 通过链不依赖它；旧合同若仍要求 `eb`，也不能拿 `jsd/oneshot` 代替。证书 document POST 200 仍不是独立的业务 readback。

### Chromium / V8Trace：只能作内核对照

`headed-20261003` 只读 capture 证明有头 Chrome 能走 `5×FO → form → cert Document POST 200`，但完整性为 `partial`、`baselineEligible=false`，关键 page-host FO body 不可取，未生成 receipt，也未登记 browser fact。第 3/4 跳约 9 KB 的请求差没有字段级对齐依据，不能归因给点击或某个 getter；`HTMLFormElement.submit` 也没有安装有效 hook。

patched Node V8Trace 在 TypeError 前终止，只有 stub DOM miss 和 `node:net open`，没有 FO/XHR/Document request boundary，不能反推 Gecko 补丁。Chromium 证据因此只能说明“另一内核存在 form 分支”，不能给出本地 noform 分支的响应语义因果，也不能证明 `cf_clearance` 值或业务接受。

### 当前卡点与下一刀

当前是三层卡点叠加：Chromium 采集完整性不足、Node 诊断执行过早退出、Firefox/RuyiDOM 在第五跳响应后发生语义分叉。合同闸门已按 `challenge` 显式迁移到 revision 2，`migrate-contracts --check` 已返回 `ready`。迁移后 `web_case.py next --preview` 重新回到 `refuse_host_enumeration / turnGate=blocked`；现在的阻塞是实验卫生闸门，不再是合同元数据问题。

下一刀保持 RuyiTrace 为唯一 browser fact，停在 `refuse_host_enumeration` / `stop-search`。要继续纯 RuyiDOM 路线，必须先拿到一份新的、同一 session 的外部边界证据，再只窄切最后一次 `cf-chl-out` 的 `KP/回调注册 → 响应解码 → form/submit` 因果；不回放另一 run 的 FO body，不手造 cookie/token/body，不枚举相邻 getter。若目标是尽快恢复生产采集，则切到 Firefox browser-worker 求解与采集会话分离的路线，先在浏览器自然完成 form/证书导航，再把经过验收的会话状态交给采集器。无论哪条路线，只有同一 lease 约 5 秒业务 readback 200 才能回填 `serverAccepted`。

详细切片证据：

- `agent-notes/20261003-firefox-trace-gap.md`
- `agent-notes/20261003-chromium-trace-gap.md`

## 纯 Node 补环境目标复核

用户目标确认为：Node 纯补环境交付，RuyiDOM 只做 Gecko 中间态和行为 oracle。按这个目标，当前失败不是“再补几个 DOM getter”就能解决，而是 Node runner 还没有走到可补环境的真实边界。

### 当前 Node trace 能证明什么

`v8-20261003021537-lhw7em` 与三个旧 `challenge-fast` run 都在同一类异步边界停止：`Iw → IF → TypeError: T[rv(...)][rv(...)] is not a function`。最新 run 的 throw 前确实把匿名对象的 `yQYB9` 槽写成数组，并随后写入 `bXxEG="navigation"`；这只能证明当前 Node 输入/运行时里的值形状不满足调用要求，不能证明 `yQYB9` 就是一个应该直接补成函数的 external-host API。

当前 run 没有 `XMLHttpRequest.open/send`、`fetch` response、Worker message、DOM callback、form/document boundary，也没有同一 session 的 FO response。`request_summary` 明确 `send_count=0`、`reached_request_boundary=false`。因此这份 trace 只能定位“stub/realm 在异步 callback 前终止”，还不能选择第一处可验收补丁。

### Trace 的决定性缺口

`v8trace_orchestrate_runner.js` 把 Node global 直接当 `window`，把 `document.createElement` 固定成同一种 `SCRIPT` 桩；XHR 没有 `readyState/status/response/responseText/response headers` 和异步事件，`fetch` 永远返回空 body 的假 200，`Worker` 直接抛错，动态 script、iframe、Blob、FileReader、PerformanceObserver、resource entries 和跨 realm `postMessage` 都没有真实执行面。这个 runner 甚至没有执行完整的页面 bootstrap/resource loader，只把 `_cf_chl_opt` 字面量和 orchestrate 直接 `eval`。

所以 trace 里看到的 `__ruyiXhr`、`USERPROFILE`、`NODE_PATH`、Node `global` leak、算法名称等 miss 不能直接变成补丁清单；它们混有 runner 自身和 Node 内部噪声。当前 profile 也没有记录未知调用的真实 property 名、receiver/prototype/descriptor、参数、返回值和 callback 因果。

### RuyiDOM 能交给 Node 的内容

RuyiDOM 能迁移的是行为合同：五段 FO 的角色和顺序、method/status/header-name 类、Cookie 名谱系、pre-FO 的 UUID/performance/RTC/iframe 调用顺序，以及 `cf-chl-out` 响应后进入 form 或 `h2/p/ol` 的分支形状。不能迁移的是 `cf_clearance`、`__cf_bm`、FO body、3488/3792 opaque response、Firefox profile 或异会话 replay。

本地 `3488/noform` 因此是 response/session 输入分支缺口，不是缺 `HTMLFormElement`。Node 当前连 response boundary 都没有，不能用 RuyiDOM 的 noform 结果直接指导 Node 补一个 form API。

### 纯 Node 的正确收敛顺序

1. **先锁 canonical input**：同一 fresh epoch 保存 challenge HTML、orchestrate、Turnstile resource hash、URL/ray/UA、Cookie/Storage 初始状态、clock/randomness 和输出 canonicalization；这些字段目前还没有完整写入 `workflow-artifacts`。
2. **重建 Node runtime 边界**：独立 `vm` realm，不把 Node `global` 暴露给 target；实现动态 script/iframe/Worker 的加载和消息闭环，先让 `KP/yQYB9` 的赋值历史可观察。
3. **补完整异步 Web API**：XHR/fetch response 生命周期、cookie writer→egress、redirect、timer/microtask、PerformanceObserver/resource entries、crypto 参数/异常面；每轮只验证一个 surface，不能先硬改 `yQYB9`。
4. **补请求响应闭环**：Node 必须真实发出五段 FO 并消费同一 session 的响应，记录脱敏的 status/header-name/body length/hash 和 callback→DOM 分支；在此之前不要分析 form 或 `cf_clearance`。
5. **再做 parity/验收**：自然产生 form/document POST 后，才做独立 TLS 请求和约 5 秒 business readback。`serverAccepted` 只能由 readback 200 回填。

下一轮不再用 `param-env` 追未知 receiver；应以 `performance.getEntries` 为第一单变量补丁候选，先从 RuyiDOM/Firefox 事实提取返回集合的字段、对象身份、调用时序和 native-like descriptor，再在 Node runner 做同等最小实现并重跑 `param-complete`。若 boundary 仍不动，再进入下一个由新 trace 选出的 surface；不要把 `performance.getEntries` 直接写成空数组，也不要把现有其余 miss 逐个试成 getter。

这两轮 canary 已实际执行：`param-env` run `v8-20261003093112-o9509m`（1411 records）与 `callback-chain` run `v8-20261003093211-o37wfl`（1448 records）都在同一 `Iw → IF → TypeError` 停止；后者只看到 timer callback 注册/进入，仍没有 IF 内部 host call。随后补跑 `param-complete` run `v8-20261003100221-c54ooe`（33291 records），打开 `get/has/reflect/source/raw` 后已经捕获决定性链：`_cf_chl_opt → yQYB9 → performance → getEntries → undefined → TypeError`。当前第一候选 external-host surface 是 `performance.getEntries`，但返回 entry shape、时序和 descriptor 仍需按 Gecko 事实确认。再用显式 `--trace all --raw-trace --source --throw-context-size 200` 做 no-network 对照，`v8-20261003102000-alltrace` 产出 `call=1253 / callback=7 / get=30267 / has=1287 / throw_context=200`，仍无 request boundary；这证明设置打开后工具能多产出事实，剩余问题在 runner/宿主执行面。

证据：`agent-notes/20261003-node-env-gap.md`、`agent-notes/20261003-ruyidom-node-handoff.md`。

## 2026-10-03 Performance 提取与 Node 重跑

本轮已开始实际补环境验证。Firefox/RuyiTrace 提取确认 challenge 代码调用 `performance.getEntries()` 无参数并消费 Array，读取 `entryType/name/duration/requestStart/responseStart/responseEnd/transferSize/encodedBodySize`；同时使用 `PerformanceObserver.observe(Object)` 和 `EntryList.getEntries() -> Array`。原始值、entry 数组长度、observer options 和 descriptor 被证据脱敏，不能回灌历史 timing。

Node canary 使用独立 runner 副本，未改基线，按单变量逐层推进：

- `v8-20261003111529-qeznxd`：`getEntries()` 实际调用 1 次，旧 TypeError 消失，下一边界是 `window.top.location` / `classList`。
- `v8-20261003112439-lvq58g`：加入 `top = window` 后，继续到 challenge 容器的 `classList.add`。
- 后续 `v8-20261003112947-brzwm4`、`v8-20261003113333-kf3aaj`、`v8-20261003113705-ozl2lh`、`v8-20261003114712-z4l6s5`、`v8-20261003115013-erm6yx` 逐层验证了 `classList`、动态节点插入、`querySelectorAll`、`parentNode` 等真实调用面。

这些运行仍没有 FO/XHR/document boundary，空 `getEntries` 只证明方法缺失已越过，不能记作 parity。更关键的是：原 Node runner 用的是旧 `229681` 字节 orchestrate，和 RuyiDOM fresh 材料 `238694` 字节不一致；切换到同一 fresh source 后，后续 free identifier 从 `WHtx4` 变成 `PQak3`。这类名字不是可直接补成 host API 的证据，说明还存在动态资源/VM 输出/source-context 差异。对应详细记录见 `agent-notes/20261003-node-performance-rerun.md`。

Source 对齐后的 `v8-20261003121849-1ykah1` 仍没有 FO boundary。RuyiDOM bridge 已记录它会先加载 orchestrate、Turnstile API，并做 Window/global mirror；当前 Node runner 仍是直接 `eval` orchestrate。下一刀应恢复这一资源/跨 realm 执行面，而不是继续堆 DOM getter。

随后做了资源 canary：`v8-20261003130747-4pwon9` 首次执行落盘 `turnstile-api.js`，补 `HTMLScriptElement` 与 `document.currentScript.src` 后资源执行达到 `turnstileEval=ok`；`v8-20261003131931-dbzjwx` 再补 `performance.getEntriesByType` 后，该 API 缺口消失。两轮仍无 FO boundary，最后停在同一 fresh source 的 `PQak3`。因此下一阶段应审计动态 eval/runProgram/跨 realm 生成链，不能继续把 `PQak3` 当作可随手实现的 host method。

RuyiDOM bridge 的已验证路径是：Turnstile API resource 加载后，Window/global mirror（`xdiN1` 一类注册）完成，再出现 3× `/fo/` 请求形状。Node resource canary 目前只执行了 API 代码，没有迁移这层跨 realm mirror，因此下一刀应复现这个 mirror 的对象身份、赋值方向和 native-like 外观；仍不写入业务事实。

动态上下文审计已完成：fresh source 中 `PQak3` 只出现一次，位于字节/摘要处理调用位置，没有静态声明；旧 source 同位点是 `WHtx4`。fresh source 存在 `runProgram` 和间接 `eval` 标记，Turnstile 直接导出已被 resource canary 排除。当前高置信缺口是 `runProgram/eval` 生成值与跨 realm mirror 的 source/context 绑定，下一刀应记录 source hash、realm、define/read、descriptor 和 Function `toString`，不写 `window.PQak3`。

新增 frame 事实进一步收敛了这条链：RuyiTrace 的 Turnstile iframe HTML inline script 为 238636 bytes，内部包含 `PQak3/xdiN1/runProgram`；只执行 86 KB 的 `turnstile-api.js` 不等于执行 challenge realm。Node 独立 frame canary 在 parent/postMessage、`innerText/querySelector` 逐层补齐后能进入 frame 的 `PQak3` 读取，但仍无 `PQak3` define、FO 或 response boundary。`runProgram` source 已确认只是 VM wrapper，`xdiN1` 是队列写入函数，不能把任一者伪造成 `PQak3`。

## 2026-10-03 生产 iframe realm

`node run.js frame` 在独立子 realm 执行同一 inline script（238636 bytes，SHA-256 `05102bb5158cd0ba9a41329021f124cad8778a9a556db9a0e802b11c07115262`）。`frameEval=ok`，`chlOptKeys=37`，`framePqOwn=false`，`framePqType=undefined`，`throwName=TypeError`，`sendCount=0`，`boundary=boundary-unchanged`。没有真实 `PQak3` define，没有 FO。gate 仍是 not-ready / false。详见 `agent-notes/20261003-node-iframe-realm.md`。

## 2026-10-05 Firefox trace 更新

fresh RuyiTrace `rt_20261005125421_1d84c46dcd` 完成了 receiver provenance 取证。Turnstile API 的 `Element.attachShadow` 对 `HTMLDivElement` 调用，challenge iframe 对 `HTMLBodyElement` 调用；本 run 没有 `HTMLScriptElement.attachShadow`。因此 Node mirror/realm-probe 中的 `HTMLScriptElement` 只应视为 runner/source-context 诊断线索，不能作为外部宿主补丁依据。

同一 browser run 还观察到 orchestrate 调用 `HTMLFormElement.submit`，HTTP index 随后记录证书 document `POST 200`。该时序的 POST 为 `originCallId=0/no_source_context`，不是完整因果 correlation；不改变本地 `forms=0`、`localReproduced=false`，也不等于 `serverAccepted`。本地求解完成后仍须同一 lease 的独立业务 readback 200。

证据：`agent-notes/firefox-receiver-provenance-20261005.md`、`evidence/web/ruyitrace/rt_20261005125421_1d84c46dcd/receipt.json`。

对照修正：`agent-notes/trace-compare-20261005.md` 已证新 run 的 body/div 来源 identity 链；新旧 iframe hash 不同，尚无 source-aligned local pair。iframe DOMTrace complete=false，JSCall 有 dropped_gate=611，17 个函数达到1024阈值，sources_unavailable=3；receipt pass 不代表调用全覆盖。新 run 仅观察补充，权威 baseline/receipt/workflow 仍为旧 9 月 29 日 run。当前不授权 canary 或新增 host API。
