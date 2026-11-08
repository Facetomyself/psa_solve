# 2026-10-22 sandbox pad document guard deleted

只删掉 `installLeadingPadEval` 里的 `if (!hasDoc) return;`。worker 的无 document 分支没有调用它。

- helper `5d577ded69e368de4e8c0a8b4f075f98768d560bc3e21781ff1f43268dd78109`
- scope `706155d2eb5880c423132aff6ef45bc92808ad9027fad0dbc0005904e1886a64`
- prior `d7f1c55bcb63506712ab1c731fa80d2fa73215a550dc7d3c79383d7250b9844d` / `d393f293d2d2469f888a20a5e468b138`
- baseline `a92ebd317fe8423bb55c52c3323a9b44`，pid 41780，exitCode 1，timedOut false，24530624400 ns
- 诊断仍是第 1 行第 1337365 列，class `slow-script`，sourceForm `token`
- raw `32a2ac26aae79d8d94a2c6b810846bad9e1dc16f36d8d5210a84f7a0b45bda84` 225 字节
- side `b89ae10c0461d09f909ada6cf9308bcefd890e9554839670a4f63a3cd71363bc` 642 字节
- 与上一发 raw/side 相同
- 盖章 `verify_host_execution` / `blocked` / `2026-10-22T04:00:54Z`
- 完成轴保持 false，没有证书 document POST，没有同租约回读
