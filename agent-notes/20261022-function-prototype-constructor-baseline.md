# 原型构造器赋值后的官方 baseline（2026-10-22）

14:32 审计读到 helper `c5243aebccc7b87d7b65e5d264cf8159c87b7126ef054621113cf79bda5c75b0`、scope `b183fa222b5a4468a744f32e1815622d5d41de7f4bdd3d569ccb0a906460badb`、baseline `5c3f17cbcf0d4eefa23ba7ebef89787f`。那时 `RealFunction.prototype.constructor=fn` 还没有写上。

随后只在 `installLeadingPadFunction` 的 `new host.Function` 函数体里、紧挨 `fn.prototype=RealFunction.prototype` 写上这一句，然后重签并跑官方 baseline。没有改裁剪谓词、`leadingPadSource`、eval 包装或调用点，没有在 worker 的无 document 分支调用它，也没有动 `Number.prototype.length=0`。

- helper sha256 `1709630ef99e24348c14ef41a7557695e9903609dbb5f5a8b3e00b4c9cef64c3`
- scope `c03b9b60785cc282667c7489e2b9d7dd37e4ae1d749dfc9f6c850dbd1a57e922`
- baseline `5d58653574064594bab0dc6dc73a493b`，execution sha256 `8bd85ca162f7af7cb9068cf0d6648faee3405477f926fc4bf0527e9101923584`
- pid 53416，exitCode 1，timedOut false，耗时 22912793400 ns
- 第 1 行第 1337365 列，kind `other`，class `slow-script`，sourceForm `token`，sourceClass `other`
- raw `32a2ac26aae79d8d94a2c6b810846bad9e1dc16f36d8d5210a84f7a0b45bda84`（225），side `b89ae10c0461d09f909ada6cf9308bcefd890e9554839670a4f63a3cd71363bc`（642），与上一发相同
- side 顶层没有 `worker`，也没有编译入口、输入或 realm 字段
- 盖章 `verify_host_execution` / `blocked`，updatedAt `2026-10-22T06:36:25Z`，约束含 `no-new-host-surface`

这句赋值没有把正式停点移开，也不能当成目标脚本已经走过该构造器。`Number.prototype.length=0` 仍是审计标出的未隔离项，本拍没有改它。没有证书 document POST，也没有同租约回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。
