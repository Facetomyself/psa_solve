# Risk Analysis

Case: `psa-cf-5s-shield-20260815`

Risk signals, lease boundary, and current ceiling. The machine contracts are `contracts/risk-control-plan.v1.json` and `contracts/risk-control-receipt.v1.json`.

## Notes

- 当前挑战是点击题。有头由人手点过。本地用可信鼠标移动和一次点击三连，widget 能完成并拿到 `cf_clearance`。
- 已排除：空配置档仍能提交，所以残留 cookie 不是有头成功的原因。应用层代理是 direct；本机 TUN 开着，但同一台机器的有头对照当天完成了证书 POST。
- 卫生：`experimentHygiene=stop-search`。不重放别的会话的 `/fo/` 正文，不把解码首字节改成 85，不定义 `window.KP`。
- 没有扩容 lease。一次只跑一轮新挑战。`cf_clearance` 这个名字不是业务放行。本类不是 scaled-collection，所以没有 `risk-control-plan`，生成块保持未填。

<!-- generated:risk-analysis -->
TEMPLATE-UNFILLED
<!-- /generated:risk-analysis -->
