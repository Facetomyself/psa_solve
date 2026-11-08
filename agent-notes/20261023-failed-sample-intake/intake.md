# 2026-10-23 原始失败样本 intake

## 范围与调度
仅执行 `web_case.py next` 盖章的 `migrate_contracts`，`turnGate=blocked`；未再次运行 `next`，未启动 Grok、未跑 target、未联网、未 patch。caseClass 保持 `challenge`。

## 合同迁移回执
执行 `migrate-contracts --apply --case-class challenge --expected-revision 10` 成功。迁移后 `migrate-contracts --check` 返回 `ready`、`missing=[]`、revision 11。metadata.currentHead 与本轮仓库 HEAD `1bc5ca86f9103cf66376699614b7119e580841af` 不一致（metadata 为 `c8de5aecef5656717b14165999a9fba7b8114802`）；该差异是迁移命令记入的 dispatcher 仓库 HEAD，不是项目 main HEAD。caseClass=`challenge`。关键业务事实未触碰；迁移前 web-case hash 未保存，标记 unknown，不能声称 hash 不变。

## 原始失败样本判断
Grok session `01a157d3-c8c9-76e3-83ec-35eb8dcbb741` 对应的可见最近失败证据是 `diagnostics/post-ownmethod-20261023/node-trace-receipt.json` 与 `agent-notes/20261023-post-ownmethod.md`。证据为运行时长 18s 后被切断、第二个 blob worker 已返回、challenge-fo 完成 200，但未出现证书 document POST，未有 readback；本地 receipt 记录 Reflect.apply 约 53,000,000 次，短名仅按长度分类、无异常名、无宿主行为命名。它不是 opcode trace，也不足以判断 JSVMP/宿主哪一层为根因；不能据此把“跑偏”归咎 opcode。

## 可复现性 / 缺口
该失败运行不可由当前已保存材料直接固定重放：命名页只有 receipt，目录内没有 run-specific input manifest、原始 HTML/source/响应输入、精确 runtime/runner hash 清单或 stdout/stderr 原始运行产物。现有 host-evidence scope/pair 属不同旧 Firefox/HTMLFormElement.submit 验证，不与该 Node Reflect.apply 运行同 scope，不能拼接成复现闭环。下一拍应由 dispatcher 决定允许的动作；预期需要先建立原始输入/执行器/版本哈希锁定并验证稳定复现，再以最小证据判断是执行超时/循环、动态字节码/VM 还是环境差异。不要把日志计数当 opcode 语义事实。

## 哈希
- migration 前 web-case：unknown（迁移前未采集）。
- 迁移后：见 `inventory.json`。
- 业务轴 before/after：迁移只写 caseClass/contracts、metadata revision/head/time 与 docs bootstrap；未编辑 `contracts/auto-decision-facts.json`、`contracts/workflow-artifacts.v1.json`、`contracts/request-parameter-lineage.v1.json`。
