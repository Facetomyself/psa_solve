# 新增诊断包装清理：隔离候选与门禁核查

## 本轮结果

- 状态：`prepared-static-verified / online-gate-blocked`。只完成可回退候选和静态验证；没有运行在线目标，没有开启真实插桩，更没有新的业务验收结果。
- 项目 `main` 无 upstream、无 remote，因此没有可按当前 upstream 执行的 fetch。未重置任何既有改动，未提交/推送。
- 原始 `diagnostics/ruyidom_bridge.js` 原样保留，字节备份和独立候选在 `diagnostics/clean-baseline-20260930/`。
- 只移除原脚本 1362–1375 行的连续 8,029 字节：Worker 原型/实例包装、同步 blob 读取与引导、createObjectURL 文本检查、BroadcastChannel 探针、Blob 源码前置、五个 crypto.subtle 包装。未新增宿主行为。
- 改动区间前后逐字节一致，SHA-256 收据在 `manifest.json`。UA、h3 映射、导航修补、交互路径和其他已有代码全部保留。
- 原版/候选外层 JS、两份拼接后的内层 hook 共 **4 项语法检查通过**。这是解析检查，不是完整单元测试、引擎 smoke、线上测试或业务验收。
- RuyiDOM CLI `status` 通过，锁定文件 hash 匹配，实际 runtime 为 Firefox 135 base。没有换核；发行版 UA 覆盖不等于底层版本改变。

## 证据

- `diagnostics/clean-baseline-20260930/manifest.json`：hash、删除边界、保留项和检查结果。
- `diagnostics/clean-baseline-20260930/runtime-status.json`：本轮只读运行时完整性检查。
- `diagnostics/clean-baseline-20260930/ruyidom_bridge.original.js`：字节原样备份。
- `diagnostics/clean-baseline-20260930/ruyidom_bridge.clean.js`：本轮隔离候选。
- `agent-notes/20260930-prepare-clean-baseline.py`：可复现构建/静态检查，拒绝覆盖不一致备份；不执行目标。
- `agent-notes/20260930-clean-baseline-state.json`：机器状态。此文件仅是本轮操作回执，不替代 `web-case.json` 或 dispatcher facts。

## 精确门禁

本轮真实 `web_case.py next` 输出：`action=refuse_host_enumeration`、`turnGate=blocked`，`docs.read=[docs/web/environment-patch.md]`。

这不仅是推测“blocked 不能干活”：

1. `skill/web-reverse/SKILL.md:45` 明确 blocked 回合只执行返回的这一个 action。
2. 同文件 `:56` 规定 stop-search 只有新外部请求边界证据才能解除；`restore-live` 适用于离线残留，`restore-real` 适用于虚拟字段残留。
3. `skill/web-env-patcher/references/pause-boundaries.md:79-89` 定义三个入口；`:93-97` 限定暂停时整理缺失项和保留结论。
4. `skill/web-reverse/references/decision-points.md:93-100` 同样没有“保留 stop-search 的显式 cleanup baseline”动作；dispatcher 对应 `scripts/web_case.py:2095,2133`。

当前事实已经是 live，无本轮新发现的上述虚拟字段需要恢复，不能为了拿到 run action 把 facts 谎报成 restore-live/restore-real 或写 ok。用户授权清理的意图已记录，但本轮明确要求“按现有门禁”；因此隔离静态候选已经准备，真实在线与后续插桩尚未开始。不是缺账号，也不是要求用户再说一次继续。

## 最小合法解锁建议

治理层显式增加或批准一个 **一次性 diagnostic-cleanup-baseline action**，与 `environment_patch` 分开：

- 输入必须是 archived runner hash、候选 hash、允许删除区间与不变收据；只允许移除已命名诊断干预，不能增加 getter/常量/目标代码 patch。
- 允许保留 `experimentHygiene=stop-search` 和所有业务验收字段；一次执行预算，不自动回到 host 枚举。
- fresh live/session-provenance 必须完整，真实双条件补丁保留，禁止异会话 response 重放。
- 结果按 `harnessHealthy` 与 `businessAccepted` 分轴记录；没有 form 是业务分支结果，不必然是 harness 故障。
- 完成后返回同一 hold；只有独立外部边界证据才另行决定路线。

本轮没有改 dispatcher 或技能治理，避免把“执行诊断清理”扩展成未经审阅的门禁重写。

## 就绪调用模板（未执行）

候选解析已验证，但输入材料仍须在获合法 action 后同会话新鲜生成。以下路径中的 `fresh-input.json` **本轮未创建**，不能拿 09-30 旧 challenge 直接冒充新鲜基线。

```powershell
$env:MOZ_FORCE_DISABLE_E10S = '1'
$env:MOZ_FORCE_DISABLE_FISSION = '1'
& 'D:\reverse_ENV\tools\node\node.exe' 'D:\reverse_ENV\mcp\ruyidom-mcp\dist\cli.js' run `
  --script 'D:\reverse_ENV\workspace\psa_solve\diagnostics\clean-baseline-20260930\ruyidom_bridge.clean.js' `
  --input-file 'D:\reverse_ENV\workspace\psa_solve\diagnostics\clean-baseline-20260930\fresh-input.json' `
  --timeout-seconds 120 --allow-network
```

正式执行包装还应将 stdout/stderr 原样存入受限日志，校验输入 provenance、不含 foResponseManifest 异会话回放、hash 锁及真实网络选项；上面是调用模板，不是已跑成功的命令记录。

## 后续插桩合同（设计，未执行）

1. 先得到合法且健康的本轮基线。新鲜有头 browser fact 仍走锁定 RuyiTrace；不开 debugger，不换 runtime。
2. top-page、Turnstile iframe、blob-worker 三个 realm 的可观测能力分别做无敏感内容的计数/边界能力测试；不可见时写 unknown，不写 0。
3. 仅比较外部请求顺序、方法、角色、响应状态/长度类、form 创建/submit、document POST 与业务回读；不做密文首字节评分，不动 VM。
4. 先测观察器是否改变边界；能力/干扰未知时不把零调用升格为“该路径不存在”。
5. 保留有头和本地独立 session provenance，不跨会话灌响应；以最早可证实外部边界差异定位，不把响应长度类别当成功语义。

## 仍然存在的观察局限

- 候选仅清理新增包装，旧 atob、Map、RTC、导航等观察还在；不能叫“完全无插桩浏览器”。
- 去掉 Worker/Blob/subtle 包装后旧摘要里的相应计数器默认 0 不再是测量结果。后续边界表必须把它们标 `not-observed/probe-disabled`，不能据 0 继续推断消息/加密没有发生。
- 当前最晚 runtime 结论仍属于先前受探针影响的会话；本轮没有新 forms/submits/业务状态读数。
- `serverAccepted=false`、`requestBoundaryAligned=false`、`stop-search` 保持原样。没有提交或推送。

## 执行准备增量（等待一次性 action 审阅完成）

- 新增 `agent-notes/20260930-clean-baseline-wrapper.py`：默认 `preflight` 不接触目标网络；`fetch` 与 `run` 必须显式调用。`run` 只执行治理 claim 给出的固定 argv，不提供任意脚本入口。
- 原始材料/日志统一写 `evidence/web/diagnostic-cleanup-baseline/restricted/<session>/`，位于已有 Git ignore 范围；不回传 URL、Cookie、token、指纹值。
- 新 fetch 保留历史 urllib、UA135、同类代理继承和 30s 窗口、既有点击/轨迹；不更换 TLS 实现、不切换执行核。只复用已授权目标 URL，不复用旧 cookie/body/script。
- 与历史脚本的不同：一次性新目录、CookieJar、403 与脚本 200/非空/Cookie 校验、缺脚本即停、无旧文件兜底、产物哈希与逻辑会话收据。因此这不是严格“只有 runner 一变量”的实验；也不是从获取到提交全程同 Gecko/TLS 的基线。
- wrapper 在 claim 之后、spawn 之前复核保护文件、runtime、原版/候选、provenance/input/artifact hash；持久化 wrapper/CLI PID、reserved/running/exited 状态，防止等待期间重复启动。
- 结果分 `harnessHealthy` 与 `businessAccepted`：无 form 不自动判工具失败；Cookie 或 submit 不自动判业务通过；移除的 Worker/Blob/subtle 探针报告 `probe-disabled/null`。
- 离线单元验证 **9 tests / OK**：覆盖无 form/有 Cookie/有 submit 不误报通过、禁用探针、timeout/输出缺失/探针失败、缺脚本拒绝与相对脚本 URL。没有借离线单元测试执行目标 JS。
- 复核原 run `rt_20260929103550_341b734038`：RuyiTrace `capture_status` 返回 completed；系统未见 ruyijs/firefox/plugin-container 活进程，没有可复用浏览器句柄。第一次 status 因项目参数需目录名而返回 PROJECT_INVALID，改为 `psa_solve` 后成功；未启动新浏览器。
- 当前无 proxy 环境变量；没有线上出口探测，也未更改系统/TUN。实际出口一致性只能在后续收据中有限说明，不能据环境变量为空声称没有 TUN。
- 当前网络准备尚未执行；等待治理 action 完成测试并获主线程放行，再先 fetch/validate、后 claim，失败的输入准备不消耗引擎运行预算。
