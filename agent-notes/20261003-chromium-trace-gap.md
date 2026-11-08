# Chromium / V8Trace 卡点分析

日期：2026-10-03  
Case：`psa-cf-5s-shield-20260815`  
范围：只读 `workspace/psa_solve` 既有 Chromium/V8Trace、对照摘要和证据目录；没有启动新网络、没有登记 Chromium browser fact、没有写 `serverAccepted`、没有改 `workspace.json` 或源码。

## 输入与完整性

| 输入 | 能证明的范围 | 完整性 / SHA-256 |
|---|---|---|
| `evidence/web/v8trace-chromium/headed-20261003/capture`，run `headed-20261003` | 有头 Chrome 151（V8 15.1）的 CDP capture；120 s 后按 duration 收口 | `summary.json` 为 `de1fe8130e56e71b73de5b2e55d92168b31b569b8bfb540bb157ff998b09a3bd`；`integrityConclusion=partial`、`baselineEligible=false`、无 receipt、无 browser fact |
| `evidence/web/v8trace-chromium/c266ff812e0facbf7/capture`，run `c266ff812e0facbf7` | headless 对照；预算截断前的 3 条 FO | `summary.json` 为 `a29416206a80a7d54246194a2e67fe6a3d57e61b82cf9405718513d26ac08445`；`integrityConclusion=partial`、`stopReason=capture-byte-budget` |
| `evidence/web/v8trace/v8-20261003021537-lhw7em`，run `v8-20261003021537-lhw7em` | patched Node `challenge-fast` 诊断 | `run.json` 为 `9003cb44f263389daf1ace6d75b1ab0015393d7fa1d73e9766a78db169954fcf`；1421 records / 1679 events，目标退出码 1 |
| `agent-notes/20261003-kernel-compare.{md,json}` | 本地 causal observer `a7e045b6cf194921bb229b6741e59b8b` 与有头目录的脱敏边界对照 | md SHA-256 `fb2c945f5f2240cb55aed3bf05eecc62be55c4446e060ec210f33149a3e7308a`；JSON SHA-256 `fffbf901df185661dfabeb275e0f2aa3cd43ec14951ddfe408159c8bfa57f552` |

有头 capture 的能力声明明确关闭 `opcode`、`jscall.detail`、`native detail`、WASM execution、object snapshots 和 raw CDP；HTTP 是 CDP decoded body，不是 wire bytes。它还有 6 个 critical `response-body-unavailable`，其中 1 个是 page-host `/fo/`，所以这不是可升格为 browser fact 的完整记录。

## Chromium 实际覆盖到哪一步

有头 run 证明了真实 Chrome 存在一条可继续的分支：先收到证书页 `GET 403`，随后有 5 条 `/fo/` `POST XHR 200`（page、challenge、challenge、challenge、page），第 4、5 条响应带 `cf-chl-out` / `cf-chl-out-s` 头名；第 5 条附近出现 `cf_clearance` **名称**。之后 `createElement("form")` 计数为 3，首次发生在证书 `Document POST 200` 前约 18 ms；该 POST 的 initiator 是 `other`，随后拿到证书验证页。这个结果足以证明“有头内核能走到 form/证书导航”这一 browser-side 对照事实。

它不能证明完整求解链：

- 第 5 条 page-host FO 的一个响应 body 无法从 CDP 取回；第 3、4 条挑战请求比本地分别多约 9 KB，但当前没有保存可逐字段对齐的 body，不能把差异归给点击、某个 getter 或某个 `eb` 字段。
- `HTMLFormElement.submit` 没有被 hook；因此 `submit binding=0` 不是“没有调用 submit”的证据。能确认的是表单元素和后续 Document POST，不能确认内部调用方式、隐藏字段值或完整 POST envelope。
- 有头窗口只提供 `cf_clearance` 名称，不保留 cookie 值；cookie 名、FO 200 或证书 POST 200 都不等于 PSA 同 lease 业务 readback，也不等于 `serverAccepted=true`。

headless run 只看到 3 条 FO XHR、无 form、无 Document POST、无 `cf-chl-out` 响应头名；它在 byte budget 截断，且是 `HeadlessChrome` 分支，不能解释有头分支，也不能反推本地 Gecko 的 3488 类结果。此前交互式启动失败和 locale/de-elevate/worker 目录问题是采集器边界，不能当成业务语义结论。

patched Node run 更早就停了：stub DOM 里有 39 个 miss、1 个 `TypeError: T[rv(...)][rv(...)] is not a function`，没有 `envcall createElement`、没有 `form.submit`、没有 FO/XHR 或 Document request boundary，request-call 仅为 `node:net open`。因此它只是 Node 侧诊断旁路，无法解释 headed 的 form/noform 分叉，也不能据此补 Gecko。

## 完整 solve 链的缺口

| 链路节点 | 当前证据 | 仍缺什么 |
|---|---|---|
| `orchestrate` | 看到挑战页和 FO 顺序，能观察到部分 DOM/API hook | 没有完整脚本调用因果、响应解码输入和分支判定值；V8 诊断没有 opcode/JSCall detail |
| `fo` | 有头 5 跳的 host 类、method、status、响应类型/长度；本地也有 5 跳骨架 | 关键响应 body 与请求字段没有同一会话、逐字段、可复放的对齐；9 KB 差异保持 opaque |
| `eb` / managed 语义 | 没有 V8Trace 产物把 `eb` 或 managed 字段解码并绑定到分支 | 不能声称 `eb` 已生成、被接受或是 noform 根因 |
| `cf_clearance` | 只看到 set-cookie 名称出现 | 没有值、属性、同 lease 证明，也没有证明它触发了业务放行 |
| form / cert navigation | headed 有 form 计数和证书 Document POST 200；本地 `forms=0`、`submits=0` | 本地仍在第五跳后进入 3488/noform diagnostic，缺自然 form 分支 |
| 业务 readback | 无同一 lease 的约 5 s 业务 readback 200 | `serverAccepted` 仍必须为 false；证书 Document 200 不能替代 `test.py` 验收 |

本地与有头的真正分叉在第五跳响应之后：本地把解码类 3488 的 page-host HTML 归为 `noform`，随后只创建 `h2/p/ol`；有头拿到另一份 HTML 后创建 form 并导航。两边前 5 条 FO 的 method/status/host 类相同，所以现有证据支持“响应语义/输入 envelope 不同导致的语义边界”，不支持“缺一个通用 `HTMLFormElement` 宿主 API”这个解释。`__clickTs` 缺失和 9 KB 请求差目前也未字段对齐，不能作为根因。

## 失败边界判断

这是三层卡点叠加，不是单一 trace 工具失败：

1. **采集边界**：有头 capture 为 partial，无 receipt；关键 FO body 缺失，能力面又关闭了 opcode、JSCall detail 和 raw CDP。headless 还被 byte budget 截断。
2. **执行边界**：patched Node 的 stub DOM 在 TypeError 前终止，连 FO boundary 都没到；它没有资格提供环境补丁事实。
3. **语义 / 验收边界**：本地收到的第五跳 HTML 走 noform diagnostic，无法与有头的 form 分支做 body/字段因果对齐；即便有头出现 Document 200，也没有业务 readback，故不能闭合协议合同。

## 下一刀建议

1. 继续把 `browserFactPlane` 锁在 RuyiTrace；本次 Chromium 目录只作 kernel comparison，不登记为 browser fact，也不因已有 CDP capture 自动启用 `cdp-reverse` debugger。
2. 若确实要再做 Chromium 对照，先做一次通过完整 integrity gates 的采集：保证 5 条 FO（尤其 page-host 第 5 条）响应 body 可取、避免 byte/duration 截断，并保留请求/响应的脱敏字段级摘要；只有需要确定分支输入时才开 `jscall.detail`，不做泛化 getter 扫描。
3. 主线应在同一 fresh lease 的 Gecko 证据里对齐第 3/4/5 跳 response envelope、`cf-chl-out` 变体和分支解码结果；不要重放另一 run 的 FO body，不要把 3488 当因果常量，不要把 9 KB opaque 差值归因到点击。
4. 只有本地自然产生 form 并发出证书 Document 后，才继续同 lease 的约 5 s 业务 readback；由 `test.py` 的真实 readback 写 `serverAccepted`。不要手发 token、手造 clearance 或把任意 200 提升为接受。
5. `v8trace` patched Node 保持侧写目录；39 个 miss 和 TypeError 不能直接转成 `code.js` / Gecko patch。

## 证据路径

- `D:\reverse_ENV\workspace\psa_solve\agent-notes\20261003-v8trace-headed.md`
- `D:\reverse_ENV\workspace\psa_solve\agent-notes\20261003-v8trace-headed.json`
- `D:\reverse_ENV\workspace\psa_solve\agent-notes\20261003-v8trace-bottleneck.md`
- `D:\reverse_ENV\workspace\psa_solve\agent-notes\20261003-kernel-compare.md`
- `D:\reverse_ENV\workspace\psa_solve\evidence\web\v8trace-chromium\headed-20261003\capture\summary.json`
- `D:\reverse_ENV\workspace\psa_solve\evidence\web\v8trace-chromium\headed-20261003\capture\gaps.json`
- `D:\reverse_ENV\workspace\psa_solve\evidence\web\v8trace\v8-20261003021537-lhw7em\run.json`
- `D:\reverse_ENV\workspace\psa_solve\evidence\web\v8trace\v8-20261003021537-lhw7em\analysis\round_summary.json`
- `D:\reverse_ENV\workspace\psa_solve\evidence\web\v8trace-chromium\c266ff812e0facbf7\capture\summary.json`
- `D:\reverse_ENV\workspace\psa_solve\agent-notes\20261003-solver-vs-headed.md`

结论：Chromium trace 已证明“真实 headed 浏览器可以从第五跳进入 form→证书导航”，但没有提供可复放的 FO/响应语义，也没有业务 readback；Firefox/Gecko 主线卡点因此仍是第五跳后的 noform 分支，当前不能宣称完整 solve 或 server acceptance。
