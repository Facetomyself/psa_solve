# 2026-10-22 放开调试器后停在第 55371 列

执行时的盖章是 `2026-10-21T21:53:39Z` 的 `repair_submit_host_behavior`，`turnGate=blocked`。这一拍只改采集器里的一处行为，没有改 `document-principal.js`。

第 30458 列不是缺的宿主 API。文件级词法只看到语言关键字，落在运算符函数里。沙箱 `Date` 和 `performance.now` 在锚点之后按墙钟增加，这一拍不改时钟，时限仍是 13。解释器每次进入都还挂着 `Debugger.onEnterFrame`，并且全局一直是 debuggee。观察完成后这条钩子仍留着，所以看门狗会抽到运算符里的列。

这一处在 `j5` 与 `jj` 两处观察都已经结束时，清掉 `onEnterFrame` 和 `onExceptionUnwind`，再 `removeAllDebuggees`。卸不掉 debuggee 时只清钩子。helper sha256 仍是 `6ad5ffb19ea7d746588f7ac4a8e604c8bb9c5bb8b98895f62455b4822eed0a0d`。runner sha256 改为 `b12043c21334bcf3b799314f0a36adb7b25fba1f7f39c4451245912fcabe12b7`。scope 重签为 `60e8a133a4f912d098d3422113413d315940e20f5ac9ce41724f673e7aa8c5a5`，`2650dcba2b133020ea31aab1dfc7693547af903ccfe51ddc69068af79ec2acbc` 与 baseline `e33f35e4e6044dc7ae37af85fb92c6ac` 留在 priorScope。

官方 baseline `bf38ae972145403d83164eae108e4bf3`：pid 35252，耗时 24722507700 ns，exitCode 1，timedOut false。side 的 `debuggee` 是 `released`。`j5` 只记到 2 次，`jj` 只记到 2 次，因为计数在放开后停止。诊断离开第 30458 列，现为源文件内第 1 行第 55371 列，kind `other`，class `slow-script`，sourceForm `token`，sourceClass `other`，没有 errorName、receiverState、receiverId。这一列是解释器 `for` 循环头上的 1 字母局部量，不是宿主调用。raw sha256 `731459ca7fda730ce26ddc27e4f3ef3736d0a3128466f0f987eb3c994773f2b9`，223 字节。side sha256 `ca42cb1f2f5e1f4b580c8b2c47052778518131c836d755800f8eb5421d8f22b3`，640 字节。事件只有 `host-diagnostic` 和 `summary`，matched false。没有证书 document POST，也没有同租约回读。完成轴保持 false。

随后 `next` 盖成 `repair_submit_host_behavior` / `blocked` / `2026-10-21T22:15:40Z`。新印仍指向这张第 55371 列回执。该列不是宿主 API，这一拍不再开第二处宿主面。
