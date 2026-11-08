# Grok 夜间运行态与时间线审计 / 2026-10-21

## 核验范围

08:32–08:36 +08:00 的只读快照；主线程已给本拍 repair_submit_host_behavior / blocked，本切片没有 next、记账、修补、重跑、终止或恢复任何任务。只读CIM进程、项目正式执行回执/状态、指定Grok会话元数据和日志目录时间。没有读取/保存会话消息正文、完整进程命令、Cookie/token或指纹原值。

机器证据位于 `diagnostics/overnight-audit-20261021/runtime/`：`processes.redacted.json`、`session-activity.redacted.json`、`execution-timeline.redacted.json`。该最后一个JSON保存逐run路径、hash和时间，可复核下面的计数。

## 1. 现在谁还活着

- **fact**：Grok主进程 PID3592 自2026-10-20 18:53:35存活。直接子进程为3个常驻MCP：ruyidom PID32960、ruyitrace PID43920、v8trace PID53716。它们的存活只证明控制面服务在线，不证明正在执行目标。
- **fact**：进程快照未发现psa_solve的runner，也没有xpcshell/firefox目标进程。最新正式collector PID17036已不在运行。没有可续poll的项目执行句柄，没有调用restart/status触发运行。
- **fact**：`contracts/host-evidence/state.json`为status=failed、pid=null，current指向ceec274d...的baseline execution；与操作系统进程状态一致。
- **fact**：Grok主会话与一个08:17创建的subagent仍有08:34以后的元数据/工具terminal文件更新，说明会话层仍在活动；不等于目标持续运行，也不够据此确定正在等待哪个模型请求。
- **unknown**：主客户端是否正在采样、等待模型网络、只读分析或做其它工具工作，不能只用grok.exe存活或summary更新时间判定。未读取全部会话正文，不宣称其已挂死。

## 2. 正式collector实际跑了多少

统计窗从10月20日22:33（工具硬化后）到本次快照，共16份正式host execution：3 completed、13 failed。午夜后共11份，全部属于同一个submit scope `9a0d32e12aad...`，全部为baseline，全部status=failed/exitCode=1/timedOut=false。

| 阶段 | 正式执行 | 状态 | 时间范围 |
|---|---:|---|---|
| 首个performance scope | 3 | 1 completed / 2 failed | 23:20–23:42 |
| 新performance scope | 2 | 2 completed | 23:48–23:49 |
| submit scope | 11 | 11 failed | 00:12–08:08 |

**关键口径**：11次submit正式collector的receipt elapsed累计约207.4秒，不是8小时。该数只覆盖这11个正式collector父进程的开始/结束时间，**不涵盖夜间临时探针、未登记helper运行、模型思考、工具读写与人工等待**；不能据此倒推整夜目标总时长、CPU消耗或模型总算力。

同submit scope的runner/source/input/config直接绑定hash各始终只有1种，但helper `document-principal.js` 持续变更。相同scope/hash不等于完整传递依赖和行为真的未变；helper漏绑的技术风险由另一审计切片负责，不在这里凭进程计数下根因结论。

## 3. 最新可证实时间线

- 00:12：开始submit正式baseline阶段；之后没有一份patched正式execution。
- 02:52：`agent-notes/20261021-submit-path-probe.md`落盘；其记述官方baseline仍exit1，且“没有submit调用”不是submit API缺失的直接观测。
- 05:32:03–05:32:23：76471063...失败，约19.731秒。
- 06:57:48–06:58:08：d05075ea...失败，约19.719秒。
- 07:36:51–07:37:11：c9e876f...失败，约19.703秒。
- 07:38:22–07:38:42：5605412...失败，约19.706秒。
- 07:41:15：`agent-notes/20261021-form-gate-probe.md`最后修改；本轮只按其中回执/阶段摘要读，不把叙述本身当工具成功。
- 08:08:15：`document-principal.js`修改；08:08:35–08:08:58最新ceec274d...正式baseline失败，约22.714秒，exit1/timedOut=false。
- 08:08:57：`iframe-parent.json`刷新，摘要为enter/leave=0，部分observe计数存在；这只是helper诊断文件，不是业务提交/读回。
- 08:35前后：Grok主会话/新subagent仍活动，但目标runner已经不在运行；未见08:08:58后的新正式collector终态。

精确lastActiveAt和快照时间随当前会话继续更新，以机器证据的checkedAt为准，不把本报告当锁住未来状态。

## 4. 是有效推进，还是整夜空转

**fact**：不能说“一整晚目标一直在跑”——正式目标运行是11次短collector执行，当前已无目标进程。

**fact**：也不能说“11次都是完全相同未改动的重跑”——helper确实被改过，笔记中的错误归因从prompter、泵、warning采集走到slow-script/source-column。技术上有诊断与错误边界变化，不能用全部exit1抹掉这些局部证据。

**fact**：从请求/业务效果看，午夜submit同scope的正式执行没有成功终态，没有patched对照、没有证书document POST/readback的正式结果，属于长时间反复失败与诊断迭代，尚不是目标业务推进。

**inference**：这里有低效重复风险，尤其同scope反复约20秒失败，却不断在辅助层解释当前错误。要认定“纯空转”仍需证明输入/完整依赖/观测口径均无变化且无新证据；现有记录不满足该强断言。更准确分类是“未取得目标边界突破的重复失败，夹杂真实但未闭环的定位进展”。

**unknown**：临时探针总次数、整夜所有工具调用/模型tokens、每次是否值得重跑，当前保留chat经历compaction，不足以精确统计。没有用summary.num_messages或当前chat行数冒充整夜次数。

## 5. 常驻与错误预算

常驻的3个MCP是正常控制面，不是跑挂的psa守护runner；未发现需要终止的psa残留。最新timedOut=false表示collector自行exit1，不是外层timeout杀进程；内部slow-script看门狗是另一层错误，不能混写成外层timeout。

当前读取的夜间笔记未显示“耗尽一次任务预算所以不能继续”的实际运行态阻塞，主阻塞是失败baseline/调用点未到达。它们反复引用allowed action，但不能由这些笔记反推用户限定了任务次数。历史自设次数/15秒限制早已被移除，不能再拿旧报告解释当前停点。

## 6. 限制与建议

last-copy仍停在10月20日16:41，不代表夜间新会话；本轮依据实际Grok会话目录元数据识别活动，不从旧对话推断新结论。会话有compaction，因此仅保存当前快照行类型计数和terminal文件时间，不宣称完整回合/工具总数。

下一步应优先让技术侧核实helper传递依赖绑定及slow-script与submit调用点的合法因果，而不是因为Grok进程还活着继续等待“目标完成”。本切片不执行该建议，不恢复目标，也不干扰当前Grok活动。
