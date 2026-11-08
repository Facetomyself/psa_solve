# 2026-10-22 sandbox pad document guard

`next` 把磁盘盖章写成 `repair_sandbox_pad_document_guard` / `blocked`，updatedAt `2026-10-22T03:47:45Z`，会话 `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`。

baseline 仍是 `d393f293d2d2469f888a20a5e468b138`，停在源文件外第 1 行第 1337365 列。页面窗已经调用 `installLeadingPadEval(this.window)`，沙箱包装已经调用 `installLeadingPadEval(sb)`。`installLeadingPadEval` 在 `host.document` 为空时执行 `if (!hasDoc) return;`，所以这次沙箱调用没有包上 eval。

下一处只允许删掉这一句。不得在 worker 的无 document 分支调用它，不得改别的宿主面。

本拍没有改 helper，sha256 仍是 `a5e1cd4c915909eb9223ea7d1d62ff29248a994b5f6a3fbad2562e37eacd520c`。scope 仍是 `d7f1c55bcb63506712ab1c731fa80d2fa73215a550dc7d3c79383d7250b9844d`。没有重签，没有新的官方执行。没有证书 document POST，也没有同租约回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 仍是 null。
