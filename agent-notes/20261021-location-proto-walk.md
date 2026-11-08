# Location 原型链上一步之后的官方 baseline

2026-10-21。`next` 对失败 baseline `8187e4d91aa04facab98a740f72dbad1` 给出 `repair_submit_host_behavior`，`turnGate=blocked`。本拍只改了 `armLocProto` 的查找深度，没有新开宿主面，没有改门，没有改采集器，没有写完成轴。

第 3028 列仍是运算符表里 `<` 函数的 `function` 关键字。`<` 在第 3046 列。调用帧是 `&`。同一窗口上的直接比较，`location`、`top`、`parent`、`window`、`frames`、`document`、`navigator`、`screen`、`history`、`performance` 都没有抛出。`Cu.evalInSandbox` 直接吃页面窗口时抛 `NS_ERROR_ILLEGAL_VALUE`，所以上一拍对页面窗口调用 `installSandboxIdentity` 没有装上。`Location` 的立即原型上没有 `toString`。再往上一级才是数据函数，而且不是 `Object.prototype.toString`。`Window` 的 `toString` 在更上三级，同样不是 `Object.prototype.toString`。旧的 `armLocProto` 只看立即原型，所以那一层方法从来没包上。

这一拍让 `armLocProto` 最多再走 4 级原型，跳过 `Object.prototype` 上的同名函数，只包找到的数据函数。健康对象自己的文本保持。回归 `test_shipped_sandbox_identity_location_comparison_survives_security_error`：1 个测试，0.037s，通过，输出 `location-primitive-ok 18`。

scope 重签为 `5247b2e5d92d77a9a7757831d8d71f913a84fcfe028235fcf27f075bd7144be4`。helper sha256 `325b6a0aa171c7e62c938712a700ee3f9470a4abc958920e240a1006a5f6611f`。`load_scope` 通过。priorScope 是 `222d589a3142544c976d95cb6667c7331776112deee283f84464e5ff94082de8` 与官方 baseline `8187e4d91aa04facab98a740f72dbad1`。runner sha256 `31746c03fd9890d48317faec1e2aa5ff5f99c7d63e0ce27c87b0956a5fa54d8a` 未变。

官方 baseline `0cd81ead2afe4955b1841e5d8f043774`：status `failed`，exitCode=1，timedOut=false，pid 39452。startedAt `1792585792045907300`，finishedAt `1792585801120627200`，相差 9074719900 ns，约 9.1s。failure 是 `execution did not complete successfully`。stdout 与 stderr 都是空文件，sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`。argvHash `8bbfa66aac4f76a7190d2081fa3c9ee7291ebf0a7f50f80a83520d3601820c60`。execution.json sha256 `3bf7da9e3e24869dedb14971012e41421c433a41e80f6e60333a215c1d4ccf33`。

raw 222 字节，sha256 `534609ca23a0472c035bc74092454398420761e448eb632583db28adac35ac2c`，与 `8187e4d91aa04facab98a740f72dbad1` 字节相同。事件只有 `host-diagnostic` 和 `summary`。诊断是第 2 行第 3028 列，matched false，base 是 object。没有 `host-observation`。raw 没有请求行。`summary.ok` 为 true 只是摘要字段，执行状态仍是 failed。

side sha256 `685ff13888535deb1104f0743711177d14997cc5b1732d278f6317eb4345855e`，与上一张 side 字节相同。base `object`，getEntries `function`，finished false，access、threw、receiverId 都是空。`scriptError` 只有 kind `other`、class `other`、line 2、column 3028。探针文件 sha256 是 `cfea2060edbe6b71a661545431e9c01eb3bec0f921599a1c9cda786eafbcf036`。side 和 raw 没有变。

这张回执仍停在第 3028 列，没有到 `HTMLFormElement.submit` 第 75507 列。没有证书 document POST，也没有同租约回读。把原型查找再走一级，没有移动官方列号，也没有改变 raw。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。本拍不再加另一个宿主 API。
