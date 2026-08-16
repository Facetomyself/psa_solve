# Triage

Case: `psa-cf-5s-shield-20260815`

## 结论等级

- Case 等级：`partial`（缺口链定位完成，求解未闭合）
- 深度：L3（运行时定位——插桩 + 三环境对照 + 源码级偏移）
- 未声称：任何"已复现求解"或"serverAccepted"

## 阻塞点

| 阻塞 | 定性 | 位置 |
|------|------|------|
| `_cf_chl_opt.yQYB9` 非函数（object） | execution-boundary（yQYB9 函数注册段被引擎环境分支跳过） | orchestrate 180073 ID 状态机 case '5' |

## 已验证事实（不重做）

1. 挑战形态：managed 强制（cType managed / cTplV 5 / cvId 3），无感自动通过（Turnstile non-interactive）
2. 提交链：fo flow 六段 URL 模板（Reqable 实抓）
3. 引擎缺口阶梯：Node（DOM 面大）< iv8（createElementNS）< RuyiDOM（yQYB9 注册链）
4. 引擎层三修复：meta CSP / history.replaceState / storage 包装（均有证据）

## 候选路线（下一步决策）

| 路线 | 成本 | 说明 |
|------|------|------|
| A. 继续定位 yQYB9 注册点 | 中 | 同插桩法（搜 `_cf_chl_opt` 键的赋值序列）；预计数轮 |
| B. 浏览器求解器注入 | 中 | 浏览器池解挑战拿 cf_clearance → 注入采集器会话；工程可行，绕过纯算 |
| C. iv8 深挖 | 低 | iv8 静默退出点定位（错误不抛，需逐步插桩）；API 面小于 RuyiDOM |

## 证据索引

- 浏览器事实：evidence/web/ruyitrace/rt_20260815060651_eb196ed770/（receipt integrity pass）
- v8trace：evidence/web/v8trace/v8-20260815070607-0a39cz/、v8-20260815071000-g8sotl/、v8-20260815075849-x7h32q/
- iv8：evidence/web/iv8/iv8-cf-probe-{1..8}/result.json
- 材料：challenge-material/（403 页 ×2、orchestrate 229KB、jsd 21KB）
- 求解器：ruyidom_cf_shield_v1.js（含全部插桩）、ruyidom_cf_bisect.js、v8trace_orchestrate_runner.js、iv8_cf_shield_probe.py

## 风险与限制

- orchestrate 混淆代码的插桩只读诊断（未改控制流，除 switch 语法错误已回退）
- 挑战材料（cH/cN）时间敏感，续作需重抓 fresh 页
- RuyiDOM runtime 是 hash 锁的课程材料，引擎本体不可改
