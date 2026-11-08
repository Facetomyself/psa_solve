# Window.prototype 原语比较

状态：同一 scope 只加了 `installWindowPrimitive`。官方 baseline 已跑完。完成轴未写。

页面自己的 `Function` 只处理 `Window.prototype` 上自有的 `toString` 和 `valueOf`。原函数照常返回。只有 `SecurityError` 或消息含 `The operation is insecure` 时，`valueOf` 返回 0，`toString` 返回空串。与 `Object.prototype` 同名的函数跳过。不改 Location，不改 `contentWindow`，不把 `window` / `self` / `globalThis` / `top` / `parent` 收成同一个对象，不调用 `evalInSandbox`。调用放在 `installFrameWindowPrimitive` 之后、`orig.apply` 之前。

回归 `test_shipped_window_primitive_comparison_survives_security_error` 通过，打印 `window-primitive-ok 7`。`test_shipped_frame_content_window_comparison_survives_security_error` 仍通过。

helper sha256 `41e7a8fecb6766f3c690daa8ffb1bbbaace79d55ce0e2b28611f1cdfc8c8bac7`。scope 重签为 `665de0cea14449717c1a676d6686d9c71c9e675f88c6a61a33dcd09c267f5e9f`，`727d4f60c83383b719183246ed8164a09273814562e60a92f8921a161efed04a` 与 baseline `02b1aecb92dd48d3b6edf237d0908795` 留在 priorScope。`load_scope` 通过。

官方 baseline `69cede48e67541ce9b3590ffc0d72316`：exitCode=1，timedOut=false，pid 27020，约 9.1s。failure 是 `execution did not complete successfully`。诊断仍是第 2 行第 3028 列，matched false，base `object`。side 仍是 kind `other`、class `other`、sourceForm `injected`、sourceClass `about-blank-injected`、errorName `SecurityError`、insecure true、parentLine 1447、sourceLineLength 0、keywordAtColumn false、stackShape `other`、flags 0、categoryClass `content-javascript`、receiverId `null`。side sha256 `450f5442a04a346eedc3f8d4a59839dbde85df251cfd737b0e4ce1074f553304`，与 `02b1aecb` 相同。raw 222 字节，sha256 `534609ca23a0472c035bc74092454398420761e448eb632583db28adac35ac2c`，与 `02b1aecb` 字节相同。事件只有 `host-diagnostic` 和 `summary`。没有 `host-observation`，没有请求行，没有到第 75507 列。没有证书 document POST，也没有同租约回读。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。

阻塞：这一处没有让正式列离开第 3028 列。
下一步：本拍不再加第二处宿主行为。
