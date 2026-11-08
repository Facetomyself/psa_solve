# Pure Compute

Case: `psa-cf-5s-shield-20260815`

Browser-free parameter generator. This is the current truth, not a diary.

## Current Stage

- Stage: 未进入。环境补丁门是 `not-ready`，没有成功基线。
- Stable entry: 无 `code.pure.js` / `runtime/*.pure.js`
- `localReproduced`: false
- `transportAdmission`: 页面 `/fo/` h3 已准入；证书 POST 未发出
- `serverAccepted`: false

## Baseline

- Immutable copy: 无
- Canonical input hash: 无独立夹具。浏览器事实指针是 `rt_20260929103550` 的 evidence receipt。
- Output fields: 目标输出是证书页 readback 200。当前没有这份输出。

## Notes

- 纯算停在卡点前面。本地会话还没有 `form.submit`，也没有证书 document POST。
- 在业务 readback 出现之前，不写 `code.base.js`，也不把浏览器成功写成 `serverAccepted`。

<!-- generated:pure-compute -->
workflow-artifacts status: `blocked`
<!-- /generated:pure-compute -->
