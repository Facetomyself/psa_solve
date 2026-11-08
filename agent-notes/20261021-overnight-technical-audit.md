# Grok 通宵技术进度与新误判审计（2026-10-21）

## 范围与权威快照

仅静态读取当前状态、已有工具 raw 和源码；不执行目标、实验、网络或修复，不修改 facts/dispatcher，不干扰进程。本轮不使用 10 月 20 日 16:41 的旧 last-copy。权威 state 已指向 **08:08:35 启动的 `ceec274d86774db4b94630cb1af653c7`**，不是 07:41 笔记里最后一条 `5605412...`。读取期间文件仍可能被 Grok 更新，本报告以 `diagnostics/overnight-audit-20261021/technical/audit-input-hashes.json` 及 execution-summary 快照为界。

## 实际进度：局部执行前移，未到 submit 或新业务边界

- 午夜以来现有正式 host execution 共 **11 次，全部 baseline、同一 submit scope、全部 exitCode=1/status=failed/timedOut=false**。未见该 scope 的 patched、pair 或 classify 完成回执。
- 最新 raw 只有两行：`host-diagnostic`、`summary`。diagnostic 为 `matched=false,line=1,column=55371`；side 报 `class=slow-script,kind=other`，`receiverId/access/threw=null`。不是 `HTMLFormElement.submit` 真实 receiver/callsite 观察。
- 所有这 11 份 raw 都没有 host-observation/wire/necko/resp。注意这也意味着正式采集器**没有覆盖请求观测**，不能反过来声称用 raw 证明“整个运行确无任何请求”。只能确认没有提交边界证据。
- 两份最新执行 `5605412...` 与 `ceec274...` 的 raw SHA-256 完全相同：07:38 到 08:08 这次正式重跑没有产生新的正式可比证据。
- 本地探针记录过真实资源条目、PerformanceObserver 回调、RTC offer 兑现、setLocalDescription、连接过的 iframe 父节点，属于有用的本地设施诊断。当前 `iframe-parent.json` 仍为 connected=yes，但不代表 iframe 导航/Turnstile/证书表单或业务成功。
- 当前 serverAccepted/localReproduced/requestBoundaryAligned 全为 false，未见误升成功轴；工具仍拒绝把 summary.ok=true、failed execution 当通过，这一点比昨天更可靠。

## P1｜新增 eval 捷径非语义等价，却默认进入正式 baseline

**位置：** `diagnostics/shadowroot-repair-20261020/document-principal.js:829–872,1017–1021`；`agent-notes/20261021-form-gate-probe.md:156–162`。

`installFastPadEval` 对长度不少于 100000 的 eval 输入，只检查首 220 或尾 220 个字符；正则看见 `0, /.*Abcd.*/, <数字>` 就直接 return 该数字，不执行完整字符串。代码还替换 Function.prototype.toString 及 eval.toString 来模拟 native 外观。

该安装在新页面全局建立后无条件调用（1020），**不在 `__watchEval` 诊断开关内**。collector 的正式 probe 又固定 loadSubScript 该 helper，所以不是“只写了未运行的独立试验”。笔记明确确认这条修改已进入 c9e/560 两次正式 baseline；当前 ceec 仍走同一加载路径。

静态反例，无需执行目标：

```js
"0, /.*Abcd.*/, 7" + " ".repeat(300)
  + "; globalThis.__sideEffect = 1; 9" + " ".repeat(100000)
```

首 220 字符匹配，所以 wrapper 返回 7 并跳过副作用；真实 eval 要执行后续语句并返回 9。只检查片段不能证明整份字符串中间全为空白。即使样本里确实多为空白，当前实现也没有完成这种证明。

此外，把原生 direct eval 替换成普通 wrapper，再以 `real.apply` 回退，会把原来依赖调用点 lexical environment 的 direct eval 转成 indirect eval；“未命中捷径就完全等同 native eval”也不成立。

**影响：** 这是改写目标 VM 动态程序的执行结果，而不是根据 browser fact 补一个缺失宿主行为。慢脚本报错从嵌套 eval 末列移到解释器列，不可当作语义正确的环境修复推进；native toString 也不证明行为等价。

**建议：** 后续求解工作应先撤销这个捷径，回到真实 eval，再诊断其循环/输入/计时/realm 原因。当前审计不执行撤销，也不拿新卡点当“补对了”的证明。

## P1｜submit 修复授权把源码列序当成动态前置关系，且没有证明错误来自该 source

**位置：** `skill/web-reverse/scripts/web_case.py:3735–3825`。

新增 `_out_of_file_slow_script` 在正式 execution 校验失败后给出 `repair_submit_host_behavior`。原来接受源文件外列号，最新又接受同一行 `column < submitColumn`（3783–3789），理由写成“源文件之内、调用点之前”（3801）。

**两个证据漏洞：**

1. JavaScript 同一行列号更小只代表文本位置，不代表先于 submit 的动态执行；解释器循环、函数声明位置、分支/异步回调都能打破此推断。该函数没有控制流或动态调用链证明。
2. 当前 side 的 `kind=other`，而 gate 只检查 `class=slow-script` 与行列一致（3793–3798），不核对实际 sourceName/source hash。raw 里的 sourceSha256 由 collector 用 scope 的常量填入，不是由警告源内容求出。因此 `1:55371` 即使小于 75507，也尚未证明它是这份 orchestrate 内的那一列，更没有证明是 submit 的原因。

这条门没有伪造 submit observation，也没有写完成轴，这是正确限制；但它**确实以不具归因能力的诊断放开宿主改动**。同 scope 并不等于同 receiver，也不等于已经具备双条件。本轮仅能认定“慢脚本仍在，submit 未观察到”，不能认定“已定位 submit 前置宿主缺口”。

## P1｜helper 与实际 Gecko 执行依赖未纳入 scope 指纹，`scope 未变` 掩盖实验基线已变

**位置：** `host_submit_collector.py:18–24,40,291–315`；`contracts/host-evidence/scope.json`；最新 `execution.json:13–31`。

scope 锁定 runner=Python collector、runtime=Python executable、input/source/config 五项。但 collector 真实执行路径还固定依赖：

- `document-principal.js`（40 行载入，通宵持续修改，当前约 43KB）；
- Node executable 和 RuyiDOM `dist/cli.js`，其下真实 Gecko/xpcshell 和 engine/module；
- 挑战 HTML（collector 自有 PAGE_SHA256 另验，值得保留）。

主 scope 和 execution receipt 没有 helper/Node/CLI/engine/module 的内容指纹。`for path ... is_file()` 只查存在，不验这些依赖字节。**因此同样的 scopeId、runner/runtime/input/source/config 五份绑定全部一致，仍可执行不同 eval、时钟、RTC、prompt 与文档行为。** 最新代码足以直接证明这个缺口，无需跑目标。

这与昨日泛泛“换 runner”不是同一问题：昨晚已启用正式 host 工具链，但动态加载依赖漏锁使其不能保证声称的“同 scope 基线”。08:08 helper 修改后仍用同一个 scope 重跑就是本例。

建议：为正式运行绑定递归依赖 manifest，至少 helper、实际 Node/CLI/Gecko、所改 engine module/prefs；变更后生成新修复 revision，并保留 baseline/patched 对照而非全部覆盖 baseline slot。

## 不应认作新误判的部分与限制

- 固定输入明确来自 **10 月 5 日**历史 challenge，笔记承认 clock=skew，且 baseline 刻意 blockUnmapped=true、不传 --allow-network。它不是 fresh live，也不能证明当前线上求解，但这次未发现 Grok 声称它已经 fresh；故记为验证范围限制，不把“旧输入”重复列作新增事实错误。
- `Date.now` 按历史页面时间字段锚定、原生 host prompt 自动选默认按钮等修改会改变观察条件；这些是当前诊断模型的一部分，不能推广到真实运行时。但目前未有工具结果证明它们是最先根因，不把相关猜测另算已定位缺陷。
- collector 将子进程 stdout/stderr 接 DEVNULL（315），所以外层文件空不是页面无错/进程未启动证据；笔记对此已有正确说明。
- 工具 exitCode=1 是 collector 的“未产生 host-observation”出口（336），不直接等于 Gecko 崩溃。当前失败记录并不证明引擎能力不够。
- 通宵不全是空转：错误类别和本地设施确有变化；但从正式目标证据看，11 次同 scope baseline 都失败，07:38 与 08:08 连 raw 都相同，尚无 submit/request/业务推进，不能称“快清关了”。

## 收口

先纠正污染 baseline 的 eval 捷径与依赖漏锁，再建立能观察真实 source/receiver/callsite 的工具结果；不要为了让第 75507 列命中继续放宽门禁。当前最准确状态：**局部本地运行诊断在推进，submit 路径仍未触达；新的语义捷径和错误授权判断正在降低后续证据可信度。**

中间证据：`diagnostics/overnight-audit-20261021/technical/execution-summary.redacted.json`。无凭据、Cookie、token 或原始指纹值写入本报告。
