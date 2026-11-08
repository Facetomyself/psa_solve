# ruyijs 求解主线

Date: 2026-11-02
Branch: `feat/ruyijs-solve`

旧刀法把 `env-bound` 直接送进 `environment_patch`，且未点名时默认 `existence`。ruyijs 是真实 Gecko，`Element.attachShadow` 这类 API 本地已有，双条件不成立，同一 digest 空转。

## 主线

```text
RuyiTrace completed
  → parameterAnalysis=want
  → ruyijs_parameter_analysis
  → record_parameter_analysis
  → convert
```

| 记录 | 下一拍 |
|------|--------|
| `local-hit` 且算法可读、不再要宿主 | cloak / 纯算 |
| `env-bound` 且 `environment-gap` 且 `dualCondition=true` 且已点名 `hostBlocker` 或已写 `gapKind` | `environment_patch`（`executor=ruyijs`） |
| `inconclusive`，或双条件未证，或 ruyijs 未点名宿主面 | `compare_facts` |
| 请求边界已对齐 | `companion_response_audit` |

## 记录规则

- `logCapabilities`、资源匹配数、form/iframe/cookie 零计数不能写成 `env-bound`。
- 没有 miss token 写成 `inconclusive`。
- challenge 输出族（FO POST、证书文档 POST）不是 `resource-drift`。
- 存在性刀失败后必须把错误的 `env-bound` 降为 `inconclusive`，不得再发同一把 existence 刀。

## 本 case 已发生的空转

- 分析 run `rj_20261102062310_d7463f5c` 被记成 `env-bound`（匹配数与 DOM 零计数）。
- `environment_patch` 点名 `Element.attachShadow`：browser 读过，ruyijs 本地已有函数且 call=ok，`missTokens=[]`。
- 规划回执 `factsWritten=[]`，revision 停在 55。

下一步是调度恢复后的 `compare_facts`：配对请求族，降 `parameterAnalysis`，禁止默认 existence。

## hold_challenge 2026-11-02

停点：`challengePhase=stuck` 且 `firstDivergence=challenge-state`。验证链没有新的外部事实。停止重复求解。

- 仍是同一道题：live FO POST 404 vs browser POST_200；local cert POST=0；readback 403 accepted=false cookie empty。
- frozen Sep 29 orchestrate vs live CF；isolation 已否掉。
- `hostBlocker` / `gapKind` unset；`attachShadow` 未再发。
- 完成门 unverifiable：ruyijs 未产生 cert-document POST 200，同 lease 业务 readback 非 200。
- 离开条件未满足：未改 `firstDivergence`，未写 `humanActionPending`，未把 challenge 输出写成 `resource-drift`，不得把 `challengePhase` 改回空。
- 本拍不 fact record。规划回执 `resolved`，不是 `needs-human`。
