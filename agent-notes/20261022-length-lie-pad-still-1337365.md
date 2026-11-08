# 2026-10-22 长度为 0 的裁剪仍停在第 1337365 列

`next` 盖章 `repair_submit_host_behavior` / `blocked` / `2026-10-22T02:41:44Z`，会话 `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`。原因是源文件外第 1 行第 1337365 列，调用点仍是第 1 行第 75507 列。约束含 `one-host-behavior`。本拍没有再 `next`。

上一发把沙箱里的 `Number.prototype.length` 写成 0 之后，停点从第 55371 列回到这段源文件外的慢脚本，raw 与 side 与裁剪之前的那次回执相同。已有的首尾裁剪用 `code.length < 100000` 决定是否动手。长度为 0 的跨区对象会被当成短脚本，原样交回。这一处只改 `leadingPadSource`：这类对象先用 `toString` 和 `charCodeAt` 收回原始文本，再按原来的首尾空白和末尾短斜杠规则裁剪。内部空格不动。没有恢复整段剥空白，没有第二处 length 写入，没有装回空函数，没有安装 `xPLd9`，没有改 13 秒时限。

Node 回归把长度为 0 的代理交给已装上的包装。旧函数交回的脚本长度是 100032，首字符是空格。新函数交回的长度小于 1000，首字符是引号，表达式结果仍是 4。短脚本、内部空格和整段剥空白的反例仍在。

helper sha256 `e0786d64fabf6793dba9a1b3d223ea379c541ecec114d5125e69d8d7d95335da`。scope 重签为 `2818e6b8337a5f2d719aef5bb5bc8c2ee81b85c29bc06957a3c116c3938a4674`。`692ddc40cbf0345d56fa0ddc5e146e664d0e700411b9913e1e20585e88df7866` 与 baseline `53d3ee5ee6e74d7bacd6d18a920ce07b` 留在 priorScope。

官方 baseline `3200477894eb4954ac3bbbc51c901124`：pid 7244，exitCode 1，timedOut false，耗时 22722347900 ns。诊断仍是第 1 行第 1337365 列，kind `other`，class `slow-script`，sourceForm `token`，sourceClass `other`。没有 errorName，没有接收者字段。raw sha256 `32a2ac26aae79d8d94a2c6b810846bad9e1dc16f36d8d5210a84f7a0b45bda84`，225 字节。side sha256 `b89ae10c0461d09f909ada6cf9308bcefd890e9554839670a4f63a3cd71363bc`，642 字节。与上一发字节相同。`summary.ok` 不是 `serverAccepted`。

这次官方 eval 没有以长度为 0 的对象进入包装，或者裁剪没有改变看门狗落点。没有到第 75507 列。没有证书 document POST，没有同租约回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 仍是 null。
