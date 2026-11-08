# 2026-10-22 page-window pad still at column 1337365

`next` 给出 `repair_page_window_leading_pad` / `blocked`，updatedAt `2026-10-22T03:16:46Z`。这一处只在页面文档替换里调用已有的 `installLeadingPadEval(this.window)`。

helper sha256 `3f0dedced31731a2eaf4ad08f7972ff8543f43100f37503739aae447e4fd4f36`。scope `9159f68f4bd3db301e94bad66c1e2df5867b67df016b21d1ab08cec45513bde8`。上一张 scope `2818e6b8337a5f2d719aef5bb5bc8c2ee81b85c29bc06957a3c116c3938a4674` 与 baseline `3200477894eb4954ac3bbbc51c901124` 留在 priorScope。

官方 baseline `7181f8b4450844c697694929435e2e16`：pid 43544，exitCode 1，timedOut false，耗时 22720866300 ns。诊断仍是源文件外第 1 行第 1337365 列，kind `other`，class `slow-script`，sourceForm `token`。raw 与 side 与上一发字节相同。没有到第 75507 列。

页面窗调用已经在 helper 里，同一列又出现，算出的门是 `verify_host_execution`，含 `no-new-host-surface`。随后一次 `next` 把磁盘盖章写成 `verify_host_execution` / `blocked`，updatedAt `2026-10-22T03:23:01Z`。没有新的宿主面，没有重签，没有新的官方执行。没有证书 document POST，也没有同租约回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 仍是 null。再下一拍 `next` 把章改成 `repair_sandbox_leading_pad`，点名 `installLeadingPadEval(sb)`，helper 未改，完成轴仍是 false。见 `agent-notes/20261022-sandbox-pad-named.md`。
