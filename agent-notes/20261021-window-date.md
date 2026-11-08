# 页面窗口 Date 构造器

2026-10-21。盖章 `repair_submit_host_behavior`，`turnGate=blocked`。只改了一处宿主行为，没有再跑 `next`。

页面窗口原先只把 `Date.now` 拨到挑战锚点，无参 `Date()` / `new Date()` 仍走墙钟。沙箱全局已经有自己的构造器，这次不给 `installChallengeClock(sb)` 加第二次包装。`installChallengeClock(this.window, true)` 在内容区用 `challengeDate` 换成同一个 `current()`。多参数、`parse`、`UTC` 和原型仍是原来的构造器。`dom.max_script_run_time` 仍是 13。真 eval 仍在，没有恢复 pad eval，没有改 `setTimeout`。

`test_shipped_window_date_constructor_uses_challenge_clock` 从已发布的 `document-principal.js` 抽出 `challengeDate`，用 Node 核对无参时间、字符串形式、`now`、显式参数和原型。

helper sha256 `05f895e7598ae0f6bcc4ac6fe494317cfe1259740adcd084772c8dd6d7db51e0`。scope `272255021f2d57a76557e4f93047a71dee58e060c7fefa2c9769982cc17e677e`。priorScope 是 `9776d304a14379f1`，其中 baseline 是 `1adb882440784c2598bfe4e52395139c`。runner sha256 仍是 `31746c03fd9890d48317faec1e2aa5ff5f99c7d63e0ce27c87b0956a5fa54d8a`。geckoLib 仍是 `9f21705d909f5e5c11bcf06af2187be7446b2112974090a3981e04a3cd11ce61`。`load_scope` 通过后才跑。

官方 baseline `fedb3277fd974be4beda2c3e1fb3ca12`：status=failed，exitCode=1，timedOut=false，墙钟约 22.717s。失败原因是执行未成功完成。raw 只有 `host-diagnostic` 和 `summary`。诊断是第 1 行第 1337365 列，matched false，base=`object`。side 的 scriptError 是 class=`slow-script`，kind=`other`，sourceClass=`other`，sourceForm=`token`。`getEntries` 仍是 function。host-observation 为 0。没有证书 document POST。调用点仍是第 75507 列。

前一条官方 baseline `1adb8824` 停在源行内第 55371 列。这一条回到源行外的第 1337365 列，没有到达 `HTMLFormElement.submit`。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。第 1337365 列没有写成观察。
