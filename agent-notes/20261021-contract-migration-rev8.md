# 合同迁移：currentHead 跟到 d06b711

2026-10-21。新回合的 `next` 给出 `migrate_contracts`，`turnGate=blocked`。原因仍是 `metadata.currentHead` 与仓库 HEAD 不一致，表面文案是缺少 `metadata.currentHead`。约束是 `legacy-contract`、`migration-required`、`no-default-recon`、`record-migration-before-next`、`goal-incomplete-does-not-override`。本拍没有改 helper，没有重签 scope，没有跑官方 baseline，没有写完成轴。

上一拍记下的 `currentHead` 是 `2d0f5d43cb74e5a40146de9d39955299833760ea`，`contractRevision` 是 7。本拍 `git rev-parse HEAD` 是 `d06b71100fe37c437ee6da96c21b059718ffe285`。该提交把 RuyiDOM 和 Patched Node 从会话 MCP 收成一次调用 CLI，并写上 ruyihttp 的主线位置。`2d0f5d43` 是它的祖先。分支 `chore/workspace-governance-index` 没有 upstream，没有 fetch。

执行 `web_case.py migrate-contracts --apply --case-class challenge --expected-revision 7`。caseClass 保持 `challenge`，status 保持 `patching`。阶段仍是 recon pass、browser-control skipped、browser-evidence pass、local-evidence pending、environment-patch pending、deobfuscation pending、protocol-recovery triage-only、parity pending。workflow 与 lineage 的 sha256 前缀仍是 `56c519650281dafc` 与 `0e09fa5d2313ecc0`，字节长度仍是 58509 与 13475，行数仍是 1517 与 353。

迁移后 `currentHead` 是 `d06b71100fe37c437ee6da96c21b059718ffe285`，`contractRevision` 是 8，metadata 与 web-case 的 `updatedAt` 都是 `2026-10-21T13:03:34Z`。

盖章前的同源探针不是官方回执。文档写完后，Location 原型上的 toString 与 valueOf 仍可配置、可写，并带有守卫标记。同源的 location、window、top 比较都不抛。因此 `722438ae8653483b92ae8cf163d7f956` 停在第 2 行第 3028 列，不是漏装 Location 原型守卫。官方 raw 仍与 `0cd81ead` 相同。没有证书 document POST，也没有同租约回读。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。
