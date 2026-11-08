# 2026-09-30 观测摘要与 instrumentation 回执修复

## 范围与完成状态

本切片为离线证据可靠性修复，不新建 action、不增加 v3 budget、不访问目标、不运行目标 JS、不写 case/facts，不重新登记或修改历史 trace/claim/receipt。完成后仍处于原有 hold；业务通过未证明。未提交、未推送。

## 可复现摘要

新增 `skill/web-reverse/scripts/diagnostic_summary.py`，直接从已有受限 `engine-stdout.json` 生成新派生摘要，并验证 execution receipt 的 stdout 路径、SHA-256 与 exit code。相对路径必须显式指定 project，输出以 `open('x')` 排他创建，不能覆盖原始证据或既有摘要。

本轮源目录：`workspace/psa_solve/evidence/web/diagnostic-instrumentation-v2/restricted/05c67ac6c8c24b38aa03d866258971ad/`。

新派生文件：`boundary-summary.offline-repair.json`；原 `boundary-summary.json` 与 `boundary-summary.corrected.json` 保持不变。

实测结果：

- `harnessHealthy=true`，`forms=0`、`submits=0`，没有 cert POST 或具备 document destination 证据的 cert document POST；没有独立业务内容回读，`businessAccepted=false/not-proven` 不是已证明服务端拒绝。
- `cookieBuckets.site` 确实观察到 `cf_clearance`；legacy `cookieNames` 与 plain 分区不含它。各分区独立输出，错误、未观测与正常空数组分开。
- 历史 `ifr=2`、`tsFrame=1`；最终顶层 light-DOM iframe count 为 `0`。这些描述不同时间/作用域，最终快照不能否定历史或跨域文档存在。
- `cfLog(policy=7)` 证明 **1 个嵌套文档 GET 200 response 与 1 个 stop**，stream stop/channel status 为 `0`。不能把 response+stop 当成两个 frame。
- `respLog` 是过滤日志，不能单靠它否定嵌套文档，也不能将它与 cfLog 的局部序号拼成全局请求顺序；重复模板路径的多个 response 不能靠一个 stop 证明逐项加载成功。
- Worker/Blob/WebCrypto 包装仍标为 `probe-disabled/null`，计数为零不解释为路径不存在；摘要不复制 URL、nonce、Cookie 值或原始指纹值。

复现（只读已有日志、写新派生文件）：

```powershell
& 'D:\reverse_ENV\.venv\Scripts\python.exe' 'D:\reverse_ENV\skill\web-reverse\scripts\diagnostic_summary.py' `
  --project 'D:\reverse_ENV\workspace\psa_solve' `
  --input '<上述源目录绝对路径>\engine-stdout.json' `
  --execution-receipt '<上述源目录绝对路径>\execution-receipt.json' `
  --output '<不存在的新派生文件绝对路径>'
```

## 回执完整性最小修复

核查确认：两个 instrumentation adapter 的 `record` 原本已调用 `validate_claim(fresh=False)`，会重验 artifact/runtime/protected hash；本轮没有重写框架，只补了以下遗漏：

- 固定 environment 及 runner/clean/profile 的路径和 reviewed hash 必须与仓库 profile 一致，即便 caller 重算 sidecar digest 也不能自换引用。
- 可选 `cookieFile` 必须在 source inventory 中，不能只绑定 challenge/script/input 却遗漏实际 Cookie 输入。
- spawn 前 `validate_claim(fresh=True)` 自身拒绝过期 `executeBefore`，不只依赖 wrapper 记得检查。
- 未启动回执的 `endedAt` 也必须不早于 claim。实际启动晚于截止仍拒绝；及时启动后晚于截止结束或记录则允许完成记账。失败不退款，不产生新 budget。

## 历史执行与当前 case 分层

v2 历史执行：PID `52968`，开始 `2026-09-30T10:18:32.958538+00:00`，结束 `10:19:04.969078+00:00`，exit `0`；启动截止 `10:19:22.320179+00:00`，已于 `10:20:51.352947+00:00` 登记为 `executed-hold`。

当前 execution receipt 的 SHA 与历史 receipt 一致，engine stdout 的 SHA 与 execution 一致。当前 facts SHA 仍等于 claim 的 `586e8577d184e35de9c4795dd28af25b69043ca7bee400ce67a8b63fe489a2cf`；本切片未修改 facts。

当前 `web-case.json` 已相对 claim 变化，不能把历史 protected hash 宣称为永恒 current equality：

- claim case SHA：`2888bc8791cead12acc3847d6fba7e74053e8cd1c97f6327889e4da0054cac14`
- current case SHA：`04207d8f09e7016da5df391bcf69849a7894741281922a1ec22903fd95e69727`
- 因此本轮严格 current `validate_claim(fresh=False)` 返回 `protected hash binding mismatch`；不 retrovalidate 成 current success，也不改历史 receipt。这与已证实匹配的 stdout/execution hash 是不同轴。

主线程确认这是后续由 `next` 要求的显式 legacy metadata migration；权威产物为 `workspace/psa_solve/contracts/case-metadata.v1.json`（`contractRevision=1`、`caseClass=challenge`、`updatedAt=2026-09-30T10:37:57Z`）。已只读确认 `web-case.updatedAt` 也是该值。claim 只有旧 case hash，没有保存完整旧 case 字节快照，因此不能声称已完整比较全部差异字段。迁移不执行目标，不改变业务成功或 facts；当前校验拒绝不等同于当时 record 失败，不据此认定历史证据被篡改。

## 测试与下一步

`test_diagnostic_instrumentation.py` 已彻底移除 workspace receipt 的创建/删除；变更性测试使用系统 TemporaryDirectory 下的独立 ROOT/workspace、合成 reviewed 字节与 runtime hash、受控时钟。生产 profile 字节测试只读 asset，不读实时 case/facts 或依赖预算未消耗。

- instrumentation/摘要：**26 tests / OK**；行为覆盖 v1/v2 的真实 claim→artifact/runtime/log/sidecar tamper→record 拒绝、过期启动拒绝及不退款、及时启动晚记账允许、未启动记账、业务字段拒绝、分区 Cookie、历史/最终 DOM/网络分层与摘要输出保护。
- web-reverse 全套：**122 tests / OK**。原 37 项浅检查换成 26 项行为测试，数量下降不代表遗漏旧 budget 状态约束。
- 既有 baseline wrapper：**9 tests / OK**；skill validator：pass；本切片指定文件 `git diff --check` 无输出。

测试命令：`python -m unittest discover -s skill/web-reverse/tests -p test_diagnostic_instrumentation.py`；全套将 pattern 换为 `test_*.py`。wrapper 命令：`python -m unittest discover -s workspace/psa_solve/agent-notes -p test_20260930_clean_baseline_wrapper.py`。这里的 Python 均为仓库 `.venv/Scripts/python.exe`。

下一步维持主线程已选的 **response → DOM causal receipt**，不是重测 getter；观察器能力、响应进入哪个 realm、何时创建/移除 iframe/form/submit 与网络提交必须建立同观测合同的因果对应。业务完成仍缺真实 cert document POST 和同会话正确内容回读。
