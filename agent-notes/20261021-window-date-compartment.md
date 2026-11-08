# 页面 Date 改在页面区构造

2026-10-21。先核对上一回为什么从第 55371 列退回第 1337365 列，再跑一次 `next`。新盖章仍是 `repair_submit_host_behavior`，`turnGate=blocked`。只改了一处，没有再跑 `next`。

上一回 baseline `fedb3277fd974be4beda2c3e1fb3ca12` 用 `host.eval` 安装页面 `Date`。间接 eval 并不在调用方词法环境里执行；按语言规则，它在被调用的 eval 函数所属 Realm 的全局环境执行。`host.eval` 当时是页面原生 eval、沙箱 eval，还是跨区包装，这份笔记没有核验。`catch` 里还会把 chrome 函数赋给 `host.Date`。同一次回执写过的 `iframe-parent.json` 仍是 `observe` 1、`entries` 1，`iframeParentConnected` 为 yes。观察者有触发。看门狗列是 1337365。这只说明慢脚本落点变了，不能单独证明某一次 eval 没有返回。源行内第 55371 列没有再出现在这张诊断里。

这一处只改安装：`challengeDateInstallBody` 交给页面 `Function`，`Patched` 在页面区诞生。返回空或抛错时不替换构造器，也不再把 chrome 函数赋上去。`Date.now` 的挑战锚点包装还在。沙箱调用仍不带构造器开关。脚本时限仍是 13。真 eval 仍在。`setTimeout` 没有替换。`__watchEval` 没有打开。

`test_shipped_window_date_constructor_uses_challenge_clock` 从已发布 helper 抽出 `challengeDate` 和 `challengeDateInstallBody`，用 `new Function` 跑这条安装体。

helper sha256 `36f189d3d9dd28d9c34bafe56d7fcab7f1648347569e2ef26cf3d5939d728257`。scope `40ffac4b2c670dd8a89bf48d2ff6bdfc020928ba5285969b8b82da27865fc7d9`。priorScope 是 `272255021f2d57a7`，其中 baseline 是 `fedb3277fd974be4beda2c3e1fb3ca12`。runner sha256 仍是 `31746c03fd9890d48317faec1e2aa5ff5f99c7d63e0ce27c87b0956a5fa54d8a`。geckoLib 仍是 `9f21705d909f5e5c11bcf06af2187be7446b2112974090a3981e04a3cd11ce61`。`load_scope` 通过后才跑。

官方 baseline `f970b6fc4a674df984364ea884a94e01`：status=failed，exitCode=1，timedOut=false，墙钟约 22.735s。失败原因是执行未成功完成。raw 只有 `host-diagnostic` 和 `summary`。诊断是第 1 行第 1337365 列，matched false，base=`object`。scriptError 是 class=`slow-script`，kind=`other`，sourceClass=`other`，sourceForm=`token`。`getEntries` 仍是 function。host-observation 为 0。`iframe-parent.json` 仍是 `observe` 1、`entries` 1。没有证书 document POST。调用点仍是第 75507 列。

页面区构造没有把列送回 55371。只要页面构造器被换成和 `Date.now` 共用锚点的 `Patched`，看门狗就留在源行外第 1337365 列。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。第 1337365 列没有写成观察。
