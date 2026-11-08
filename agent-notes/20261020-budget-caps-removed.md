# 项目内次数与时限已取消

2026-10-20。只动 `psa_solve` 合同，没有重跑 Node，没有改 `experimentHygiene`，没有写 `hostProbe` / `serverAccepted` / `boundary-moved`。

已去掉：

- `diagnostics/shadowroot-repair-20261020/receipt_adapter.py` 的各一次、15 秒、`executeBefore`、独占槽和“过期不退还”。再跑会先把旧 claim、日志和 receipt 抄到同名 `.historical`。
- `fixed-profile.json` 的 `budget` / `timeoutSeconds`，以及会在每次 `next` 后把复跑判死的 `dispatcher-turn.json` 哈希钉。输入、runtime 和其余保护文件的哈希还在。
- `authorization.json`、`subtree-locate` 授权、`receiver-provenance` 输入回执里的次数、秒数和 `dispatcherRemains`。

旧运行记录原样保留，包括四份 `evidence/web/diagnostic-*/receipt.json` 里的 `budget: 1`。那是当时的计数字段。共享诊断脚本仍会因为回执文件已存在而拒绝再领同一份 reviewed profile；那是去重，不是本项目的次数合同。

v8trace 采集器的字节上限没有动。
