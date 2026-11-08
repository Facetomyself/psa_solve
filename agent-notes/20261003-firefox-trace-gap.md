# Firefox / RuyiTrace 卡点分析（2026-10-03）

## 结论先行

Firefox 证据面已经把真实浏览器的 challenge 通过段录全了：`cert GET 403` → `orchestrate GET 200` → 五个 `/fo/` POST → 最后一个 page-host `/fo/` 下发 `cf_clearance` 名 → `cert document POST 200`。当前卡点不是 Firefox trace 没抓到，而是本地 RuyiDOM 没有重现同一个响应分支：它在 `cf-chl-out` 响应后走到 `noform`/诊断 DOM，`form`、`submit` 和证书 document POST 都没有出现。因此这是一条 **semantic/execution boundary**，不是采集边界；`serverAccepted`、`localReproduced` 和独立业务 readback 仍未证明。

## 输入与完整性

- 主证据 run：`rt_20260929103550_341b734038`，`interactive`、`dom-observe`、Firefox 155 baseline、90 秒；`request.json` SHA-256 `37c457ab198818bb95b71ad317450aba1b0e618298fe2ec38ff9df026944d04d`。
- 主证据索引：`evidence/web/ruyitrace/rt_20260929103550_341b734038/evidence-run.json`，SHA-256 `7429c76e812f0ee62f9bd7b7139a56f112d708497392952b137cd5167467218e`；369 artifacts，metrics records 1,137,181，分区含 `cookie/descriptor/domtrace/eval/event/http_packet/storage`。
- receipt：同目录 `receipt.json`，文件 SHA-256 `529d484c35f90ac2bdcab9a3ab332822b04df1263a5fd30ee63e4a8831407f65`，`integrity=pass`，raw root `980d1002ee040e0e513593a412600ad6ef2515b070a7a0b623659764b8b688c2`。
- 交叉 run：`rt_20260928061614_ee71af43b2`（receipt root `fe80c7e81d7b767b24605e6ec3c0fee82de7e40bfbec8c66925f734e8fcdb178`）重复得到同一主线；它的正式摘要见 `agent-notes/20260928-ruyitrace-formal.md`。
- 当前合同状态：`contracts/auto-decision-facts.json` 为 `ruyidom=diverged`、`localReproduced=false`、`serverAccepted=false`、`requestBoundaryAligned=false`、`firstDivergence=environment-gap`、`experimentHygiene=stop-search`。`contracts/workflow-artifacts.v1.json` 对主 run 的 browserObserved 多数为 pass，但 `clearance-fo`、`cert-document-post` 的 local/server 仍为 fail，`executionReadiness=diagnostic-only`。

## Firefox trace 已覆盖的事实

主 run 的 `raw/http_packet/index.jsonl` 有 161 条记录，关键链如下（只保留形状、状态和 header 名）：

| 顺序 | 事实 | 结果 |
|---|---|---|
| 1 | 证书 document GET | `403`，存在 `cf-mitigated: challenge`，写入 `__cf_bm` 名 |
| 2 | `orchestrate/chl_page/v1` | `GET 200`，脚本资源已实际加载 |
| 3 | page-host `/fo/` | `POST 200`，`text/plain`，h3 |
| 4 | Turnstile/challenge-host `/fo/` × 3 | `POST 200`，先 `text/plain`，后两次 `text/html` |
| 5 | clearance `/fo/` 的响应 | 有 `cf-chl-out` / `cf-chl-out-s` header 名；page-host 最后一个响应的 `Set-Cookie` 名含 `cf_clearance`、`__cf_bm` |
| 6 | 证书 document POST | `POST 200`，响应是证书验证页；该响应另写站点 cookie 名 `psa-locale`、`env` |

这与 `docs/web/request-chain.md` 的当前 h/b 形态一致：主站 `/fo/` 两次、Turnstile 主机 `/fo/` 三次；本轮不是必须出现 `eb/managed` 才算浏览器通过。`eb=0` 的事实仍应记录为“未观察到”，不能拿它替代通过判定。`jsd/oneshot` 在证书 POST 之后才出现，不能当作 challenge gate。

RuyiTrace 同时留下了完整的 DOMTrace、eval、event、storage、cookie descriptor 和异步记录；receipt 的 writer/integrity gate 通过，未见 `dropped_*` 或 I/O 错误。它足以证明 Firefox 真实浏览器走到了上述 wire 边界，但敏感 body、cookie/token 原值在证据面被脱敏，只有 header 名、状态、哈希和长度类可以复用。

## 没覆盖、也不能从这批 trace 推出的节点

1. **本地求解分支**：RuyiDOM 在最后一个 `cf-chl-out` 响应后没有走浏览器的表单分支。当前受限 causal observer 明确为 `forms=0`、`submits=0`、`certDocumentPostObserved=false`，最终是 `h2/p/ol` 诊断文案。`window.KP` 在旧桥接记录中缺失；该点是本地执行/语义边界。
2. **`eb/managed`**：主 run 没有 `eb/managed`。这与当前有头 Firefox 的实际 h/b 通过链并不矛盾，但如果旧合同仍要求 `eb`，本 run 没有提供该节点的证据，不能自行补写或把 `jsd` 当成它。
3. **业务 readback**：目标合同要求“同一 lease、清关后约 5 秒的业务 readback 200”。主 run 的 `cert document POST 200` 是 challenge 解除后的证书页导航；其后主要是页面脚本和 analytics/fetch。没有一个被合同标为独立 `business-readback` 的请求/响应对，也没有 readback 内容或业务字段的独立验收，所以不能把这次 `cert POST 200` 升格为最终业务成功。
4. **`serverAccepted` / 纯算 parity**：trace 只能证明浏览器事实。它不证明本地生成了同一 session-bound `fo-body`、同一 `form-body`，也不证明独立采集器在同一 lease 上得到业务 200。当前 facts 和 workflow artifact 都明确保持 false/triage-only。
5. **同 TLS / 可重放性**：跨 urllib、RuyiDOM 和浏览器的材料交接不是同一 TLS 导航；原始 response body、cookie/token 值不能从脱敏 trace 反推出可重放样本。

## 卡点性质：采集边界还是语义边界

判定为 **语义/执行边界**：

- 采集侧：RuyiTrace runtime、index、receipt 均通过；主 run 的 HTTP packet、DOMTrace、eval、event、cookie、storage 分区都落盘，writer 统计没有丢弃或 I/O 错误。Firefox 已经抓到 orchestrate、全部 `/fo/`、`cf_clearance` 名和证书 POST。
- 执行侧：本地桥接给了 `cf-chl-out` 响应后落入 `noform` 分支（历史形状为 3488/诊断文案），而真实 Firefox 的对应清关响应形状为 3792 并继续生成 form/证书 POST；本地没有 form/submit/document POST。`firstDivergence=environment-gap`、`requestBoundaryAligned=false` 与该差异一致。
- 这不是“再把 Firefox trace 开大一点”能解决的缺口，也不是点击是否发生：真实 Firefox 在本轮无感完成，主线差异位于本地执行器对响应/状态/宿主语义的解释和 session 绑定。

注意：`补环境进展清单.md` 里保留了一段 2026-08-15 的历史 `serverAccepted` 成功叙述；它与当前 `workspace.json`、`auto-decision-facts.json`、主 run workflow artifact 不一致，不能覆盖当前事实，后续应按当前合同重新验收。

## 下一刀建议（可执行）

1. **保持 Firefox RuyiTrace 为唯一 browser fact**；Chromium/V8Trace 只做对照，不能登记成主证据或替代 Firefox run。
2. **停在现有 `refuse_host_enumeration` / `stop-search` 闸门**，不要继续枚举相邻 host getter，也不要手工补 `eb`、cookie、token 或 body。下一次材料必须是 fresh、同一 run 的真实响应和同一 session 绑定。
3. **若重新开启本地语义诊断，只做一刀窄切片**：围绕 fresh `orchestrate` 的 `KP`/回调注册与最后一次 `cf-chl-out` 解码，记录“响应 → DOM form/submit → cert POST”的因果边界；对照主 run 的 request-size classes（约 2252、4738、83372、86530、8695），禁止 body replay 和 synthetic cookie。
4. **本地出现 cert POST 后再验收业务**：沿同一 lease 等待约 5 秒，明确记录独立 `business-readback` 的 method/path/status/业务字段摘要；只有该 readback 200 才能把 `serverAccepted` 置为 true，并回填 parity/readiness。
5. **若仍是 noform/诊断分支**，维持 `environment-gap`、`localReproduced=false`、`serverAccepted=false` 和 `triage-only`；不要把 `cf_clearance` 名存在、widget complete、`cert GET→POST 200` 单独当作最终求解成功。

## 证据路径

- 主 Firefox run：`evidence/web/ruyitrace/rt_20260929103550_341b734038/`
- 主 HTTP 索引：`evidence/web/ruyitrace/rt_20260929103550_341b734038/raw/http_packet/index.jsonl`
- 主 receipt：`evidence/web/ruyitrace/rt_20260929103550_341b734038/receipt.json`
- Firefox 正式摘要：`agent-notes/20260928-ruyitrace-formal.md`
- 请求链：`docs/web/request-chain.md`
- 本地因果边界：`agent-notes/20260930-causal-observer-chain.md`、`agent-notes/20260930-causal-observer-live.md`
- 当前决策事实：`contracts/auto-decision-facts.json`
- 当前工作合同：`contracts/workflow-artifacts.v1.json`
- 工作区状态：`workspace.json`、`web-case.json`
