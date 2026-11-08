# Grok 下午增量技术审计（2026-10-21，19:00 后读取）

## 范围与快照

本轮只读核查 13:04 午间已审计状态之后的改动和 19:00 放行记录，不执行目标、网络、补丁、next 或事实写入，也不打断活动进程。没有把旧 last-copy 当下午会话。

锁定快照：

- helper：`document-principal.js` SHA-256 `7833680f96bce1cc91dc50df409c34a60847ca01479102885a0a1de7cae667f9`。
- 当前 scope：`75fe61cf541e6e34...`。
- 最新正式 baseline：`356e17e4159e4aee8da0a6cc37d3d8c8`。
- 当前动作由主线程已读为 `repair_submit_host_behavior / blocked`，指向 2:3028 的 function 关键字；本代理不再次调度。
- 输入哈希、脱敏 raw/side：`diagnostics/afternoon-audit-20261021/technical/`。运行中的进一步修改不属于本快照。

## 结论

**有可保留的纠偏：中午指出的 XHR/Observer 同步时序问题已有代码层修正，settings FATAL 和普通脚本失败被区分，origOpen 列号也没有继续被错当 getter 根因。**

**新的主要偏差是：默认又加了一层不安全的 eval 源码改写；最新没有 sourceName/错误名的 2:3028 failure 被精确写进特许 gate，仍未证明具体宿主缺口。**目前没有新的真实 submit/业务边界通过证据，运行从约 22.7 秒变为约 9.1 秒不能单独算“跑得更远”。

## 1. 最新实际进度：失败形态变了，不是提交链已推进

权威链：`contracts/host-evidence/state.json` → baseline `356e17.../execution.json`。

- status=failed、exitCode=1、timedOut=false。没有该 scope 成功 patched/pair/classify。
- raw 222 bytes，仅 host-diagnostic + summary；诊断为 line=2、column=3028、matched=false，sourceSha256 是 collector 固定写入的绑定 orchestrate hash。
- side：base=object、getEntries=function，access/threw/receiverId=null，**finished=false**，scriptError 只有 kind=other/class=other/line/column；没有真实 sourceName、error name/message、sourceForm/sourceClass。
- 正式 collector 仍不写 wire/necko/resp。因此没有工具证据证明 FO、XHR、submit 或证书 POST 已到达；“raw 里 0 行”不能当完整网络未发生的证明。
- 午间的 side 曾 finished=true、slow-script；当前 finished=false，且 collector 排除了 warning 才记录这条 other 错误。准确描述应为“构造/初始化尚未正常完成，出现了另一条未归因的非 warning 错误”，不能说已经进入 submit 前更深阶段。
- serverAccepted/localReproduced/requestBoundaryAligned 仍 false，没有误升成功轴。

## 2. F1 · P1 · fact：新的 eval 剥空白变换不保持语义，且处于正式默认安装路径

### 2.1 实际实现与执行面

位置：`diagnostics/shadowroot-repair-20261020/document-principal.js:1365–1416,1530–1538`。

`stripLargeTrailingRegex` 对长度不少于 100000 的字符串，找末尾两个斜杠；只要位置/间隔符合、斜杠外非空白字符不超过 80，就删除这两斜杠之外**所有**空格、换行、回车、Tab，然后调用 realEval。

`installLargeEvalStrip` 在带 document 的新全局上默认调用（1538），没有 `__watchEval` 开关；它把 globalThis.eval 替换成 wrapper（1411），同时包装 Function.prototype.toString 伪装 native（1410）。最新正式 probe 固定 loadSubScript 该 helper（collector:55），当前 scope 的 helper ref hash 与快照一致，18:12/18:36 两份记录明确该层保留。因此这是被纳入正式 baseline 的默认环境变更，不是孤立未引用的文件。

**覆盖限制：** 最新 raw 没有安装标志、eval enter/return 或输入 hash，所以不能进一步声称“最新 2:3028 错误必然由这层变换造成”。代码默认安装路径已证，特定目标调用是否命中以及造成何种错误仍未知。

### 2.2 静态反例，不执行目标

```js
" ".repeat(100000) + "'a b'.length + /x/.source.length"
```

该输入满足当前长度/末尾斜杠/非空白数量条件。真实 eval 返回 `3 + 1 = 4`；变换会得到：

```js
'ab'.length+/x/.source.length
```

返回 `2 + 1 = 3`。因为实现不识别字符串、注释、token 边界或自动分号规则，“斜杠外空白都不是表达式的一部分”的注释不成立。

即使目标观察样本恰好是数字/逗号/正则，当前 matcher 也没有把可变输入限制为经证明的安全 grammar。测试 `eval-strip-ok 7` 只覆盖作者选择的样本，不能证明任意被接受输入等价。

另外，将原生 eval 换成普通函数，再 `realEval.call`，会令原来 direct eval 的调用不再保有 direct-eval lexical semantics。所谓“还调用真 eval”不代表源程序执行合同未改变；字节索引、耗时与动态源码外观也都可能受影响。

**结论：** 下午不是恢复早上“直接 return 数字”的同一个捷径，但又引入了另一种目标动态源码改写。它至少是需要隔离的实验干预，不是已证的宿主等价修复。不应以它导致的超时/报错位置移动作为 VM 程序正确推进证据。

## 3. F2 · P1/P2 · fact：function 关键字特许门以未归因错误的外形放开修补，不构成宿主缺口证明

位置：`skill/web-reverse/scripts/web_case.py:3735–3752,3816–3857`；`agent-notes/20261021-function-keyword-gate.md`、`20261021-kind-other-gate-trace.md`。

新增布尔路径为：

1. scope 的绑定 source 第 2 行第 3028 列，词法扫描恰好落在 `function` 最后一个字符；
2. side.class == other 且 side.kind == other（3829）；
3. **只要 sourceForm 或 sourceClass 键存在就拒绝**（3831），缺这两字段才可过；
4. 行列一致便返回 repair_submit_host_behavior，取消 no-new-host-surface，允许一处宿主行为改动。

这没有核验异常实际来自那个 source：collector 自己承认 `kind=other` 只表示 sourceName 没命中几个固定片段，真实 sourceName 没有保存；诊断的 sourceSha256 是 scope 的常量，不是抛错脚本内容求得。扫描绑定 source 上碰巧是 `function`，并不能把未归因的控制台错误绑定回该 source。

更关键的是，没有 error name/message、动态 stack、receiver 或实际 property access，尚不知道这里是 SyntaxError、TypeError、跨 compartment 初始化失败，还是其它来源错误。它不是 submit:1:75507，也没有说明缺哪个宿主 API。

**边界判断：** 若人明确授权继续收集该错误的诊断，这可以是一条人工 diagnostic continuation；本审计不把“允许进一步读证据”本身当错误。问题在于它发出的是实际 host behavior repair 动作，并用精确列号与“身份字段缺失”替代了缺口证据。单元测试证明“这张新门会按设计开”，不证明应该修哪个行为或修法等价。不得把 gate 通过计作补环境双条件或业务进展。

这比中午的 55371 例外又增加了一类特征匹配门，但没有增加来源鉴真。准确下一步是保存完整异常身份来归因，不是继续为每个新停止列复制一条放行条件。

## 4. 纠偏确实存在：中午不能原样重报的三项

### 4.1 XHR 默认异步已恢复，缺状态不再默认成功

当前位置：helper `1245–1362`。

- status 缺失/无效回 0，不再转 200（1250–1251）。
- HTTP status >=200 触发 load，status 0 才 error（1256–1259），已修中午 4xx/5xx 误走 error 的问题。
- send 根据 `_async !== false` 判断，只有显式同步才在 send 返回前 finish；缺省异步通过 timer 0（1297–1303,1354–1357）。
- property callbacks 与 addEventListener listeners、loadend 的通知也被补齐。

这些是实质合同纠偏，不能继续说“所有 XHR 默认强制同步”。目前仍未证明已达 full WebIDL/event/parity；本地 fixture handler 和合成 XHR 也不是网络真实性证据。

### 4.2 Observer 已不再同步重入 observe

helper `574–578` 现为仅 armTimer(0)、armTimer(200)，不再 fireNow()。所以中午指出的默认同步通知错误已撤回。保留两个固定 timer 的模型不等于原生 PerformanceObserver 全语义，但至少异步/重入方向改对。

### 4.3 settings FATAL 和 origOpen 的解释更准确

- helper `133–137` 的 settings.server=data 测试地址用于 `MOZ_DISABLE_NONLOCAL_CONNECTIONS` 的离线 harness，阻止 Mozilla Remote Settings 后台同步导致非本地连接 FATAL。没有证据表明这条配置跳过了 Cloudflare/PSA challenge 或改了目标 VM 分支。
- `20261021-baseline-exit-root.md`、`settings-server-skip.md` 将 collector exit 1、CLI JSON 解析失败、引擎/构造器提前结束分开分析，并明确某些退出原因仍分不清，不再全部叫 timeout。
- `origopen-attribution.md` 正确指出 1439 是读取已保存 slot.origOpen 的数据属性，不是 document.open getter 的失败；watchdog 落点不等于该属性根因。

这些提升了诊断质量。但“移除身份文档 event pump 后约 9.1 秒报新错”仍需验证 identity channel 是否真的提交、资源 loader 是否在正确 document 上安装，不能只凭更短墙钟声称修复成功。

## 5. 尚无工具验证的新里程碑

- 午后主要仍是重新绑定 helper 后跑 baseline；本 scope 没有成功 patched/双条件 pairing/确定性 boundary 分类通过。
- 历史 page/cloud FO、iframe/API 的回灌规则仍是离线夹具；没有新证据显示它们被当前目标请求真实消费，更不表示 fresh 响应或同会话清关。
- 依赖 hash/rebind/priorScope 继续有效，能够证明用哪版 helper，但不能让源码变换和 gate 例外变成科学证明。
- 无完成轴误升，也不能据此说“离成功只剩 function 这一处”。目前连 2:3028 的具体异常名和来源都未保存。

## 6. 后续最短建议（本轮不执行）

先把 eval 剥空白层隔离回诊断实验，避免继续污染默认语义；在不改 gate、不再换宿主行为的情况下，补齐 2:3028 的真实 sourceName/source identity、异常名/文本和调用栈，再判定是否真的存在一个可补宿主缺口。继续保留已改正的默认异步 XHR/Observer、scope 指纹和失败不升成功的纪律。

状态最准确表述：**下午修正了一些环境合同和排障归因，但没有新增求解/请求/提交通过证据；新的 eval 源码干预与按未知错误外形定制的 gate，正在再次把实验与修复混在一起。**

证据：`diagnostics/afternoon-audit-20261021/technical/audit-input-hashes.json`、`latest-execution.redacted.json`。未写凭据、Cookie、token 或原始指纹值。
