# 02b1aecb 的正式身份仍不能点名宿主调用

2026-10-21。`next` 给出 `verify_host_execution`，`turnGate=blocked`。约束含 `no-new-host-surface`。盖章理由是「baseline 工具未成功完成或文件/scope 已变」。

`load_scope` 通过。state 与 scope 都是 `727d4f60c83383b719183246ed8164a09273814562e60a92f8921a161efed04a`。baseline `02b1aecb92dd48d3b6edf237d0908795` 的 runner、runtime、input、source、config 和全部 dependency 都与 scope 一致，`verify_ref` 通过。`validate_execution` 的错误是 `execution did not complete successfully`：status `failed`，exitCode 1，timedOut false。文件和 scope 没有漂移。

`_out_of_file_slow_script` 返回空。side 已有 `sourceForm` `injected` 和 `sourceClass` `about-blank-injected`，function 关键字不再放行宿主修补。同一条 scriptError 是 errorName `SecurityError`，insecure true，parentLine 1447，sourceLineLength 0，keywordAtColumn false，stackShape `other`，receiverId `null`。诊断仍是第 2 行第 3028 列，matched false，base `object`。raw 仍是 sha256 `534609ca23a0472c035bc74092454398420761e448eb632583db28adac35ac2c`。

这组身份说明抛错发生在 about:blank 注入脚本，异常名是 `SecurityError`。它没有给出接收者，也没有可分类的栈帧位置。不能把它写成 `HTMLFormElement.submit`，也不能再按未定位的宿主对象加补丁。没有证书 document POST，也没有同租约回读。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。
