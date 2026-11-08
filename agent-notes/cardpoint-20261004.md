# 新卡点分析（2026-10-04）

## 判定

相对 2026-10-03 已知的“Node 少 iframe/响应驱动执行面”假设，最新卡点不是又一个可补的 DOM/Window host API：独立 iframe realm 已进入生产离线诊断 runtime，但实际执行仍以同级 `TypeError` 停在构造器调用，没到 `PQak3` 的真实 define、FO send 或 response boundary。现在证据能支持的根因收敛为：执行器缺少触发该构造器的真实 challenge/DOM 生命周期输入（尤其资源/响应驱动的状态），而不是 realm 隔离本身，也不是 `PQak3` 可直接硬编码。

## 新旧差异

- 既有结论：Turnstile iframe inline script 被 Node 当单一 global 执行；`PQak3` 仅被读取、没有 define；需迁移 iframe realm、DOM/message 和 FO response callback 生命周期。
- 新增实验：已在 `runtime/run.js frame` 建立独立 `vm.Context`，装入同一份 238636-byte inline script；`frameEval=ok`、`_cf_chl_opt` key 数 21→37，但 `framePqOwn=false`、`framePqType=undefined`、`parentPqOwn=false`。
- 新卡点：抛错变为 `TypeError: h[bb(...)] is not a constructor`，但异常类别与此前 DOM/状态 TypeError 同级；`parentPostMessageCount=0`、`sendCount=0`、`boundary=boundary-unchanged`。因此“独立 iframe realm 可解决 PQak3”已被该 canary 否定，且当前缺少能把该 constructor 解析到真实 producer/生命周期的证据。
- 注意：这不证明需要任意补 `postMessage`、`querySelector`、`innerText`、构造器或 `PQak3`；也未证明 iframe realm 本身完整。只能说这一刀未改变可验收边界。

## 状态与风险

- 最新材料/状态文件更新时间为 2026-10-04 00:32（本机时间）；`workspace.json` 内容仍停在 2026-10-03：`updatedAt=2026-10-03T08:16:02Z`、`next=refuse_host_enumeration`，slice 列表未登记 `slice-node-iframe-realm`，三件套与 progress 仅追加了 10-03 结果，存在状态账本滞后。
- `analysis-progress.md`、`next-plan.md`、`triage.md` 已记下 constructor TypeError 与停止条件；旧 `next-plan` 顶部 yQYB9 object 卡点、旧三件套的早期“注册段待定位”仍在，容易和当前 source-aligned `PQak3` / execution-boundary 结论冲突，需后续治理但不是本次卡点的证据。
- 无 2026-10-04 新增 `diagnostics/` 或 `temp/` 运行产物。最新直接证据为 `agent-notes/20261003-node-iframe-realm.md`，修改时间 2026-10-04 00:32；关联 frame 行为事实见 `agent-notes/20261003-turnstile-frame-fact.md` 与 `agent-notes/20261003-node-dynamic-context.md`。
- 业务验收仍未闭合：`requestBoundaryAligned=false`、`localReproduced=false`、`serverAccepted=false`；无同 lease 的约 5 秒业务 readback 200。Browser fact 仍是 Firefox/RuyiTrace 已到 5×FO、clearance 名、cert POST 200；不能据此声称当前 solve 成功。

## 建议下一步

1. 先把 `workspace.json` 补记本次离线 canary slice 与证据路径，并统一 `next-plan.md`、`triage.md`、`report.md` 的当前根因表述；旧 yQYB9/object 不再作现行首要卡点。
2. 在 `stop-search/refuse_host_enumeration` 规则内不要继续试邻近 host getter 或伪造 constructor/message/DOM。下一次实验只能由新 browser fact 直接约束：定位真实 iframe 构造点的 receiver/property/source-site 与其所需输入，或取得同一 fresh lease 的 response/callback 生命周期证据；缺证据就维持 blocked。
3. 不改 `environmentPatchGate`、parity、`serverAccepted` 等验收标记；在真实 request boundary 到达前不得进入业务 readback。

## 证据

- `workspace.json`：状态账本仍记录 `next=refuse_host_enumeration`，但缺少本轮 iframe slice。
- `analysis-progress.md` 第 461-466 行；`next-plan.md` 第 107-111 行；`triage.md` 第 114-118 行。
- `agent-notes/20261003-node-iframe-realm.md`：独立 realm canary 指标、TypeError、未发请求及停止条件。
- `agent-notes/20261003-turnstile-frame-fact.md`、`agent-notes/20261003-node-dynamic-context.md`：inline script 与 `PQak3` 静态/动态上下文边界。
- 最近 diagnostics 文件为 `diagnostics/performance-entries-canary/` 下 2026-10-03 23:24 文件；temp 无 2026-10-04 更新文件。
