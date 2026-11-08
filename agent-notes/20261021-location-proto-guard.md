# Location 原型原语守卫后的官方 baseline

2026-10-21。`next` 对失败 baseline `9d37d27a432f4e1fa6ea973ca8b31fe0` 给出 `repair_submit_host_behavior`，`turnGate=blocked`。约束含 `same-scope`、`one-host-behavior`、`no-completion-facts`。本拍只改了已有的 `installSandboxIdentity`，没有新开宿主面，没有改门，没有改采集器，没有写完成轴。

上一张官方 raw 与安装时才替换 `location` 的那一刀字节相同。绑定源第 2 行第 3021 列起是运算符表：第 3046 列是 `<`，调用帧第 3354 列是 `&`。两边都是两个长度 2 的参数和 `return`，没有宿主 API 字面量。这一回在拿到 `location` 之后，无论 `String(location)` 是否抛错，都给它的原型上已有的 `toString` 和 `valueOf` 包一层：原函数照常调用，只有 `SecurityError` 或消息含 `The operation is insecure` 时才返回 `document.documentURI` 的文本。安装时自己就抛错的对象仍写上自己的文本函数。读取 `location` 本身抛错时，仍用原来的替身。

回归 `test_shipped_sandbox_identity_location_comparison_survives_security_error`：1 个测试，0.039s，通过。覆盖原型抛错、读取抛错、健康文本保持，以及安装时自身可读、同原型另一个对象稍后抛错。

scope 重签为 `cef99760eca406e441a408ac29d22cbd41076befae2522bb7230fcca807dd942`。helper sha256 `75ce72bd9ee21bef0c28c83fd988ef8d811d6414ec732b1c7992535613a126b8`。`load_scope` 通过。priorScope 是 `2e241bf099f9f5c79338714383d0c8e73f9cc4a661cea4679358825946c2bdba` 与官方 baseline `9d37d27a432f4e1fa6ea973ca8b31fe0`。runner sha256 `31746c03fd9890d48317faec1e2aa5ff5f99c7d63e0ce27c87b0956a5fa54d8a` 未变。

官方 baseline `0b68c2894cfb476fbc809bcc05830f0c`：status `failed`，exitCode=1，timedOut=false，pid 54112。startedAt `1792584313749698900`，finishedAt `1792584322826339900`，相差 9076641000 ns，约 9.1s。failure 是 `execution did not complete successfully`。stdout 与 stderr 都是空文件，sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`。argvHash `a669d8d4d0ce746a6684251e9be9505f87c996e2eded9d3ee14ffecd8ca973b1`。execution.json sha256 `f4a28126f54d4577f09680c7372d183154e26d5be4db7a106dd3dc0207ee995c`。

raw 222 字节，sha256 `534609ca23a0472c035bc74092454398420761e448eb632583db28adac35ac2c`，与 `9d37d27a432f4e1fa6ea973ca8b31fe0` 和 `dd3f7a2723a4487ea116c04c650425d9` 字节相同。事件只有 `host-diagnostic` 和 `summary`。诊断是第 2 行第 3028 列，matched false，base 是 object。没有 `host-observation`。raw 没有请求行。`summary.ok` 为 true 只是摘要字段，执行状态仍是 failed。

side sha256 `685ff13888535deb1104f0743711177d14997cc5b1732d278f6317eb4345855e`，与上一张 side 字节相同。base `object`，getEntries `function`，finished false，receiverId 空。`scriptError` 只有 kind `other`、class `other`、line 2、column 3028。探针文件 sha256 是 `693f9f35879b3f6b9a9b4db3938d54c3cc19169fef7712739c5c3e4f7b81ae92`。side 和 raw 没有变。

这张回执仍停在第 3028 列，没有到 `HTMLFormElement.submit` 第 75507 列。没有证书 document POST，也没有同租约回读。给 Location 原型接住 `SecurityError` 没有移动官方列号，也没有改变 raw。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。本拍不再加另一个宿主 API。
