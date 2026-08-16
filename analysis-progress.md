# Web Analysis Progress

Case: `psa-cf-5s-shield-20260815`

## Update Discipline

- Read this file before changing a runtime shim, local reproducer, resource mapping, request shape, or risk plan.
- Rewrite it after each evidence capture, single-variable experiment, material failure reclassification, or completed batch. Keep only the current truth.
- Record evidence pointers and redacted hashes only. Do not write raw Cookie, token, account, proxy, challenge material, or browser profile data here.

## Current State

- Case status: `partial`（实验 serverAccepted 已记录；生产接入与交付合同未闭合）
- Current stage: `protocol-recovery` → `production-integration-pending`
- 结论：RuyiDOM/vanilla Node 路线曾取得真实页面回读；2026-08-16 已新增 capture-only JSONL IPC，使 Node 不再自行联网。PSA 同 Sticky lease 的 admission recovery 已完成本地测试，但 Mac canary、parity/risk receipt 与非 synthetic workflow/lineage 尚未完成，因此不得标 `completed`。
- serverAccepted 证据：2026-08-15 20:57 UTC（epoch 20260815-205514 材料）——引擎 fo 提交（POST /cdn-cgi/challenge-platform/h/g/fo/975026845:1786795506:.../a2b85a4b9d412442/{cH-token}）后，curl 带同一 __cf_bm 会话请求页面返回 HTTP 200、159131 bytes、真实 Next.js 页面（psa-locale/environment cookie + x-middleware-rewrite 头）。对照：无 clearance 时同请求 403 + 5.5KB 挑战页。
- 残留项：新版本材料（205514/204641 epoch）在提交后路径有 hk call-opcode 崩溃（fq 未执行、来源未定位——提交已发出并被接受，崩溃属提交后清理路径）；旧版本材料（15:01）无此问题。作为已知局限记录。

### 2026-08-16 clearance 会话绑定与生产链路实验（demo2-demo6 全记录，定论见 findings F6/F7）

#### 一、机制定性（官方文档 + 四源搜索求证）

- PSA 的 429 + `cf-mitigated: challenge` 来自 **rate limiting 规则 + managed challenge 动作**（throttling 模式，Free/Pro/Business 计划强制）；403 是 WAF/security 类规则 block 的状态码——Firefox 指纹通道当前只见 429（curl/Node TLS 通道才会 403）。
- challenge 状态按 fixed action 语义持续：**触发后 ~20-30s 内所有请求被拦**（与 clearance 无关）。
- 官方模型：pass challenge -> request counter 归零；cf_clearance tied to visitor/device（实测为 IP+UA+TLS 级）。

#### 二、实验时间线（同日，同 IP、同 sn 序列、firefox 指纹）

| 时间 | 实验 | 形态 | 结果 |
|------|------|------|------|
| 16:29 | demo2 串行求解组 | 同 session + 独立提交 clearance | 续航 [13,16,9,14] |
| 16:34 | demo2 no-solve 对照 | 等 25s 不求解 | 稳态续航 [6,8] |
| 17:28 | demo3 run2 | 新会话 B 带 clearance / C 裸 | B=1 / C=5 |
| 17:33 | demo4 AB 交替 | 触发后 20s 开始 | B、C 全被拦（窗口内） |
| 17:43 | demo5 同 session bridge | 冷却仅 2s | A 续航 5 |
| 17:47 | demo5 同 session bridge | 冷却 5s | A 续航 15，B 对照 0 |
| 18:52 | demo5 bridge | 求解提速后固定冷却撞窗 | A=0、B=0（恢复期仅 17s） |
| 18:54 | demo5 | 恢复期 30s | **反转：A=1、B=15** |
| 19:08 | demo5 subject=c | 单变量裸会话 | C=2 |
| 20:02 | demo5 subject=b | 单变量 clearance | **B=15（复现）** |
| 20:09 | demo5 subject=a | 单变量原会话 jar | **A=0（jar 污染）** |
| 20:32 | demo6 生产首跑 | 异步 bridge + 会话分离 | 段 [15,16,6*,15]，669 页/h，1 次连接挂起 |
| 22:18 | demo6 优化复跑 | 404 微间隔 + 挂起快判 + 重试 | 段 [17,8,8,9,9]，788 页/h，重试自愈 1 次 |

（* 6 为连接异常截断段）

#### 三、定论（横比三轮 + 生产复跑支撑）

1. **clearance 跨 session 有效**（IP+UA+TLS 级绑定）：裸 C=2 vs 带 clearance B=15（两轮复现），增益约 7 倍。官方「tied to visitor/device」在本场景不含会话级绑定。
2. **bridge 同 session 形态有 jar 污染副作用**：fo 响应 set-cookie 回灌进采集会话 jar，挑战链中间态 cookie 与 clearance 混带 -> 立即重新挑战（A=0 甚至低于裸 C=2）。demo2 旧形态（fo 走独立 cr.post）无此问题。
3. **求解通过 = 计数器归零**：B 从 0 打到阈值（15）才再触发，与 Phase 1 触发位置一致。
4. **恢复等待必须按距触发绝对时间 >= 30s**：求解提速（27s -> 12s）后固定冷却会撞衰减窗口。
5. **rate limit 阈值动态衰减（F7，medium 置信）**：同 IP 当日 20+ 轮实验后，段通过数从 15-16 降到 8-9（20:32 run 15/16/15 -> 22:18 run 17/8/8/9/9）。求解成功率保持 100%，触发频率上升是 CF 侧收紧。单 IP 吞吐上限随之从 ~1000 降到 ~750-800 页/小时。

#### 四、生产形态（demo6，已两轮实测）

```
干净 AsyncSession 采集（显式 ck，404 微间隔，gap 间隔）
  -> 429 触发（挑战页 body 直接到手）
  -> 触发会话即用即弃 capture-only bridge 异步求解
     （asyncio subprocess + AsyncSession 发 fo + FO_CONTINUE/FO_ACCEPTED 分类 + stdin 回灌）
  -> 恢复等待（距触发 >= 30s）
  -> 新干净 AsyncSession + 显式 ck 继续
异常处置：挂起 10s 快判 -> 重建会话重试一次 -> 仍失败 45s 冷却；
重试撞挑战页直接转入求解。
```

吞吐模型（单 IP）：`段请求数(阈值) × RTT + 求解 ~13s + 恢复 ~17s` 为一个周期。
- 阈值 15 时：~50s 周期 -> ~1000 页/h 理论上限
- 阈值 9 时（当前 IP 状态）：~43s 周期 -> ~750-800 页/h（实测 788 已贴合）

#### 五、边界与下一步

- 单 IP 继续优化的代码空间已尽；提速路径：IP 冷却数小时（阈值大概率回 15）、换出口、或多 IP sticky 池轮换（每 IP 一个 demo6 worker，proxy-usage 提取 + 注入，吞吐线性扩展——高并发采集的正确姿势）。
- F7 为 medium 置信：需不同 IP/时段对照确认阈值衰减是「当日行为累积」还是「长期趋势」。
- demo6 的 solve_bridge_async 与主循环是采集主链的移植单元；旧 bypass_solve（demo2/3/4/5 共用形态）已被 bridge 形态取代。

## Browser / Local / Purecalc Boundary

- Browser fact role: `verified`（rt_20260815060651_eb196ed770，index/receipt integrity pass，rootSha256 399daaf7dc35e4b7489aed07db3c60cf0c69d80bdfb0e0da5f78fedfadc8df7e；receipt pointer sha256 自引用不一致为 MCP 侧 bug，已在 web-case.json limitations 记录）
- V8 local fact / first divergence: 未启动（引擎执行层优先）
- Environment patch scope: `external-host-only`; VM/opcode/bytecode/WASM internal patch: `forbidden`
- Success baseline (`code.js` / `runtime/*.code.js`) and `.base.js` hash: 未建立
- Purecalc ledger: `纯算提取进展清单.md`
- Purecalc candidate (`code.pure.js` / `runtime/*.pure.js`) and stable entry: 未建立
- `localReproduced` / `transportAdmission` / `serverAccepted`: 均未达
- Vanilla client business readback evidence: 无
- Browser automation in final collector: `forbidden`

## Stable Baseline

- Browser run / evidence pointer: rt_20260815060651_eb196ed770（psa_solve）
- Local run / profile: RuyiDOM gecko-xpcshell（Firefox 135 base），runtime hash 校验 pass
- Canonical input hash: 挑战页 cH/cN/cRay 每次访问刷新；runner 输入 `ruyidom-input-v1.json`
- Resource epoch and relevant content hashes: orchestrate `chl-page-orchestrate.js`（228910 bytes，ray a2b5fd7dff701b46 版本）
- RequestShape / target endpoint: `POST /cdn-cgi/challenge-platform/h/{flow}/{eb}/{payload}/{...}/{...}`；flow 段当前为字面 "undefined"（缺口）
- Verified wire route / decoy or wrapper route: 提交为 challenge-platform 相对路径 POST
- Dynamic state and Cookie writer / refresh / outbound egress evidence: `__cf_bm` 两段刷新（挑战前/求解后），`cf_clearance` 求解后下发（浏览器事实）
- Response decode pipeline and fixed-sample proof: 未建立
- Route-local transport admission matrix: 未建立

## Parameter And State Ledger

| Field or state | Source -> transform -> consumer | Current verification | Evidence pointer |
| --- | --- | --- | --- | --- |
| `_cf_chl_opt` | 403 页 init script 注入 -> orchestrate 读取 | 33 字段初始化 verified（引擎） | runner pageState.cfChlOptKeys |
| 提交 URL flow 段 | orchestrate 内部构造 | 3 段字面 "undefined"（缺口） | runner wire xhr url |
| `cH`/`cN`/`cRay` | 403 页每次刷新 | 时间敏感已排除（fresh 页同缺口） | challenge-page-fresh.html |

## First Divergence Or Blocker

- Observation: 引擎执行 orchestrate 后抛 `TypeError: can't access property "call", iw is undefined`（混淆局部变量，经 eval 抛出，window.onerror 不捕获）；提交 XHR URL 含三个字面 "undefined" 段。真实浏览器同版本 orchestrate 无此错误（求解 1.1s 完成）。
- Classification: `execution-boundary`（orchestrate 混淆内部执行路径差异），宿主 API 面板健全已排除常见缺口；meta CSP 与 history.replaceState 两缺口已修复且有证据。
- Evidence pointer: runner 输出 errorShapes.stackHead（observe@ruyidom.js:1267 链）
- Why alternative explanations do not currently fit: fresh 挑战页重跑结果一致（材料过期排除）；hostPanel 16 项宿主 API 全 function/object（宿主缺失排除）。

### 2026-08-15 v8trace 定位收敛（源码级）

- v8trace（challenge-fast，1415 records）Node 崩溃：`TypeError: T[rv(...)][rv(...)] is not a function`；RuyiDOM 引擎同位置 `IG is undefined`——两环境同根。
- 崩溃链（v8trace throw_context + 源码解码）：
  1. J 表构建（RfXVH/JSyym/UoZbM/Toloz/UMkbs/BUgft 6 函数 + SzTgJ="…challenge-platform/h/" + bXxEG="navigation" + yQYB9 数组）完成（源码 50136 附近）
  2. 主逻辑调用 `T[1381](base64$base64)`（日志队列函数，源码 28525 定义：内部 `T[1020][1761](Z)` push 日志）
  3. 崩溃：`T[1020][1761]` 不是函数——T[1020]=[] 的赋值（源码 28496）与 T[1381] 同序列、位于 switch 语句 break 后——**该赋值序列被条件跳过**（引擎环境未走进对应 switch 分支）
- 关键编码解码：wn.Ie=1381、wn.Ip=2099（条件检查键）；dG={Z:1020,J:870,IV:958,Ip:1020,Ii:1761}（T[1020]=队列数组、T[958]=30、[870]=length、[1761]=push 语义）。
- 遗留定位工作：真实浏览器执行路径对照（该 switch 分支在浏览器是否执行、依赖哪个环境条件）——CDP 断点 orchestrate 源码 28496 可一步验证。

### 2026-08-15 三环境对照（Node/iv8/RuyiDOM）与缺口阶梯

- iv8（离线 V8 + DOM 仿真，probe-4 domPanel）：`document.createElement`=function 但
  **`document.createElementNS`=undefined**——orchestrate 在 Pv（源码 106287）调用
  `C[XJ(...)](2参数)`=createElementNS(ns,tag) 创建 CF 指纹 SVG 元素（`cx`,`15` setAttribute）。
- iv8 + createElementNS 桩后：无错误但 0 POST、静默退出（下一缺口不抛错）。
- Node（v8trace v8-20260815075849）：补 createElementNS 桩后崩溃点后移 3 行
  （index.jsonl:1396 vs 1393），同类型 T[rv()][rv()] 崩溃——Node DOM 缺口面过大，
  逐桩补齐不现实（SKILL.md 判据：DOM 缺口面大 = 补环境不可行场景）。
- RuyiDOM（真实 Gecko，最完整）：**createElementNS ×3**（lastTag="path"，SVG path）
  + createElement ×41 执行成功，之后崩于 `IG.call`（IG undefined）——比 iv8/Node
  走得更远。错误经 eval 抛出无列号（onerror/addEventListener('error') 均不携带
  message/colno）。
- 结论：公共缺口=createElementNS（有证据）；RuyiDOM 的 IG.call 是下一缺口
  （orchestrate 内部，混淆变量名，定位需 VM 级分析或引擎列号支持）。

### 2026-08-15 IG.call 定位收敛（Pv → IF 函数边界）

- Pv 函数完整解码（源码 106287 后）：`document.createElementNS` 创建 SVG 图标
  指纹元素（setAttribute cx/cy/r=15 + path d=CF 图标路径数据 + appendChild 组装），
  **RuyiDOM 已完整执行**（createElementNS×3 计数吻合：circle/icon/path 三元素）。
- 崩溃点 = **下一个函数 IF 的首行**（源码 138575 附近）：
  `IV = T[ZZ(1753)][ZZ(1134)]()`，随后 `for(Ip=0; Ip<IV[ZZ(870)]; ...)` 遍历——
  语义是"获取元素集合并遍历"。`IG.call` 崩溃 = T[1753键][1134键] 非函数。
- T[1753] 非 document（RuyiDOM 的 document 方法原生齐全且 querySelectorAll 类
  可用）——需字符串表解码 1753/1134/870 三键确认宿主对象。
- 三环境统一叙事：Pv 之前的缺口（createElementNS 等）→ 修后到达 IF 的
  T[1753][1134] 集合调用——真实浏览器该调用成功（元素集合非空）。



### 2026-08-15 IG.call 最终定位（ID 状态机 case '5'）

- IF 链路全健康（RuyiDOM 插桩实测）：`performance.getEntries` ✓、
  `PerformanceObserver`（new T[1910键]）✓、ID 回调是 function ✓。
- 崩溃点 = ID 状态机（源码 180073 函数）case '5'：
  `T['_cf_chl_opt']['yQYB9']?.['call'](IG)`（插桩解码：_cf_chl_opt,yQYB9）。
- RuyiDOM 里 `typeof _cf_chl_opt.yQYB9` = **object**（非函数）；真实浏览器
  挑战求解期 yQYB9 应为函数（挑战完成后 _cf_chl_opt 整体清除——CDP 实测
  hasChl=false，求解期临时状态）。
- 语义：yQYB9 是 orchestrate 求解流程注册到 _cf_chl_opt 的回调函数；
  RuyiDOM 引擎里注册步骤未执行（被更早的环境分支跳过），yQYB9 停留在
  对象形态（33 字段初始化的字段形态）。
- 三环境缺口阶梯定稿：
  Node（createElementNS 等 DOM 缺口面大）< iv8（修 createElementNS 后
  静默退出）< RuyiDOM（走最远，卡在 yQYB9 回调注册链）。

### 2026-08-15 Phase 1 结果：yQYB9 假设修正

- 赋值历史捕获（_cf_chl_opt setter 观测）：403 页 init 整体赋值 16 字段；
  yQYB9 **仅一次赋值、类型 object、Array.isArray=true**——**yQYB9 是数组**
  （收集 performance entries 的队列），"应为函数"假设被推翻。
- case '5' 真实操作（三键解码）：`_cf_chl_opt.yQYB9.push(entry)`——
  数组 push，引擎里健全。
- 崩溃点在更深处：caseNow=2（ID 状态机 case '2'）——case '2' 变量面板
  健全（Ic=object/PX=function/PI=object/IV[IU]=function）——崩溃链
  ID case '2' → PX（源码 37470）→ PJ（源码 125005，entry 属性 JSON 解码：
  `decodeURIComponent(JSON.parse(...))`）。
- PJ 的 J 参数（entry 属性字符串）在引擎环境可能为 undefined 或格式差异
  ——下一缺口定位目标。
- 嵌套回调链：ID case '2' → PX → PJ（每层 2-3 工具调用下钻，还有若干层）。

### 2026-08-15 Reqable 真实浏览器对照（决定性新事实）

- 当前 PSA 无感挑战 = **Turnstile non-interactive 自动通过**（用户无点击）。
  提交 URL 模板 `/cdn-cgi/challenge-platform/h/g/fo/{id}:{ts}:{hash}/{ray}/{token}`
  （psacard.com 侧 + challenges.cloudflare.com 侧各一次 fo POST，最后
  POST /cert 带求解结果拿 200 页面）。
- 新版 orchestrate（229681 bytes）内 eb 模板：`/eb/{id}/{ray}/{token}`，
  id 为硬编码字面量。引擎旧材料拼出的 `/h/undefined/eb/{id}/undefined/undefined`
  缺 ray/token 段。
- 新 orchestrate + 新 403 页重跑引擎：错误从 `iw` 变 `IG`（同模式
  `.call` 崩溃）——缺口跨版本稳定，是引擎环境差异而非材料问题。

## Current Single-Variable Experiment

- Baseline: offline 注入 + orchestrate 本地映射 + history/storage 桩（v1 runner）
- Changed variable: 移除 meta CSP（v4）→ history.replaceState 包装（v5）→ storage 原型包装（v6）→ fresh 挑战页（v7）
- Expected discriminating result: 提交 URL 完整、无 orchestrate 内部异常
- Result: SecurityError 已消除；`iw is undefined` 与三个 undefined 字段稳定存在
- Evidence pointer: psa_solve/ruyidom_cf_shield_v1.js 迭代记录

## Rejected Or Inapplicable Routes

| Route | Evidence that rejected it | Re-open condition |
| --- | --- | --- |
| RuyiDOM 真实导航（v2） | 导航后 document 空（location 仍 about:blank） | 引擎真实导航模式修复 |
| gated trace 抓挑战段 | GATE_TIMEOUT / BROWSER_OWNERSHIP_PROBE_FAILED 两次失败 | MCP 侧修复 |

## Minimal Verifiable Facts

- 403 页 managed challenge（cType managed / cTplV 5 / cvId 3），CF 边缘 NRT。
- 浏览器求解 ~1.1s 且 managed 无交互自动通过；Turnstile 只在预热 profile 连续访问时触发（本 case 目标规避）。
- 引擎能初始化 `_cf_chl_opt` 33 字段并发出提交 XHR（URL 不完整）。
- 提交 URL 前缀 `/cdn-cgi/challenge-platform/h/`，三个 "undefined" 段为 orchestrate 主动拼接的字面量（缺口字段名待定位）。

### 2026-08-15 环境缺口定稿：UpvLO0 + ZHfDS6（VM 程序验证链）

- VM 程序（IY 状态机 case '13' runProgram，44 opcode 主程序 + 子程序）语义已完整解码：
  - yQ=常量物化（字符串/数字/NaN/数组）、yD=双寄存器常量、yX=寄存器移动、yA=对象创建、yj=对象字段写、y7=属性获取、ye/yR=按名调用 opcode（`obj[prop].call(obj,args)` 族）
  - 程序数据：10 个字符串（window/prototype/ANTT9/UpvLO0/querySelectorAll/querySelector/Element/Document/style/eval）+ native 函数 + 常量 4521/NaN/1755
  - 第一个调用：`window["UpvLO0"].call(window, "1v01dl/...==$NtkGhkT...==(base64$base64 16+16字节)")` — 引擎里 window.UpvLO0 undefined 崩溃（yR opcode Io=1 分支，方法键 "call"）
  - 第二个调用：`window["ZHfDS6"].call(window, "function jcLw7(s){return function(k){for(var o=new Uint8Array(k.length),i=0;i<k.length;i++)o[i]=k[i]^s.charCodeAt(i%s.length);return o}}")` — ZHfDS6 接收程序重建的**完整函数源码**（XOR 流解密器）
- 程序自身从字节码重建函数源码（"function"+" "+"jcLw7"+"(s){...}" 片段拼接）→ 交给 ZHfDS6 → 随后程序调用 window["jcLw7"] —— 语义：ZHfDS6 = 函数注册/求值助手（真实浏览器中由 orchestrate 定义，被引擎环境分支跳过）
- 诊断桩（功能性）：window.UpvLO0=记录桩；window.ZHfDS6=(0,eval)(src) —— 补桩后 errors=0，程序完整运行：
  - 到达「Verification successful. Waiting for {placeholder.com} to respond」（PJ 解码 mtsjj1 文案）
  - 构建隐藏 iframe（sandbox=allow-same-origin + visibility hidden 等 8 项样式）
  - UpvLO0 后续调用载荷：13V7mVH...$QnwcCJ...、bY4JPwin...$o1+qY2T...
  - 性能指纹基准循环：1337331 空格字符串（~1.3MB）+ Date.now 时间戳反复构建 —— 循环等待提交层响应不闭合
- 剩余缺口：提交/响应异步层（Worker「honk」消息协议 / blob URL / iframe 脚本）在 RuyiDOM 引擎未把消息回传页面，程序永远轮询。RuyiDOM Worker/iframe 异步支持待验证（hostPanel wk=function 存在但消息回传未证实）。
- 关键证据文件：workspace/psa_solve/ruyidom_cf_shield_v1.js（插桩 runner + 级联桩）、challenge-material/orchestrate-served.js（served 代码，列号映射用）

### 2026-08-15 提交链路实证（第二里程碑）

- Worker/blob postMessage 往返 smoke 通过（pong:ping）——RuyiDOM Worker 层不是执行边界。
- **window.ZHfDS6 = window.eval（原生别名）**——程序检查 `ZHfDS6.toString() === eval.toString()`（对比值 false 时循环）；1.3MB 空白字符串是 eval 性能指纹基准（长度 1337359 ≈ 程序常量 1337331）。此前 eval 桩/worker 转发桩均错。
- UpvLO0 = XOR 流解密器（按 jcLw7 语义实现，payload base64$base64 拆分 XOR）——已产出 16 字节解密值（e02433f0...、95096791...、ced1a35c...、8d5e4d41... 等，MD5 级 128 位哈希形态）。
- 修复 `String.replace` 的 `$'` 特殊模式 bug（wrapper 中 `split('$')` 被替换串解释，整个页面被插入）——改用 replacer 函数。
- 修复 setTimeout/setInterval 包装 receiver（固定 window，程序用对象作 this 调用时原生会抛）。
- resources.handler 改为 blockUnmapped:false + challenge-platform 的 xhr/document 放行真实网络（net-pass 记录）。
- **提交实证**：`POST /cdn-cgi/challenge-platform/h/g/eb/478345907:1786773913:H-v1Ic.../a2b6539108bf25c6/managed`，body = 完整 $ 分隔指纹载荷；页面设置 cf_chl_rc_ni=1；_cf_chl_opt 新增 CqJg7/cseK1/jWOLY8 字段；流程深入 Angular testability 探测（whenStable/getTestability/get）。
- 剩余缺口：P7 轮询器（提交验证 + 重试）内 `J["DCkwl7"]`（ZZ(1011)）读取 J undefined——J = P7 第二参数，来自 Iw 的 `setTimeout(P7,100,Ig,IG)` 传参（IG undefined，上游状态缺口）。P7 尾：`J[ZZ(519)]=...` + `Ie.send(x(J))`，x(J) 为载荷变换函数。

### 2026-08-15 cf_clearance 持续采集验证（生产可行性）

- 实验（test_clearance_collection.py）：sticky 出口（196.170.94.23，全程一致）拿 clearance → 同出口同 Firefox 指纹连续请求 20 个页面。
- 结果：17×200 + 3×404（序列号不存在的业务空结果）+ **0×403**——有效页面实质 100% 通过。
- 采集四契约（实验确认）：① sticky 出口绑定（sid+t-30，clearance 与出口 IP 绑定）；② TLS 指纹一致（Firefox impersonate）；③ __cf_bm+cf_clearance 会话延续（跟随响应轮换）；④ 0.3s 间隔 20 连发无触发。
- 生产闭环：403 → Node 求解（14s）→ curl_cffi 提交 → clearance → 同会话持续采集；clearance 过期重走 --fresh。

### 2026-08-15 Cliproxy 机房 IP 链路验证

- 链路（记忆 cliproxy-windows-chain-lessons 复用）：本机 → `ssh -D 127.0.0.1:18081 oracle-newapi-primary`（SOCKS 隧道）→ Cliproxy gateway `us.arxlabs.io:3010`（Rand 账号，机房出口 223.196.193.34/102.157.229.183 等）→ 目标。Windows Clash TUN 对 gateway 3010 明文 CONNECT 系统性挂起——必须走 SSH 隧道（历史已知坑）。
- demo 新增 `--cliproxy-rand`：材料抓取（curl_cffi 非 impersonate 经级联触发 403）+ 提交/验证（curl_cffi Firefox 指纹经级联）全链路机房 IP。
- 实测（23:38）：材料 403 → Node 求解 errors=0 → fo 提交 200 → cf_clearance → 验证 200 + 159,484 字节 + "Cert Verification 143963534" = **serverAccepted TRUE**。
- 观察：机房 IP + Firefox TLS 指纹直通 200（无挑战）；机房 IP + 非浏览器 TLS（curl 原生）触发 403——TLS 指纹仍是首要变量，IP 类型是次要变量。
- 遗留清理：测试 SSH 隧道（18080/18081）已清理。

### 2026-08-15 TLS 指纹根因定稿（重新 trace 结论）

- **重新 RuyiTrace capture（2.5.6 runtime，fresh profile）**：真实浏览器指纹（Firefox 155 TLS）**直通 200**（无挑战）——同一 IP、同一时间窗口。
- **curl_cffi 0.16.0（impersonate=firefox）实测直通 200 + 159KB 真实页面**——与浏览器一致。
- **根因定稿**：TLS 指纹是决定性变量——Node 20 TLS 在 CF 侧被标记为非浏览器客户端（触发挑战 + 求解后验证被拒）；Firefox 指纹放行。此前「IP 风控升级」归因被修正：真正变量是客户端指纹层，IP 变化只是改变了触发条件。
- **修复链路**：求解仍在 vanilla Node（orchestrate 执行 + 载荷产出）；**提交与验证改用 curl_cffi Firefox 指纹**（demo.py IMPERSONATE="firefox"）。实测：fo 提交 200 + cf_clearance 签发 → 验证 200 + 159,618 字节 + title "Cert Verification 143963534"（真实页面）。
- demo.py 无参数一键运行稳定复现 serverAccepted（23:19 验证）。Node 求解侧无改动——载荷自始至终被 CF 接受，唯一变量是发送载荷的 TLS 指纹。
- 修正历史局限记录：curl/Python urllib 重放被拒的原因同为 TLS 指纹（非「不同源」）；curl_cffi Firefox 指纹是唯一验证可用的 Python 侧 client。

### 2026-08-15 eb 触发定位与无痕对照

- eb 提交代码结构已定位：`new XHR → open("POST", ebUrl) → timeout=5e3 → setRequestHeader → send(gi(gN))`，整段在 try/catch（异常静默吞）。Node 中该段未执行（无 open 记录）——**上层触发条件不满足**，非 send 失败。
- 同进程内联验证（求解+验证同一 Node 进程/TLS）仍 403——**TLS 会话绑定假设排除**。
- **无痕浏览器对照（用户实测）**：无痕可直接进入（managed 挑战自动求解通过）——IP 未风控。Node 求解被拒而真实浏览器通过——差异收敛到：① eb 提交缺失（浏览器必发）；② 行为指纹质量（Node 的性能基准/时间戳字段与真实浏览器分布不同，CF 风控模型学习后收紧）。
- 排除项汇总：TLS 会话绑定（同进程仍 403）、IP 风控（无痕浏览器正常）、cookie 组合（jar 语义已修）、XHR 响应头（已修）。
- 剩余主嫌疑：eb 提交（触发条件上层链待定位）+ 行为指纹字段真实性（补环境边界——1.3MB eval 基准、时间戳等为 Node 真实值而非浏览器值）。

### 2026-08-15 分支链路对比（Node vs RuyiDOM 同材料）

- 同材料（223831）对比：RuyiDOM 提交 = fo ×1 + **eb/managed ×1**；Node = fo ×2——**Node 缺 eb 提交分支**。
- 已修复相关缺口：XHR `getResponseHeader/getAllResponseHeaders`（原返回 null——P7 读响应头判断）、document.cookie 增量 jar 语义（原覆盖语义丢失 cf_clearance）、XHR 标准字段（responseType/responseURL/withCredentials/timeout/upload/on* 事件属性）。
- eb 提交仍未触发：fo 响应 body 为加密 blob（非 JSON），P7 的解密-判断链未闭环（解密函数/key 来源待定位）。
- **关键对照**：22:26 的 Node serverAccepted 成功时同样无 eb 提交——**eb 非 clearance 生效的必要条件**（至少风控宽松窗口如此）。当前连续 403 主因判断仍为 IP 风控升级（高频求解），eb 缺口列为结构差异待完善项。
- 载荷字段数对比（同材料）：Node 29 字段 vs RuyiDOM 20 字段——结构差异存在，但字段值为随机加密无法直接对比内容。

### 2026-08-15 IP 风控升级证据（验证波动归因）

- 时间线：21:40-21:47 vanilla Node 补环境 serverAccepted 多次成功（HTTP 200/159KB）；21:48 起连续 6+ 次全 403（demo 与 verify 脚本同败）。
- 求解链稳定：cf_clearance 每次均签发（Node fo 提交响应），失败仅在「clearance 页面验证」环节。
- 排除项：TLS 一致性（Node TLS 验证同 403）、cookie 组合（原材料 bm / 轮换 bm 双组合）、代码差异（demo 与 verify 脚本同败）。
- 归因（风控判定纪律-多维）：AWS 数据中心 IP（43.199.43.75）高频求解（半小时 20+ 次 fo 提交）触发 CF 会话风控升级——clearance 形式签发但页面二次验证（jsd 行为证据层）拒绝。求解链能力不变，验证成功率受 IP 信誉窗口约束。
- 复验路径：换 IP 冷却后重跑 demo.py --fresh（求解链无需改动）。
- **复验结果（用户实测）**：换 IP 后 demo.py --fresh 通过——serverAccepted 复验成功。归因闭环：IP 风控升级是唯一变量；vanilla Node 补环境求解链稳定可用。

### 2026-08-15 vanilla Node 补环境 serverAccepted（最终里程碑）

- **纯 Node（无 RuyiDOM/浏览器）求解 → Node XHR 提交 → cf_clearance → 页面 200/159KB = serverAccepted TRUE**（2026-08-15 21:41，demo.py 一键复现）。
- 关键修复链（Node 版 eb/clearance 闭环）：
  1. XHR shim 相对 URL 需 base（`new URL("/cdn-cgi/...")` 失败静默 return——提交从未发出）
  2. XHR 同源自动附 Cookie（浏览器行为；此前提交无凭证被 CF 拒）
  3. 响应 Set-Cookie 应用（字符串/数组双形态）+ demo 从 responses 提取 cf_clearance 与轮换 __cf_bm
- 验证证据：Node 的 fo 提交响应 `cf_clearance=I.5OxTVQlN...` + 轮换 __cf_bm 组合请求页面 → HTTP 200、159,394 字节真实页面；Python/curl 重放同载荷被 cf-chl-out 拒（TLS 指纹）——**Node 20 TLS 被 CF 接受**。
- 提交形态：fo ×2（bodyLen 2178 首轮 + 4599 完整轮）；clearance 由第二轮响应签发。

### 2026-08-15 vanilla Node 补环境形态（模块化重构）

- 用户纠正：补环境运行时依赖应为 Node（RuyiDOM 是诊断执行层，SKILL 主线：vanilla Node/Python client 最终验收）。demo 用 Python（非 PS）。
- 产出：`runtime/code.js`（vanilla Node 浏览器面 shim + 定位缺口补丁）+ `runtime/run.js`（vm 执行 + 提交捕获）+ `scripts/demo.py`（无参数一键 demo）。
- Node 补环境缺口链（本轮定位）：classList 元素面 → location 定义顺序（document.location undefined）→ window 别名/类构造函数（Element/Document/RTCPeerConnection 等）→ 按名全局（ANTT9/qOeu1/PnHD6）→ VM `new Proxy` null target（垫底）。
- 当前 Node 版状态：errors=0、fo 提交产出（bodyLen ~2188）、Python urllib 发送得 HTTP 200（无 cf-chl-out，形式接受）；**eb 提交未产出、clearance 未签发**——Proxy 垫底改变 VM 探测分支。如实记录：serverAccepted 证据仍属 RuyiDOM 诊断层。

### 2026-08-15 提交链路完整闭环（第三里程碑）

- **根因（最终）**：我的 setTimeout/setInterval 诊断包装器丢弃了原生变长参数——`setTimeout(P7,100,Ii,Ic)` 的第 3/4 参数被吞，P7 收到 (undefined,undefined,undefined) → `open("POST","undefined")` + `J["DCkwl7"]` 崩溃。修复为 arguments 全量透传后 errors=0。
- IY 嵌套机（IQ 回调）程序串 `0,3,2,4,1`：case 4 构建数据映射 Ic（cpza4/kwYu6/Cplz9/zcNj0/bACR4/gAMzq7/NWUB3/WpIu5/yRMqb7/jRwR8/yTXuH8/NGYVs4/yCCo2/ucBTZ7/InHf7/riWe2/YIjU8/qOeu1/PnHD6/IfWx3/RGOD3/QnRk5 21 字段）→ case 1 调度 setTimeout(P7,100,Ii,Ic)（此时 Ii=string /fo/ URL、Ic=object）。
- IY case 11 构建 /fo/ 提交 URL：`J[ZZ(1847)](J[ZZ(1962)](J[ZZ(1352)],_cf_chl_opt[ZZ(1408)])+'/fo/478345907:1786773913:H-v1Ic.../'+_cf_chl_opt[ZZ(1755)],'/')+_cf_chl_opt[ZZ(759)]`。
- **提交实证**：3 次 POST `/cdn-cgi/challenge-platform/h/g/fo/478345907:1786773913:H-v1Ic.../a2b6539108bf25c6/{cH-token}`（与 Reqable fo 模板一致）+ eb/managed POST；body = 完整 $ 分隔指纹载荷；P7 轮询器 4 次带参调用（Z=string,J=object,IV=number）。
- 已知未决：字符串表 ZZ 偏移并非全局 475（_cf_chl_opt 实际在 entry 1371→键 1846，DCkwl7 在 536→1011）——静态解码需按函数族分别确认；运行时解码已全部验证。

## Next Minimal Action

- Action: ① 获取新鲜挑战材料（当前 IP 不触发挑战——需换低信誉 IP 或等待自然触发）复验 serverAccepted；② 按 SKILL 产出最小补丁版 code.js（剥离诊断探针，仅保留功能性缺口补齐：UpvLO0 XOR 解密 + ZHfDS6=eval + storage/history 包装 + 变长参数透传）；③ 更新三件套（report/findings/triage）。
- Required fresh evidence: 新鲜 403 页 + orchestrate（同版本材料）下的引擎复跑 + 真实 CF 响应（cf_clearance 或拒收原因）。
- Stop condition: serverAccepted；或新鲜材料复验仍被 CF 拒收（按风控判定纪律多维归因，记录 evidence 转路线评估）。
