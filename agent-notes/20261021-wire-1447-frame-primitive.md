# parentLine 1447 与 frame 原语接线

状态：只核对。helper 未改。scope 未重签。没有新的官方 baseline。没有再跑 `next`。完成轴未写。

磁盘文件与 scope `727d4f60c83383b719183246ed8164a09273814562e60a92f8921a161efed04a` 的绑定哈希相同，也就是产生官方 baseline `02b1aecb92dd48d3b6edf237d0908795` 的那一组：

- helper `document-principal.js` sha256 `40a98a9f2e93ce20c5c97bd697d5929fbac9cc5d10c3a8cf0b885cd6705faf57`
- runner `host_submit_collector.py` sha256 `c563864c6a34cd56551892e39faa7e7c1dae04056c1ba43346edde01938a5f6b`，与该执行的 runner 相同
- gecko `ruyidom.js` sha256 `9f21705d909f5e5c11bcf06af2187be7446b2112974090a3981e04a3cd11ce61`

正式路径是：采集器 `loadSubScript` 载入 helper，调用 `installDocumentPrincipalPreserve(RuyiDOM)`，再 `new RuyiDOM(html, {url, beforeParse})`。`beforeParse` 只做 `classify`。helper 第 139 行保存原来的 `_replaceDocumentHTML`，第 1565 行换成 `wrapped`。构造器在 html 加 url 时调用这个方法。`wrapped` 第 1539 行调用 `installFrameWindowPrimitive(this.window)`，第 1541 行 `orig.apply` 进入锁定的 `_replaceDocumentHTML`。该方法第 1447 行是 `document.write` 的 `Cu.evalInSandbox`，Firefox 把它记成 parentLine 1447。已发布测试 `test_shipped_frame_content_window_comparison_survives_security_error` 断言这次调用位于 `installPageLocationPrimitive` 之后、`orig.apply` 之前。

已发布门对这张 side 仍返回 `repair_null_receiver_identity`。约束含 `no-new-host-surface`，没有 `one-host-behavior`。接线不缺，所以本拍不补第二处 contentWindow、Location、window 或 `Object.prototype`。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 仍是 false。`experimentHygiene` 仍是 `ok`。

阻塞：接收者仍空。没有证书 document POST，也没有同租约回读。
下一步：本拍停手，不再 `next`。
