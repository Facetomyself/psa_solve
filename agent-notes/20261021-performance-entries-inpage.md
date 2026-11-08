# 页面区 performance entries

日期：2026-10-21

动作：`repair_submit_host_behavior`。只改 `document-principal.js` 里 `performance.getEntries` 和 `getEntriesByType`。

## 改动

页面 `Function` 读取本窗口资源日志，筛 `script` / `iframe` / `style`，返回内容数组。`getEntries` 把页面计数加一。侧记 `entries` 在这个计数存在时读它。`getEntriesByType` 不加这个计数。`Function` 失败时仍用原来的 `Cu.exportFunction`。XHR、Date、PerformanceObserver、脚本时限 13、真 eval、`__watchEval` 都没改。

已有测试 `test_shipped_performance_now_advances_from_date` 执行了这具函数。通过，0.071s。探针打印 `entries-ok 2`。

## 重签

- helper sha256 `cad831df04859bc28b4cb3a85ea7b9dabd617e8d9b57445e5b2e6806f8a09a85`
- scope `12e9914655ebf4fd56fe6b3fb1b7ac10c74831a1dd8084d759280721bf3714e5`
- priorScope `8ed7e127a4352a7ff940147fd5c2f41b0202a7950f1c7f419329857f1d164a62`，baseline `e9251003e0514f5d8dd6b4d39debe9fd`
- runner `31746c03fd9890d4` 与 geckoLib `9f21705d909f5e5c` 未变
- `load_scope` 通过后才跑官方 baseline

## 官方 baseline

`c9d67de103124d38bbc60b3ea4370527`：exitCode=1，timedOut=false，约 22.733s。失败原因是执行未成功完成。

raw 只有 `host-diagnostic` 和 `summary`，225 字节，与 `e9251003e0514f5d8dd6b4d39debe9fd`、`869824e67a524e90ab47ab86016fd64b` 字节相同。诊断是第 1 行第 1337365 列，matched false，base `object`。侧记 kind=`other`，class=`slow-script`，sourceClass=`other`，sourceForm=`token`。`entries` 1，`observe` 1，`iframeParentConnected` `yes`。watch 计数仍是 0。

没有其他事件行。采集器不记 wire、necko、resp。没有工具证据证明证书 document POST 或约 5 秒后的同租约 HTTP 200 已发生。列号只记慢脚本落点，不证明 eval 已返回，也不证明没有网络请求。调用点仍是第 75507 列。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。
