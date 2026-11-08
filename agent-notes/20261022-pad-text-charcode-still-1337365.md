# 2026-10-22 padText charCodeAt reject deleted

只删掉 `padText` 里两句 charCodeAt 核对，`toString` 得到字符串后直接 `return via`。调用点没改，document 早退没有装回。worker 的无 document 分支没有调用它。

- helper `c0a334eeb869138388362eeb2a2f0bb1d290e0aeb46fc932a9f718d6ab51c4e0`
- scope `c454797a825165ecb4660363b0f7593bed5d21d70760cbdf2845320c6041e8e9`
- prior `706155d2eb5880c423132aff6ef45bc92808ad9027fad0dbc0005904e1886a64` / `a92ebd317fe8423bb55c52c3323a9b44`
- baseline `9a2d0ab3f80147ab83ff13ab2d0bc58b`，pid 45308，exitCode 1，timedOut false，22720998600 ns
- 诊断仍是第 1 行第 1337365 列，class `slow-script`，sourceForm `token`
- raw `32a2ac26aae79d8d94a2c6b810846bad9e1dc16f36d8d5210a84f7a0b45bda84` 225 字节
- side `b89ae10c0461d09f909ada6cf9308bcefd890e9554839670a4f63a3cd71363bc` 642 字节
- 与上一发 raw/side 相同
- 盖章 `verify_host_execution` / `blocked` / `2026-10-22T04:14:28Z`
- 含 `no-new-host-surface`。不得再发未点名的宿主修复
- 完成轴保持 false，没有证书 document POST，没有同租约回读
