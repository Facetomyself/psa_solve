# 合同迁移：补上 metadata.currentHead

2026-10-21。`next` 对当前失败状态给出 `migrate_contracts`，`turnGate=blocked`。原因是 legacy case 的 `metadata.currentHead` 与仓库 HEAD 不一致。约束是 `legacy-contract`、`migration-required`、`no-default-recon`、`record-migration-before-next`、`goal-incomplete-does-not-override`。本拍没有改 helper，没有重签 scope，没有跑官方 baseline，没有写完成轴。

迁移前 `contracts/case-metadata.v1.json` 的 `currentHead` 是 `915f61211163cc18e65612b04b9408cb47f14cae`，`contractRevision` 是 5。`git rev-parse HEAD` 是 `5b2ed693264312232ac41225b420215898bf089f`。

执行 `web_case.py migrate-contracts --apply --case-class challenge`。caseClass 保持 `challenge`，status 保持 `patching`。阶段状态没有改。`contractRefs` 仍指向原有 workflow 与 lineage，risk 两项仍是 null。这两个合同文件的 sha256 前缀仍是 `56c519650281dafc` 与 `0e09fa5d2313ecc0`，字节长度仍是 58509 与 13475。

迁移后 `currentHead` 是 `5b2ed693264312232ac41225b420215898bf089f`，`contractRevision` 是 6。index 仍是 80 行，`doc_health` 为 `[]`。

官方 baseline 仍是 `0cd81ead2afe4955b1841e5d8f043774`，停在第 2 行第 3028 列。没有证书 document POST，也没有同租约回读。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。
