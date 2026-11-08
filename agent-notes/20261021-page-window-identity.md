# 页面窗口身份安装后的官方 baseline

2026-10-21。`next` 对失败 baseline `0b68c2894cfb476fbc809bcc05830f0c` 给出 `repair_submit_host_behavior`，`turnGate=blocked`。本拍只改了一处已有行为，没有新开宿主面，没有改门，没有改采集器，没有写完成轴。

第 3028 列仍是运算符表里 `<` 函数的 `function` 关键字，`<` 在第 3046 列。调用帧第 3345 列是 `&` 函数的 `return`，`&` 在第 3354 列。两个函数都只比较或运算自己的参数。Location 原型守卫上一张官方 raw 没有变。那套守卫只从 `Debugger.onNewGlobalObject` 进入。挑战脚本是 `_replaceDocumentHTML` 里的 `document.write` 在页面窗口执行的。`wrapped` 在调用原来的替换之前，已经给 `this.window` 装了 cookie、对话框、时钟和 XHR，但没有调用 `installSandboxIdentity`。这一拍在 `orig.apply` 之前，对 waive 后的页面窗口调用一次已有的 `installSandboxIdentity`。

回归 `test_shipped_sandbox_identity_location_comparison_survives_security_error`：1 个测试，0.038s，通过。它锁定这次调用出现在 `installInlineXHR(this.window)` 之后、`orig.apply` 之前。

scope 重签为 `222d589a3142544c976d95cb6667c7331776112deee283f84464e5ff94082de8`。helper sha256 `27aaae184eecb16b2e04231679abc1e70923ceb024d9aa0264012b22c29314a0`。`load_scope` 通过。priorScope 是 `cef99760eca406e441a408ac29d22cbd41076befae2522bb7230fcca807dd942` 与官方 baseline `0b68c2894cfb476fbc809bcc05830f0c`。runner sha256 `31746c03fd9890d48317faec1e2aa5ff5f99c7d63e0ce27c87b0956a5fa54d8a` 未变。

官方 baseline `8187e4d91aa04facab98a740f72dbad1`：status `failed`，exitCode=1，timedOut=false，pid 18436。startedAt `1792584834917440000`，finishedAt `1792584843994964900`，相差 9077524900 ns，约 9.1s。failure 是 `execution did not complete successfully`。stdout 与 stderr 都是空文件，sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`。argvHash `beb28597684b13255be0b40ed52350551050dbfacec816a0dc1a68d513722485`。execution.json sha256 `9fb0134a135229aebeacc7fbf660351f7c2b8387dee2fda611f0b9c3c4874af0`。

raw 222 字节，sha256 `534609ca23a0472c035bc74092454398420761e448eb632583db28adac35ac2c`，与 `0b68c2894cfb476fbc809bcc05830f0c` 字节相同。事件只有 `host-diagnostic` 和 `summary`。诊断是第 2 行第 3028 列，matched false，base 是 object。没有 `host-observation`。raw 没有请求行。`summary.ok` 为 true 只是摘要字段，执行状态仍是 failed。

side sha256 `685ff13888535deb1104f0743711177d14997cc5b1732d278f6317eb4345855e`，与上一张 side 字节相同。base `object`，getEntries `function`，finished false，access、threw、receiverId 都是空。`scriptError` 只有 kind `other`、class `other`、line 2、column 3028。探针文件 sha256 是 `062ef06ed814f03b3858e294b043a8464664ecea163eb57c318ce44946db2410`。side 和 raw 没有变。

这张回执仍停在第 3028 列，没有到 `HTMLFormElement.submit` 第 75507 列。没有证书 document POST，也没有同租约回读。把已有身份安装补到页面窗口，没有移动官方列号，也没有改变 raw。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。本拍不再加另一个宿主 API。
