# 合同迁移：currentHead 跟到 2d0f5d43

2026-10-21。新回合的 `next` 再次给出 `migrate_contracts`，`turnGate=blocked`。原因仍是 `metadata.currentHead` 与仓库 HEAD 不一致。约束是 `legacy-contract`、`migration-required`、`no-default-recon`、`record-migration-before-next`、`goal-incomplete-does-not-override`。本拍没有改 helper，没有重签 scope，没有跑官方 baseline，没有写完成轴。

上一拍记下的 `currentHead` 是 `5b2ed693264312232ac41225b420215898bf089f`，`contractRevision` 是 6。本拍 `git rev-parse HEAD` 是 `2d0f5d43cb74e5a40146de9d39955299833760ea`，提交说明是接入 ruyihttp 作为可选 Firefox Necko/NSS 传输。`5b2ed693` 是该提交的祖先。分支 `chore/workspace-governance-index` 没有 upstream，没有 fetch。

执行 `web_case.py migrate-contracts --apply --case-class challenge`。caseClass 保持 `challenge`，status 保持 `patching`。阶段仍是 recon pass、browser-control skipped、browser-evidence pass、local-evidence pending、environment-patch pending、deobfuscation pending、protocol-recovery triage-only、parity pending。`contractRefs` 未改。workflow 与 lineage 的 sha256 前缀仍是 `56c519650281dafc` 与 `0e09fa5d2313ecc0`，字节长度仍是 58509 与 13475。

迁移后 `currentHead` 是 `2d0f5d43cb74e5a40146de9d39955299833760ea`，`contractRevision` 是 7。index 仍是 80 行。

官方 baseline 仍是 `0cd81ead2afe4955b1841e5d8f043774`，停在第 2 行第 3028 列。没有证书 document POST，也没有同租约回读。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。
