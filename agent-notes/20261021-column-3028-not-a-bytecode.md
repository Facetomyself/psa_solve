# 第 3028 列不是字节码，也不是宿主 API

状态：只做了静态记号和这套 Gecko 的编译列对照。没有改 helper，没有重签 scope，没有跑官方 baseline，没有写完成轴。

绑定源第 2 行第 3021 到 3049 列仍是长度 29 的匿名函数，两个长度 2 的参数，函数体是 `return` 后的 `<`。`<` 在第 3046 列。第 3028 列只是关键字 `function` 的最后一个字符。同一张对象表里还有 13 个别的运算函数。调用帧那一列第 3329 到 3357 列是 `&` 函数，`&` 在第 3354 列。两处都没有宿主 API 字面量。

这套运行时把该 `<` 函数编成独立脚本：起始列是第 3029 列（参数列表的 `(`），唯一字节码列是第 3037 列（`return`）。`&` 函数的唯一字节码列是第 3345 列，与非正式栈的调用帧一致。全文件编译后，没有任何偏移的列号是 3028。因此第 3028 列不是 `<` 的执行点，也不是某一次宿主调用的调用点。

`describeScriptError` 仍把 `receiverId` 写成字面量 `"null"`，不读 JS 接收者。官方 `stackShape` `other` 只说明字符串栈没有 `@行:列`。`Window.prototype` 的 `toString` / `valueOf` 已在 `69cede48` 试过，列和 raw 都没动。操作数的内部类没有新的正式证据。Location、contentWindow、window 身份、`Object.prototype` 不再加。

没有证书 document POST，也没有同租约回读。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。

阻塞：缺的是比较操作数的内部类，不是另一处原型包装。
下一步：没有这个类之前不改宿主。
