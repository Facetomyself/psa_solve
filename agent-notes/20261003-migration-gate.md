# 合同迁移与当前 web_case 卡门（2026-10-03）

## 判定

本切片只读检查，没有执行 `migrate-contracts --apply`。检查开始时 case 确实需要迁移：`migrate-contracts --check` 返回 `status=migration-required`、`missing=[metadata.currentHead]`、`revision=1`。当前文件已被同一工作会话的其他动作更新为迁移后状态：`case-metadata.currentHead=b48aca9db76226a89dcd0a274c56a9c7a08b9952`、`contractRevision=2`，因此现在再次 `--check` 返回 `status=ready`。这次外部 apply 的实际副作用已经发生，不能把它归因到本切片。

## 依据与目标分类

- `web-case.json` 当前 `caseClass=challenge`、`status=patching`，目标是 Cloudflare managed challenge 的 RuyiDOM 求解、证书 POST 和同 lease 业务 readback；按 `full-workflow-contracts.md`，`challenge` 是正确目标类，不能降成 `recon`。
- `contracts/auto-decision-facts.json`：`revision=4`、`ruyidom=diverged`、`localReproduced=false`、`serverAccepted=false`、`requestBoundaryAligned=false`、`firstDivergence=environment-gap`、`experimentHygiene=stop-search`。
- `contracts/case-metadata.v1.json` 迁移前是 `currentHead=7952b2e68d7396c2793611c119c84687de5044e5`、`contractRevision=1`；当前为 dispatcher root HEAD `b48aca9db76226a89dcd0a274c56a9c7a08b9952`、revision 2。
- `psa_solve` 子仓自己的 HEAD 是 `1bc5ca86f9103cf66376699614b7119e580841af`（branch `main`，upstream `f90a6945b55b083e991233b050a68edddf3a8acb`）。脚本 `web_case.py` 的 `_repository_head()` 明确在 `D:\reverse_ENV` 根仓执行 `git rev-parse HEAD`，所以迁移校验/写入的 `currentHead` 应是 `b48aca9d...`，不是子仓 `1bc5ca86...`。

## 真实检查命令与结果

```powershell
& "D:\reverse_ENV\.venv\Scripts\python.exe" `
  "D:\reverse_ENV\skill\web-reverse\scripts\web_case.py" migrate-contracts `
  --project "D:\reverse_ENV\workspace\psa_solve" --check
```

迁移前输出：`migration-required`，`missing=["metadata.currentHead"]`，`revision=1`；工具给出的显式命令模板为：

```powershell
& "D:\reverse_ENV\.venv\Scripts\python.exe" `
  "D:\reverse_ENV\skill\web-reverse\scripts\web_case.py" migrate-contracts `
  --project "D:\reverse_ENV\workspace\psa_solve" --apply `
  --case-class challenge --expected-revision 1
```

迁移后复核命令仍是上面的 `--check`，当前输出：`status=ready`、`missing=[]`、`revision=2`。

## `--apply` 的代码级副作用

`web_case.py` 的 `migrate_contracts_command` 会：

1. 将 `web-case.json.caseClass` 设为显式 `--case-class`，并重写 `contractRefs`；这里应保持 `challenge`。
2. 调用 `bootstrap_case_contracts`；现有 `contracts/workflow-artifacts.v1.json` 与 `contracts/request-parameter-lineage.v1.json` 已存在，所以不会覆盖它们；只有缺失模板才会新建。
3. 原子写入 `web-case.json`，更新 `updatedAt`。
4. 原子写入 `contracts/case-metadata.v1.json`，`contractRevision` 从 1 增到 2，`currentHead` 写 dispatcher root HEAD。
5. 调用 `bootstrap_project_docs`/`render_project_docs`。迁移前对现有 `docs/web/*` 做的无写入预比较显示 generated sections 均不变；当前 `index.md`、`environment-patch.md` 内容 hash 仍分别为 `7f47c63f16081f19684ae95718d05b6045c551b9064936a87af296cff99a6a1e`、`b60ff16cb0cb3e685f5a4ab03be3e65486d557be16257f6d807c0972e81fa09e`。

它不会自动改 `contracts/auto-decision-facts.json`，不会清掉 `stop-search`，也不会把业务阶段改成完成。

## 迁移后的当前卡门

当前真实命令：

```powershell
& "D:\reverse_ENV\.venv\Scripts\python.exe" `
  "D:\reverse_ENV\skill\web-reverse\scripts\web_case.py" next `
  --project "D:\reverse_ENV\workspace\psa_solve" --preview
```

输出 action 是 `refuse_host_enumeration`，`turnGate=blocked`，`landing=env-patch`；`docs.read` 只有 `docs/web/environment-patch.md`。约束明确要求停止相邻宿主字段搜索、保持真实双条件补丁、不要因目标未完成而继续开新宿主面。迁移只解除 legacy metadata 门，**没有**授权 `environment_patch`、新的 host getter、`serverAccepted` 或业务 readback。

`web_case.py validate --project ...` 仍有两个独立问题：旧 artifact `receipt-399daaf7dc35` 的指针 SHA-256 不匹配（期望 `399daaf7...`、实际 `6c038605...`），以及 `environment-patch` stage 为 `running` 而 `environmentPatchGate.status=not-ready`（校验错误要求 `ready`）。这两项不是迁移门，不能借 `--apply` 掩盖。

## 证据路径

- `D:\reverse_ENV\workspace\psa_solve\web-case.json`
- `D:\reverse_ENV\workspace\psa_solve\contracts\case-metadata.v1.json`
- `D:\reverse_ENV\workspace\psa_solve\contracts\auto-decision-facts.json`
- `D:\reverse_ENV\workspace\psa_solve\contracts\workflow-artifacts.v1.json`
- `D:\reverse_ENV\workspace\psa_solve\docs\web\environment-patch.md`
- 执行规则：`D:\reverse_ENV\skill\web-reverse\references\case-contract.md`、`full-workflow-contracts.md`；实现：`D:\reverse_ENV\skill\web-reverse\scripts\web_case.py`
