# ruyijs 分支意图

Date: 2026-11-02
Branch: `feat/ruyijs-solve`

用户点名 `workspace/psa_solve`：开分支，先用 ruyijs 完成该 solve，后续再扩展到纯 Node 补环境。

## 本分支完成门

- 执行器：`localJsEngine=ruyijs`
- 浏览器只作行为 oracle，不作为 ruyijs 求解运行依赖
- 同一 fresh 输入与 session：请求响应、目标提交、parity、约 5 秒后同 lease 独立业务 readback 200
- 不以浏览器成功替代 ruyijs 完成
- 纯 Node 补环境不作为本分支完成门

## 调度输入

- `taskClass=web`
- `evidencePointers.case=web-case.json`
- `evidencePointers.facts=contracts/auto-decision-facts.json`
- 历史 case 缺 `parameterAnalysis` 时按 skipped 走 RuyiDOM；本分支要把 `parameterAnalysis` 写成 `want`，让 dispatcher 先给 `ruyijs_parameter_analysis`

## ruyijs 主线（本分支）

```text
RuyiTrace completed
  → ruyijs_parameter_analysis（隔离门；0.1.3 可 runtime-pending）
  → record_parameter_analysis
       local-hit + 算法可读 + 不再要宿主 → cloak/purecalc
       有 miss token 才 env-bound
       日志/匹配数/DOM 零计数 → inconclusive
  → env-bound 且 environment-gap 且 dualCondition 且已点名 hostBlocker
       → environment_patch（executor=ruyijs；禁止默认 existence）
  → 其余 → compare_facts（配对请求族；输出族不是 resource-drift）
```

存在性刀失败（本地已有该 API）必须把 `parameterAnalysis` 写成 `inconclusive`，不得再发同一把 existence 刀。纯 Node 补环境仍不是本分支完成门。
