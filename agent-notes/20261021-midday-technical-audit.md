# Grok 午间增量技术审计（2026-10-21）

## 读取范围与当前结论

仅审计上午报告之后的新改动和最新 12:52 笔记；只读源文件与既有工具产物，不执行目标/补丁/测试/网络，不改 facts、scope、dispatcher。本次锁定 helper SHA-256 为 `f7ea7358e85384f342a5c4b0b77ceec37a0415fe6205060744243c1413d4cbe0`，state 当前 baseline 为 `13a5d2e400e74067934b6155d4063651`，scope `2d6dfc95...`。快照 hash 与脱敏 raw 见文末。

**有实质改进，但仍未到 submit 或业务请求边界。最硬的新问题是把异步 API 改成同步来干预忙循环；Date 的“已确认根因”表述也比现有证据强。**

## 已证实修正，不应继续按旧错批评

1. 旧 `installFastPadEval` 已从当前 helper 删除；正式新全局安装路径不再启用跳过 eval 的捷径。`installEvalProgressWatch` 仅在 `__watchEval` 下启用，当前 baseline 未开。不能再说最新结果由早上的 pad eval 短路直接造成。
2. scope 现在包含 dependencies：helper、Node、CLI、Gecko exe/xul/plugin/mozglue/lib，以及 API/iframe/FO 等静态资源；`host_evidence.py:185–193` 会核验依赖 ref。helper 变更对应新 scopeId，priorScope 保存旧执行链。上午“helper 变了而 scope 恒定”的漏洞已有实际修正。
3. `55371 < 75507` 不再被文案直接写成动态“调用之前”。目前是显式命名的第 55371 列例外。它仍不是 receiver/调用链证据，但不能把旧的列号先后误判原封不动算作新错。
4. 10:32 的 form-create 回执正确地区分 Node 工厂缺 form 与当前 Gecko runner；没有把 Node 的 form 映射补丁当成当前 Gecko 卡点解法。

## 最新真正走到哪

权威文件：`contracts/host-evidence/state.json` → `evidence/host-executions/13a5d2e400e74067934b6155d4063651/execution.json`。

- 最新是 baseline，status failed、exitCode 1、timedOut false。当前 state 没有成功的 patched、pair、classify 结果。
- raw 只有 host-diagnostic 与 summary。诊断仍是 `matched=false,line=1,column=55371,base=object`；side 为 `class=slow-script,kind=other,sourceClass=other,sourceForm=token`，receiverId/access/threw 为空。没有真实 submit host-observation。
- raw 没有 wire/necko/resp。collector 本来也不记录这些请求事件，故“raw 里证书 POST 0 行”是**没有覆盖下的零计数**，不能升格为完整网络观测。当前只能说没有工具证据证明 FO/XHR/submit/证书 POST 已发生。
- `iframe-parent.json` 的 entries=1/observe=1、connected=yes 是本地设施观测；不是 iframe 导航、Turnstile 完成或提交成功。
- 最新 serverAccepted/localReproduced/requestBoundaryAligned 仍为 false；没有误报通关。

## F1 · P1 · fact：异步 API 被改成同步，正式 baseline 已混入非浏览器时序

### XHR

位置：`diagnostics/shadowroot-repair-20261020/document-principal.js:1006–1073,1115–1117`。

`installInlineXHR` 默认安装在页面窗口，不在诊断开关里。send 读取资源 handler 后立即写 readyState=4/status/body，并在 **send 返回前**调用 onreadystatechange/onload/onerror。它不读取 open 的 async 参数，不区分默认 async=true 与显式同步 XHR。

`agent-notes/20261021-inline-xhr.md:5` 明确把该改动解释为“同一次脚本里的等待看不到 setTimeout 回调，所以让 send 返回前完成”，并将其留入正式 baseline。它不是只存在于未执行的独立探针。

正常异步 XHR 的响应回调不能在 send 同一调用栈里被提前执行。旧资源加载器用 task 调度也许还有其它缺陷，但不能由“当前 VM 忙等看不到 callback”推出浏览器本应同步完成。若页面 busy loop 依赖未来 task，其原因还可能是缺资源、返回值、realm、状态或目标自身检测，改变事件循环合同是在绕过条件，不是已证的 native 行为恢复。

此外 `xhrCompletion` 把缺失、0 或负 status 转成 200（1011–1012），将未知/失败值合成为 HTTP 成功；onerror 又被用于 HTTP 4xx/5xx（1067–1068），而真实 XHR 对 HTTP 错误状态仍触发 load，error 属网络/传输错误。当前本地 handler 的映射都显式返回 200，因此尚不能证明缺省 200 分支已影响本轮执行，但实现本身不符合合同。

### PerformanceObserver

位置：同文件 `:393–455`；`agent-notes/20261021-observer-notify.md:5,11`。

`runObserverNotify` 在 observe 返回前直接 fire()，然后才保留 0ms 与 200ms timer。该函数是正式合成 PerformanceObserver 的默认实现，并非 `__watchEval` 下的诊断开关。PerformanceObserver 通知应在异步 performance timeline task 中投递，不能同步重入 observe 调用者。笔记承认该动作是为了让忙循环当场看见 callback；随后慢脚本列从 1337365 变到 55371。

**判断：** 这证明“人为改变通知时序后执行形态变了”，不证明“修复为浏览器语义”。当前正式 baseline 因此已不是 native 时序对照；后面的 Date 因果判断要受此混杂限制。抽出 helper 跑的顺序测试证明 `fire,0,200` 按作者预期发生，不是独立浏览器合同验证。

## F2 · P2 · inference 被写成 fact：Date 根因和“那次 eval 返回”尚未闭合

精确位置：`agent-notes/20261021-window-date-inpage.md:15`：

> 页内时钟让那次 eval 返回了。……跨区 new Date() 是从 55371 退回 1337365 的原因。

支持该假设的真实证据：把 exported chrome current 改为页面 Function 内捕获 RealDate.now 后，正式 slow-script 列确实从 1337365 回到 55371；源码也确实减少了 current 的跨 compartment 调用。这个方向有技术合理性，不能说完全没推进。

但证据仍不足以把它写成已定位根因：

- 最新 `__watchEval` 未开，计数为 0 只表示没采集，不表示 eval 没返回，也不证明某条特定 eval 已返回。
- 两轮 raw 均仅保存慢脚本行列，sourceClass/kind 都为 other，没有 runtime source identity、同一 eval input hash、enter/return 关联或被测 Date 的 compartment/receiver identity。
- 两次都在脚本时限附近失败。跨区 overhead、时钟读数、进度/采样差异都可能改变超时落点，不能仅凭落点替代控制流证明。
- 上游已有同步 XHR/Observer 干预，样本是旧 challenge + 合成时钟。该结论最多适用于当前离线模型，不是当前线上真实 challenge 的根因。

**建议表述：** “页内 current 修改与慢脚本落点恢复相关，怀疑跨 compartment 调用/时钟行为影响了执行；尚未证明同一 eval 返回及其因果链”。不是反证其假设必错，而是拒绝证据不足的定论。

## F3 · P2 · fact：关于 indirect eval 的解释写反了

位置：`agent-notes/20261021-window-date-compartment.md:5`：

> 那是间接 eval，函数会生在调用方作用域。

一般 ECMAScript 语义恰好相反：direct eval 才可能使用调用点 lexical environment；indirect eval 在被调用 eval 函数所属 Realm 的全局环境执行。`host.eval` 究竟是页面原生 eval、继承的沙箱 eval 还是跨 compartment wrapper，必须实际核验，不能从“它是间接调用”直接推导“生在 chrome 调用方作用域”。

替换为页面 Function 的方向可以减少歧义；但 Node 的 new Function 值测试不验证 Firefox Xray/Cu.exportFunction/compartment 行为，也不能倒推原始 host.eval 的 Realm。此处是新的技术解释错误，不等于证明当前 Function 安装方案一定失败。

## 回灌/边界与剩余限制

- 当前 collector 已映射历史 page FO 明文和 cloud FO 明文（`host_submit_collector.py:129–141`），以及保存的 iframe/API 文档。这只是**增加离线 handler 命中能力**，不是实际新 FO 请求出现，更不是服务器返回了这些数据。
- 映射按 method/host/path 形状选择历史第一份正文，不绑定本次 request body、nonce、响应序号。若同形状下一阶段请求出现，会继续回同一旧正文。它可作显式固定夹具实验，但不能用来证明 fresh/live 会话一致性或真实清关；新 scope/依赖 hash 只能证明“这份旧正文没变”，不能证明它适用于当前请求。
- 当前基线仍 blockUnmapped=true。非 baseline 才向 RuyiDOM CLI 传 --allow-network（collector:430–432）；本次没有正式 patched 成功回执。因此并未回到 fresh live 验证。
- performance.now 目前由 Date.now-origin 再钳到 0（helper:342–350），不是严格单调：墙钟回拨时它可以从 40 降回 0。该契约缺陷尚未证明是本次首个卡点，不另当已定位根因。
- 第 55371 列例外现在是明确人为授权，不再伪称真实 submit 双条件。它没有补上 source identity 或缺口类型，只是允许继续改宿主；不要把“门放行了”当作“科学因果已证明”。

## 下一步（本轮不执行）

先把本地干预与浏览器等价修复分开记账，保留真正异步的对照；针对 Date 假设采集同一输入的 eval return/compartment/时钟调用证据，再决定是否留补丁。请求侧要加实际 handler/wire 事件后，才能判断历史资源是否真的被消费、FO 是否出现及其顺序，不能再用没有请求记录的 raw 支撑完整网络结论。

证据：`diagnostics/midday-audit-20261021/technical/audit-input-hashes.json`、`latest-execution.redacted.json`。本轮未输出凭据、Cookie、token 或指纹原值。
