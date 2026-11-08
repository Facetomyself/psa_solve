# 页面区 Location 原语守卫之后的官方 baseline

2026-10-21。`next` 对 revision 7 给出 `repair_submit_host_behavior`，`turnGate=blocked`。约束是 `same-scope`、`one-host-behavior`、`submit-callsite-only`、`no-completion-facts`。第 3028 列仍是 `<` 函数的 `function` 关键字。沙箱里的 `armLocProto` 已经走过 4 级，官方 raw 没变。`Cu.evalInSandbox` 直接吃页面窗口会抛 `NS_ERROR_ILLEGAL_VALUE`，所以页面窗口上的 `installSandboxIdentity` 没有装上。挑战脚本在 `document.write` 时跑在页面区。

这一拍只加了 `installPageLocationPrimitive`。它用页面自己的 `Function` 跑同一段守卫：最多 4 级，跳过 `Object.prototype` 同名函数，只有 `SecurityError` 或消息含 `The operation is insecure` 时才返回 `document.documentURI` 文本。没有调用 `evalInSandbox`。沙箱里的 `armLocProto` 和页面窗口上的 `installSandboxIdentity` 调用都留着。回归 `test_shipped_sandbox_identity_location_comparison_survives_security_error` 通过，打印 `location-primitive-ok 18` 和 `page-location-primitive-ok 5`。helper sha256 `bb3a7687d4adeb0c511a3e80499f40fa2d8ec5289c439a8ea167439817a98024`。scope 重签为 `87371cc117dae175f403155ef09371f86ab7c77311fb76107afd9811e42eebd3`，`5247b2e5d92d77a9a7757831d8d71f913a84fcfe028235fcf27f075bd7144be4` 与 baseline `0cd81ead2afe4955b1841e5d8f043774` 留在 priorScope。`load_scope` 通过。

官方 baseline `722438ae8653483b92ae8cf163d7f956`：exitCode=1，timedOut=false，pid 57244，约 9.1s。诊断仍是第 2 行第 3028 列，matched false，base `object`。side 仍是 kind `other`、class `other`、line 2、column 3028，finished false。raw 222 字节，sha256 `534609ca23a0472c035bc74092454398420761e448eb632583db28adac35ac2c`，与 `0cd81ead` 字节相同。side sha256 `685ff13888535deb1104f0743711177d14997cc5b1732d278f6317eb4345855e`，也与上一张相同。探针 sha256 `1764b6278b5f63149bea102e9bb7a525b9f02a49806bd071c582e073f64d4375`。没有 `host-observation`，没有请求行，没有到第 75507 列。没有证书 document POST，也没有同租约回读。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。页面区安装没有移动官方列号，也没有改变 raw。
