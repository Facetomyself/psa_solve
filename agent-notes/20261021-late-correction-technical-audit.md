# 深夜纠偏闭合与新增偏差技术审计（2026-10-21，22:20 后读取）

## 范围与当前快照

只读核查 20:18 审计之后的新产出；不执行目标、测试、网络、patch、next、fact，不消费新的 run 动作。当前最新正式执行仍是 **`02b1aecb92dd48d3b6edf237d0908795`**，scope `727d4f60...`，helper SHA-256 `40a98a9f2e93ce20c5c97bd697d5929fbac9cc5d10c3a8cf0b885cd6705faf57`；22:20 的改变是 gate/授权，不是新目标执行。

已锁定代码/状态/笔记哈希与脱敏 raw/side：`diagnostics/late-correction-audit-20261021/technical/`。已绑定文件当前一致，不报告 stale 漂移。

## 结论摘要

**真实改进：正式 collector 终于把 SecurityError、injected 来源类别、parentLine 等纳入 side；查明 1447 是锁定 Gecko RuyiDOM lib 的 document.write 注入入口，而不是 submit 或 VM 中某个新宿主调用。eval 剥空白保持撤除，失败和业务轴没有误升。**

**主要未闭合：Location/window 广补没有从默认 helper 隔离，还加了把 contentWindow 安全异常变成数值 0 的占位。新 gate 的来源分类比上轮细，但决定放行的 side 没有进入 execution 的 hash 证据链，receiverId 又是 collector 恒填的“未知”占位。不能据此认为已定位空 receiver，更不能认为新宿主行为已有双条件。**

## 1. 纠偏状态表

| 问题 | 核对状态 | 依据与限制 |
|---|---|---|
| 默认 eval 不等价剥空白 | **已改，维持** | 当前 helper 无旧 strip/fastPad 默认安装，本轮没有重新引入；不再批评已撤的同一实现 |
| 正式 collector 丢异常/source 身份 | **部分已改** | describeScriptError 动态分类 nsIScriptError 的 sourceName/errorMessage 等；02b1 的 side 确有新字段，但 raw 仍只有行列诊断 |
| 实际 receiver 未观测 | **未改** | receiverId 在 collector:375 恒填字符串 null，不是从比较操作数/错误接收者获得 |
| side 证据绑定 | **新增消费漏洞，未闭合** | execution 仅绑 raw/stdout/stderr，新 gate 直接另读同目录 side 无 hash/ref，scope 也未绑定这份运行输出 |
| Location broad catch/闭包 URL | **未撤，且覆盖扩大** | 沙箱旧 guard 继续保留；页面 Function 又安装四级原型 guard，均在默认路径 |
| top/parent=self | **未撤，生效范围仍未知** | installSandboxIdentity 中继续定义；真实 Window evalInSandbox 失败已被识别，沙箱/iframe 默认入口仍在 |
| iframe contentWindow | **新增非等价干预** | 安全异常时返回共享普通对象（valueOf=0,toString=''），不是浏览器 WindowProxy 合同 |
| 工具失败/完成轴 | **正确保留** | 02b1 仍 failed/exit1；三完成轴 false，未当 submit/业务成功 |
| null-receiver 新 gate | **从只诊断改为实际放行一处行为** | 当前 run、移除 no-new-host-surface、增加 one-host-behavior，已超过“继续取证”范围；但没有点名宿主 API |

## 2. 正式 collector 的新增身份哪些是真采、哪些不是

位置：`diagnostics/shadowroot-repair-20261020/host_submit_collector.py:275–375`。

### 已真实升级的部分

- sourceForm/sourceClass 根据实际 `se.sourceName` 分类，不是写死 about:blank（275–283,335–366）。
- errorName 来自错误文本正则，必要时读 `se.exception.name`（286–291,356–359）；insecure 来自实际错误消息。
- parentLine 从 sourceName 中的 `line N >` 解析（281–283），sourceLineLength 从实际可得 sourceLine 算；stackShape 尝试读取 se.stack/exception.stack。
- `02b1.../submit-host-side.json` 这些值确实已进入正式产物，优于上轮只在非正式探针笔记里存在。

所以不能把整张 side 都说成 AI 自填。它的错误类型与注入入口分类有真实工具来源。

### receiverId 仍是未知，不是“实际对象为空”

`describeScriptError` 返回值第 **375 行固定 `receiverId: "null"`**，listener 第 76 行再把它赋回 observed.receiverId。该值没有读取实际 receiver、比较的两个操作数、nativeId 或对象创建链。

必须区分：

- **已知 receiver===null**：真实操作数/调用接收者被捕获并比较；
- **receiver 未采集**：日志用字符串 null 作占位。

本案是后者。SecurityError 也不等同于 null receiver 的 TypeError。Grok 笔记承认“仍未点名 API”，不应把这种诚实的未知本身当假造事实；但 gate 用 `receiverId=="null"` 来筛选放行时，这个条件只验证默认日志格式，不能提升真实接收者的归因资格。

## 3. 1447 的归因有实质进展，但它只是注入父入口

锁定文件：`storage/web-runtimes/ruyidom/lib/ruyidom.js:1447–1451`：

- 1447 为 `Cu.evalInSandbox(`；
- 执行串是 `document.write(__ruyiHTML); document.close();`；
- 错误的 injected 脚本由这条路径产生。

这与 helper 内部当前的 1447 行无关，也不是 orchestrate 里的 submit 1:75507 或实际 Web API callsite。`parentLine` 动态解析结果与锁定 runtime 源码一致，能够说明**从哪个引擎注入通道出来**，不能据此知道 `<` 两个操作数是什么、哪个权限检查失败。

当前栈仍被压成 other，sourceLineLength=0；真实 source内容/动态 source hash 与接收者还没有被机器关联。正确的新增结论是“SecurityError 经 document.write 注入链出现”，而不是“已经找到了空 receiver 所需的一个新宿主面”。

## 4. F1 · P1 · fact：新 gate 关键输入 side 未绑定到执行证据链

### 实际写入与读取

- `host_evidence.py:271` 仅验证 raw、stdout、stderr 三类产物 ref；`324–326` 写 receipt 也只有这些输出。
- `02b1.../execution.json` 没有 side/submit-host-side.json 的路径/hash、通用 artifacts 列表或 side 摘要 hash。
- scope/config 绑定的是静态 runner/input/source/config 与 dependencies，**没有这份执行后产生的 side 内容绑定**。
- `web_case.py:3823` 校验 raw hash 后，**3858 行直接** `json.loads(raw.with_name("submit-host-side.json").read_text(...))`；未先 verify_ref 或与 raw 中同内容 hash 比较。
- 新 sourceClass/errorName/parentLine/receiverId 等放行条件都来自这份未绑定 side；raw 自身仍只包含旧的 2:3028 行列诊断，未容纳这些身份值。

### 影响

不改已登记 execution.json、raw、stdout、stderr 或 scope 的任何字节，只改这份 sibling side，就可能在 verify/ref 全不变的情况下改变 `_null_receiver_injected_security_error` 的结果和是否放开新宿主行为。无需怀疑 Grok 真的篡改，静态消费路径已证明鉴真边界遗漏。

这不是要求同用户工作区变成密码学不可伪造；是连当前已设计的“产物 ref/hash 一致性”也没有覆盖到**授权所消费的关键产物**。

建议先把 side 或完整身份事件纳入工具执行产物与 raw 的正式绑定，再消费它，而不是只以目录邻接当来源保证。

## 5. F2 · P1/P2 · fact：新 gate 放行的是实际行为，不仅是继续诊断；精确 shape 仍不能替代缺口证据

当前代码：`web_case.py:3760–3780,3867–3892`；正式回归 `test_web_case.py:3279–3360`。

- 精确检查 injected/about-blank-injected、SecurityError、insecure=true、parentLine=1447、sourceLineLength=0、keyword=false、stackShape=other、receiverId="null"、flags/category；
- 通过后为 `repair_null_receiver_identity`、**turnGate=run**；
- **移除 no-new-host-surface，增加 one-host-behavior**；
- 测试明确断言 run/不含 no-new-host-surface/含 one-host-behavior，因此不是一个仅凭名称误读的诊断动作。

比下午仅靠 function 关键字和缺字段更细，是正向来源分类；但缺 source 文本、缺栈位置、缺 receiver 都仍是缺证。精确匹配一组“未知字段取默认值”的形状，不能推导一个真实存在性/行为缺口。

22:14 的 `accept-completion-axis-unwritten.md` 曾明确说明：在未点名 API 时放开该约束会授权新宿主行为，因此不放开。22:20 note 又在**没有新的目标执行、helper未变、scope未变**的情况下修改 gate，使同一份 02b1 side 得到 run。这个变化的实质是授权策略改变，不是新运行证据消除了阻塞。

人可以选择批准探索，不等于代码缺陷；但必须称为**证据不足下的有界诊断探索**，而不是“identity-bound/空receiver已定位”的修复凭据。若接下来只是补操作数身份观测，方向正确；若再据此任选一项宿主行为，就是重复上轮无 receiver 广补的模式。

## 6. F3 · P1 · fact：Location/window 没隔离，contentWindow 又用普通常量对象吞安全异常

### 6.1 “已关闭的表面”不是“默认代码已撤除”

当前 helper：

- `915–986` 沙箱 identity 仍含 window/self/globalThis/top/parent→g；
- `937–980` 仍以捕获的 documentURI 替代 SecurityError，location getter 的 catch 仍不区分异常类别；
- `838–868` 新页面 Location guard 最多走四级原型；虽跳过 Object.prototype同名函数，仍以本页闭包 hrefText 回答不同 receiver 的失败；
- `1536–1539` 默认安装 sandbox identity、page Location、frame Window primitive，然后才执行 orig.apply。

scope 的 helper hash 正是当前 `40a98a9f...`，正式 generated probe 加载该 helper。因此它们确实是**正式 baseline 默认尝试安装**，不是只保留在独立诊断文件。

“不得重复已关闭的 Location/contentWindow/window 身份”可以理解成探索记账上不再重试，笔记没明说已删代码，不据此指控它说谎。但从纠偏执行看，上轮要求隔离广补没有完成，这些干预仍污染基线。

### 6.2 contentWindow 的占位不符合原生对象/异常语义

`frameWindowPrimitiveBody`（881–902）：

- closure 创建一个共享 `box={valueOf:()=>0,toString:()=>''}`；
- 原 getter 抛 SecurityError时返回 box（898）；
- getter 成功后还强行执行一次 `win<0`，若该额外转换抛 SecurityError也返回 box（899）；
- 将 HTMLIFrameElement.prototype.contentWindow 替换成该 getter（902）。

真实 contentWindow 应是相应 iframe 的 WindowProxy或 null，原生安全边界抛错与“返回可转成 0 的普通对象”不是等价行为。两个不同 iframe 的失败路径还会收到**同一个 box 身份**。读取 getter 本来不一定需要数值转换，这层又额外触发了一次转换。

这是一项明确的语义干预，不是单纯修 descriptor/toString 外观；当前没有 browser fact 证明同点失败应返回0/空串，也没有实际 receiver证明报错来自 contentWindow。

正式 `64d3...` 与 `02b1...` 的 raw仍不变，不能证明该补丁对目标触发或产生帮助。应区分“代码有这些语义风险”与“本轮错误已被该代码造成”；后者当前未知。

没有发现本轮另一个已证的 EventTarget 修复或相应 browser/local pair，不能把泛化的“宿主补齐”扩成已完成模块清单。

## 7. 当前真实产出与保持正确的部分

- 正式 side 从无身份升级成可分类的 injected SecurityError；这是本轮最有价值的新证据。
- 认识到 `Cu.evalInSandbox` 不能直接吃真实 page Window，旧页面 identity 调用未安装；这修正了上轮仅检查调用顺序的乐观假设。后续页面 Function 替代调用仍需实际行为验证，不是原生等价证明。
- helper/runtime/资源绑定当前一致，priorScope 和正式失败回执继续保留。
- 02b1 仍 failed/exit1、finished=false，无 host-observation；没有 submit:1:75507、wire/necko/resp 或 fresh readback 的新证据。
- 三业务完成轴仍 false，未把 gate 从 blocked变run误报成成功；本轮“门变了、目标未再跑”区分正确。

## 8. 最短收敛方向（本轮不执行）

先把正式身份 side纳入执行产物绑定；把 receiverId="null"改成明确 unknown/未采集，不把占位当对象状态。接着仅做操作数/真实source/callstack观测，确认 SecurityError真正来自什么安全边界。隔离没有双条件支撑的 Location/contentWindow常量兜底，再用同一输入看真实异常，而不是在同一未归因错误上继续换一个宿主行为。

最终判断：**正式观测前进了一步，纠偏没有全部闭合；决定继续修一处宿主的是新授权，不是新的 receiver或业务进展。当前最紧要的是证据链 side漏绑与仍留默认的常量兜底，不能只靠把 gate条件写得更精确来解决。**
