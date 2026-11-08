# 沙箱 Date 构造器已经装上

日期：2026-10-21

动作：`repair_submit_host_behavior`。只改沙箱 `Date` 的安装方式。

## 上一回

`12894c3b70894772bf5c0fb65a2a252a` 让沙箱调用 `challengeDate`，但仍走 `Cu.evalInSandbox`。侧记 `clockResource` 是 `sandbox-throw`。不能证明构造器已经换上。raw 没有证书 document POST。

## 这一处

内容全局上传入 `evalInSandbox` 会抛错，构造器留不下来。这一回用该全局自己的 `Function` 和页面同一段 `challengeDateInstallBody`。构造器写上之后，标记才是 `installed`，并写下 `__clockInstall`。锚点读取失败不再把标记改回 throw。

测试 `test_shipped_sandbox_date_constructor_uses_challenge_clock` 执行了这具函数。通过，0.033s。探针打印 `sandbox-date-ok 14`。失败的 `Function` 把标记留在 `sandbox-throw`，成功的安装是 `sandbox-installed`。

## 重签

- helper sha256 `728f1ddd8c08f5dba7855ae541afc423a63906049c2d2792a6b9670275a37db6`
- scope `56c5660873f731dbf78ad98c5eaef911053404deae8b3734059736df61cb556d`
- priorScope `342ef8a0935dc7c039889db68542c3165015e66b30a3f6c752a52da098ac13e5`，baseline `12894c3b70894772bf5c0fb65a2a252a`
- runner `31746c03fd9890d4` 与 geckoLib `9f21705d909f5e5c` 未变
- `load_scope` 通过后才跑官方 baseline

## 官方 baseline

`2cce87b688f34c08bb42f7021e966e81`：exitCode=1，timedOut=false，约 22.72s。失败原因是执行未成功完成。

raw 只有 `host-diagnostic` 和 `summary`，225 字节，与 `12894c3b70894772bf5c0fb65a2a252a` 字节相同。诊断是第 1 行第 1337365 列，matched false，base `object`。侧记 kind=`other`，class=`slow-script`，sourceClass=`other`，sourceForm=`token`。

`clockCtor`=`installed`，`clockInstall`=`installed`，`clockResource`=`sandbox-installed`。`entries` 1，`observe` 1。

没有证书 document POST 行。没有同租约回读行。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。
