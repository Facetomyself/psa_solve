# 2026-10-22 sandbox leading pad named

`next` 把磁盘盖章写成 `repair_sandbox_leading_pad` / `blocked`，updatedAt `2026-10-22T03:32:05Z`，会话 `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`。

baseline 仍是 `7181f8b4450844c697694929435e2e16`，停在源文件外第 1 行第 1337365 列。页面窗已经调用 `installLeadingPadEval(this.window)`。helper 里还没有 `installLeadingPadEval(sb)`。下一处只允许在现有 `_sb` 包装里、紧挨 `installChallengeClock(sb)` 调用它。

本拍没有改 helper，sha256 仍是 `3f0dedced31731a2eaf4ad08f7972ff8543f43100f37503739aae447e4fd4f36`。没有重签，没有新的官方执行。没有证书 document POST，也没有同租约回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 仍是 null。
