# 新 Firefox trace 与本地 runner 对照 / 2026-10-05

## 范围与结论

- 只读现有 runner、历史诊断 JSON、新 run 既有 DOMTrace、HTTP packet、JSCall dictionary/stats 与合同；没有执行 target JS、启动浏览器、capture、canary、网络或修改 facts。
- 新观察 run：`rt_20261005125421_1d84c46dcd`；旧 canonical baseline：`rt_20260929103550_341b734038`。
- 新 trace 可推进的是已有证据的 source/identity 对齐与提交边界审计，不足以自动授权隔离 canary 修正执行。`refuse_host_enumeration` / `blocked` 不因这份对照解除。
- mirror 的 factory 错型与查询失真是可证 runner defect；该缺陷是否造成历史 `It` 首错、是否与 RuyiDOM 的 response-to-diagnostic 分支有关，仍未证明。
- 上轮“新 trace 直接否定 local receiver 假设”的说法过强：它证明新 run 两条具体调用的真实 receiver，不会否定一个不同 source、不同 realm 的本地 constructor 读数。严谨结论是不能据此给 `HTMLScriptElement` 添加 `attachShadow`，也不能声明 patch gate ready。

## Browser-to-local 对照表

| 面 | 新 Firefox browser fact | mirror / realm-probe 既有 local evidence | 判定 |
| --- | --- | --- | --- |
| API attachShadow source/call site | pid 51372，`xe`，API line 2 col 74808；createElement 在 col 74781 | mirror 载入 9/28 API；未记录该 API 调用的 local source hash、receiver identity 与对应 offset | 同类路径，不是已锁定的 browser/local call pair |
| API receiver 与创建路径 | DOMTrace 83043 `createElement("div")` 返回 HTMLDivElement，83044 attachShadow 的 receiver nativeId 与返回 nativeId 相同 | mirror `createElement(t)` 丢弃 t，固定 `makeElement()`，默认 SCRIPT | factory defect 可证；不等于 target parity |
| iframe attachShadow source/call site | pid 50068，`df`，iframe line 1 col 207126；上一条 body getter 在 col 207105 | 历史 iframe `Timeout.It`，表达式 `x[bf(CW.IZ)][bf(CW.IM)](b)`，原始 offset 约 214416；instrumented offset 改变 | source hash 不同，不能把 df 对应成 It |
| iframe receiver 与读取路径 | trace 101 的 `Document.get body` 返回 HTMLBodyElement；102 的 attachShadow receiver 是同 nativeId | local 只记录 `constructor.name=HTMLScriptElement`；没有 tag、ownerDocument、identity、decoded first key 或 `receiver===document.body` | 新 run 的 body 来源已证；历史 local 来源缺证 |
| attachShadow 参数/返回 | 参数只见 Object identity；返回 ShadowRoot identity | local TypeError 表明方法不可调用；无返回值；没有实参深记录 | 不足以确定 mode 或补完整 ShadowRoot 行为 |
| create/query | browser 已证明上述 createElement/body getter identity 链；未全量追踪查询 | mirror factory 丢 tag；queries 忽略 this，miss 伪造 DIV，重查重建对象；head/body/root 默认 SCRIPT | factory、query、document typing/identity defect 可证；不应一轮混修 |
| iframe realm | browser body 属于 iframe HTMLDocument，iframe source 独立 | mirror 间接 eval 到共享 global/window/document，临时更换 currentScript/location；无独立 frame document | 已证 runner 模型差异；具体首错归因未证 |
| source hash | 新 iframe inline script 238893 chars，SHA-256 `eee05641ead359eed27d49331f02cab589feca0c6373b41305e03eb72e9870a7` | 历史 iframe 238636 chars，SHA-256 `05102bb5158cd0ba9a41329021f124cad8778a9a556db9a0e802b11c07115262` | 明确不同，不能称 source-aligned |
| form.submit | pid 51372 trace 90886，HTMLFormElement，jj line 1 col 75507，随后 cert document POST 200 | mirror 给所有 element 通用 submit，只设置 `__ruyiFormSubmit`，不建 document POST；历史 realm result 没有 submit evidence，foRequests=0 | browser 提交存在；mirror stub 不是请求边界 |
| cf-chl-out → document POST | page-host FO seq40 响应含 cf-chl-out；随后 form.submit；document POST seq41 200 | 历史 RuyiDOM complete-to-diagnostic：cf-chl-out 后先 createElement h2、排障 DOM，无 form/submit/POST | 输出分支差异真实但跨会话/runner；未锁定 first causal divergence |

## 同 run source 与 native identity 证据

以下 nativeId 只作本地 evidence identity 使用，不是跨 run 映射。

### API div 链

- 文件：`evidence/web/ruyitrace/rt_20261005125421_1d84c46dcd/raw/domtrace/trace_process_51372.ndjson`。
- 83043：seq 83069，origin_call_id 2687，Document.createElement args `["div"]`，returnObj `id=000000000000040e` / `nativeId=08e157a35c264ce0` / `HTMLDivElement`。
- 83044：seq 83070，origin_call_id 2688，Element.attachShadow thisObj 是相同 id/nativeId/class，return ShadowRoot。
- source：`https://challenges.cloudflare.com/turnstile/v0/b/d76008a69eab/api.js` 的本 run query variant；`xe` line 2 col 74781 → 74808。
- 对应 packet：`raw/http_packet/000006_GET_200_challenges.cloudflare.com_turnstile_v0_b_d76008a69eab_api.js_c7858510_pid48180_400000013.http_packet.json`。
- API response text length 86732；UTF-8 SHA-256 `76763bb46224400a11af989831d62d06629aba6f67d50cac96afae4a590adf59`，等于 HTTP index 的 responseSha256。

### iframe body 链

- 文件：`.../raw/domtrace/trace_process_50068.ndjson`。
- 79：seq81，Document.get body，HTMLDocument nativeId `ecd29e368194f82c`，返回 HTMLBodyElement `id=00000000000000ec` / `nativeId=8ca81f311803363c`；`df` line 1 col 206714。
- 101：seq103，origin_call_id1030，相同 document 的 get body，返回相同 BODY identity；`df` line 1 col 207105。
- 102：seq104，origin_call_id1032，Element.attachShadow，thisObj 是相同 BODY identity；`df` line 1 col207126；返回 ShadowRoot。
- source 是本 run `/cdn-cgi/challenge-platform/h/b/turnstile/f/av0/rch/7czq1/...` 的 iframe；不是旧 `/rch/4crrq/...` source。
- packet：`raw/http_packet/000010_GET_200_challenges.cloudflare.com_cdn-cgi_challenge-platform_h_b_turnstile_f_av0_rch_7czq1_0x4AA_05c807ac_pid48180_400000016.http_packet.json`。
- 以 mirror 相同的首个 inline script extraction 方式读取 packet text，未执行脚本：length238893，UTF-8 SHA-256 `eee05641ead359eed27d49331f02cab589feca0c6373b41305e03eb72e9870a7`。
- HTTP 整个 iframe document responseSha256 `4f73fec288f4e19c44ea54403ff35f95443e9ed28a15d184e04b1a0e6e5446d0`，不能拿 document hash 与 inline script hash 直接相比。

### submit 与 POST 时序

- `trace_process_51372.ndjson:90886`：seq90993，ts1791204889346，origin_call_id5270，HTMLFormElement.submit，receiver nativeId `5979349c822408c8`，JS id 空。stack `jj` col75507 → `run` col54155 → `jI` col65697，orchestrate line1。
- page-host FO seq40：endMs1791204889326，status200，响应 header name `cf-chl-out` 与 `cf-chl-out-s` 存在，body text3792 chars。只读取 header names，不输出值。
- cert document POST seq41：startMs1791204889366，endMs1791204890532，status200，responseSha256 `3632bcb6ae9c24ad8adc4c7e9e2a79b270fd271965a6f4880a573346ea38cdd6`。
- POST originPid51372 与 submit 一致，但 `originCallId=0`、`correlationStatus=no_source_context`，没有 submit → channel 的直接 call-id linkage。存在紧邻同进程时序，不应伪称完整因果 correlation。
- 这不是独立同 lease 业务 GET/readback，不足以写 serverAccepted。

## Trace 设置与覆盖限制

request.json 确认 interactive、baseline、60s、traceLimit500000；JSCall filter/detail/source 是 iframe URL 子串，native detail 列表含 create/query/attachShadow，不含 submit。API attachShadow 与 form.submit 的上述事实来自 DOMTrace，不是已完成 JSCall detail 深参数对齐。

| stats | iframe pid50068 | API/orchestrate pid51372 | 解释 |
| --- | --- | --- | --- |
| DOMTrace session_stopped.complete | false，seq500344 | true，seq91115 | 新 run 不是全部 DOMTrace 完整；已观测前段两条链仍可用 |
| DOMTrace writer dropped_* / io_errors | 全0 | 全0 | writer 无丢包不等于 producer 无截断 |
| JSCall total limit 配置 | 100000 | 100000 | 配置值，不是已 hit |
| recorded / dropped_limit | 42528 / 0 | 5561 / 0 | 没证据表明 total limit hit |
| per_func_limit 配置 | 1024 | 1024 | 3.3 的该 run 仍显式配置1024 |
| max func records / 达到1024函数数 | 1024 / 17 | 321 / 0 | iframe17个函数触及配置阈值；stats 未给 omitted-call count，不能宣布具体丢了多少 |
| dropped_gate | 611 | 611 | 存在 gate 排除，不等于 writer dropped |
| sources_unavailable | 3 | 0 | iframe还有 source覆盖缺失 |
| dropped_no_func_id / dropped_chunks / io_errors | 0 / 0 / 0 | 0 / 0 / 0 | 不等于 object identity 参数有深内容 |

- 逐个 DOMTrace 文件尾部核查：14个 process trace 中，50068 与61640的 `complete=false`，其余12个为true。不是所有关键 writer 都受限，50068明确是本次已识别的 iframe；61640的作用本切片未归因。
- `receipt.integrity=pass` 是395个产物的内容/索引完整性，不授予调用全覆盖。`sources_unavailable=3`、函数达到阈值、producer complete=false 需独立记录。
- `50068.detail.bin` 1314744bytes/hash `69afb5d9f9ebf15796d7c5fdd6bf50760fd753aedddac7b152dc9d4f6e2dcad5`；`51372.detail.bin`11548bytes/hash `5774b51ea8507ad77800e9bc7b3a89e14e282ffd26d644b29173b1fea5f590a6`；receipt 两者 indexed/indexMatch=true。
- 原始 detail 已在 receipt 中，不代表已做窄解码与 semantic pointer/identity receipt。本切片未解码二进制，不把 `.bin` 的存在当参数事实。
- DOMTrace 的 options 参数是 `Object`，nativeId为0；submit JS id为空但nativeId非空。不能断言 `{mode:'closed'}` 或完整跨平面 JS/native identity。

## Runner defect 与缺证据分类

### 可证 runner defect

- `mirror-canary.js:114-115`：createElement/NS丢弃tag；`:121-122` head/body/root默认SCRIPT；`:47,60`将其设成script tag/prototype。
- `mirror-canary.js:51-52,117-119`：element查询忽略this、document ID查询忽略id、miss伪造DIV；class查询从顶层旧HTML重建而非持有live node identity。
- `mirror-canary.js:241-245`：iframe沿用共享document/global，只改currentScript/location然后eval；不同于独立iframe document/realm。
- `mirror-canary.js:55`：所有元素通用submit只写布尔值，不能产出cert document请求；这一stub的存在不是browser form submission实现。

### 仍缺证据

- `realm-probe-canary.js:118-120`只记录constructor.name，不能判定历史receiver实际是body、factory产物还是真script。
- 历史x-call与fresh browser df源hash明确不同，尚无同source call-site与receiver-origin对照。
- `runtime/lib/iframe-realm.js:342,485-500`保留tag、持有owning document、createElement传tag；frame模式构造独立vm.Context，因此不能拿它当mirror修复后的rerun。其plain对象/constructor stubs也不具完整browser branding；本切片不为其新加API。
- RuyiDOM的最后FO→diagnostic分支在不同live baseline发生；mirror首错在FO=0发生，二者不是已证同一根因。

## 最新观察与权威合同不一致

- `web-case.json:49` activeRuns.ruyitrace指向新run，但`:66-68` artifacts中的receipt仍指旧9/29run。
- `contracts/workflow-artifacts.v1.json`的canonicalInput、request shapes、resources和environmentCoverage仍引用旧9/29run；其末尾还注明resource contentHash等是class-label hash，不是rotating source byte hash。
- 因而新run目前是最新observational supplement，不是自动替换后的authoritative canonical baseline。不得拼接新receiver事实、旧source/nonce/response、旧contract再声称parity。
- 本切片不替换合同，不写environmentPatchGate、hostProbe、experimentHygiene、acceptance或dispatcher facts。

## 建议下一步与授权判断

当前事实不足以授权一个“source-aligned最小修正验证”：没有source一致、local receiver provenance、baseline合同一致与dispatcher许可。一般“推进”不是绕过blocked进行canary的授权。

允许推进的只读材料处理是：针对现有同run数据补窄detail解码和source/identity receipt，标清trace覆盖限制；由主线判断是继续旧canonical baseline的匹配证据，还是正式重建新baseline合同，不能只改activeRuns。无需立即重采Chromium或Firefox。

若未来门禁明确允许验证，最小候选应是factory/document typing这一单surface的隔离副本修正，并记录actual tag、ownerDocument、stable identity、creation/query来源与`receiver===document.body`；不同时补attachShadow、queries、ShadowRoot、form transport，也不修改target JS/opaque response。这个候选是设计建议，不是本轮执行许可。

业务闭环仍须同一真实lease上的本地请求边界与独立readback；浏览器POST200不能替代localReproduced/requestBoundaryAligned/serverAccepted。
