# Chromium trace 配置审计与最小方案

日期：2026-10-05。等级：static-verified；目标运行验证：runtime-pending。

范围：只读锁定 runtime、wrapper、preset 与 headed capture 的小型 manifest。未启动浏览器、capture 或目标网络，未修改 runner、dispatcher 或业务事实。状态文件为 `D:/reverse_ENV/workspace/psa_solve/workspace.json`；会话句柄：无。当前 HEAD/合同迁移检查由主线程处理，本文不解闸。

## 结论

需要新的有界浏览器证据，问题必须收窄为：`createElement/NS` 返回对象是否成为后续 query/host call 的 receiver，处于哪个 realm；最后 FO 响应之后为何没有目标 document POST。现有 headed run 抓到完成分支，但缺响应正文且没有通过完整 browser-fact gates，不能作为新 patch 的双条件依据。

Chromium 可做独立内核对照，但现成 `env-hooks` 只能补一部分接收者来源；它不能直接证实 `attachShadow` 接收者的 tag/constructor。主事实仍为 Firefox 时，Chromium 结果不混入 Firefox 补丁依据。

## 现有 headed-20261003 的明确缺口

- `capture/launch.json` 为 `backend=chrome-cdp`、`headless=false`，不是 native transport；`hooks=true`，`jsCallDetail=false`、`nativeDetail=false`、`objectSnapshots=false`。
- 时长 120 秒、总预算 1 GiB、事件预算 200000、单正文 16 MiB；结束原因为 duration，而非预算截断。
- `integrityConclusion=partial`，6 个 critical gap 均为 `response-body-unavailable`，另有 2 个非 critical `request-open-at-stop`。因此不能用“网络请求有 200”推出对应正文完整。
- 抓到 5 个 FO、带 `cf-chl-out` 的结束响应和 cert document POST 200；没有 submit hook，不代表没有 submit 调用。
- 该目录没有完成 wrapper 的 `runtime-hash`、`evidence-index`、`evidence-receipt` 与 `integrityReceipt` 全链。不得登记为 `browserFactPlane=v8trace-chromium`。

## 真正存在的设置与能力

锁核：`storage/web-runtimes/v8trace-chromium/20261003/V8Trace-Alcohol-case-prompts-20261003/`，Chromium `151.0.7922.72`；descriptor 宣告 `v8trace/detail/1`、`v8trace/objects/1`、`v8trace/browser/1`、`v8trace/redirect-body/1`。开采前仍须 `chromium-status` 验证 required-file hash，不能仅凭目录存在。

| 需求 | 实际开关/字段 | 能力边界 |
|---|---|---|
| 可见窗口 | wrapper `mode=interactive`；collector `headless=false` | 没有 `headed=true` 参数；要求 launch 中无 headless flag |
| DOM 创建/query receiver 与 args/return | `hooks=true` | `Document.createElement/NS`、Document/Element query、get/setAttribute 等 enter/return；receiver/result 为 realm-local WeakMap ID，字符串 tag/selector 可见 |
| tag/constructor | 无专用开关 | hook `valueRecord` 对对象只有 ref ID/callable，不读取 tagName/constructor；仅可由创建 tag 参数 + 同 realm 返回 ID + 后续 receiver ID证明部分来源 |
| attachShadow/submit 来源 | 现成 hooks 未覆盖 | 没有 `Element.attachShadow`、`HTMLFormElement.submit/requestSubmit`、Document body/head/root getter，也未安装 Node 插入/DOM tree 方法；不能据缺失事件判未调用 |
| JS/Native 实参返回与源码关联 | `jsCallDetail=true`、`nativeDetail=true`、`scripts=true`；可加 `correlations=true` | detail entry/argument/return/throw/resume/suspend；JSCall 为实际 Ignition activation segments，不是无损完整 JS 调用图 |
| 对象内容 | `objectSnapshots=true`，depth=2/nodes=64/properties=256 | own-storage 有界观察，不执行 getters/Proxy traps，不展开 prototypes/internal slots；不是 DOM tag、document tree 或持续全局 identity 查询 |
| async callback | JSCall detail 的 resume/suspend 与实际回调执行 | hooks 只看 setTimeout/queueMicrotask 注册调用，不包回调；correlations 明写 completeCausality=false，缺 async task ID 时仍未决 |
| HTTP 响应正文 | `http=true`；建议 `transport=native` | native 网络/renderer body stream；CDP 是 getResponseBody，可能失效；正文完整性需逐请求检验，不靠开启 flag 保证 |
| 重定向正文 | collector `redirectBodies=true` | 新锁核支持有界原生 drain，每跳最多 5 秒；不重放请求。它只处理 redirect body，不能保证修复所有非重定向 CDP missing body |
| iframe/eval | `scripts=true`；CDP `contexts=true` | CDP 支持 page/iframe/worker/shared_worker/service_worker，递归 autoAttach 并在新 document 安装 hook；native 以 process/isolate/context scope 与源码事件核查覆盖，contexts 通道会被 wrapper 抑制，不可假设每个 iframe 都采全 |

`traceLogOptions` 及 filtered `get/call/reflect/source` 不是本 Chromium capture schema 的设置：本轮定向检索 wrapper/runtime collector 未发现该 key。Patched Node 的 profile/tokens/query filters 不能拼到 Chromium `capture-start`；`--receiver/--prop/--args/--result` 是 Node query 过滤器，不是 Chromium 启动过滤器。Chromium scripts 通道是真源码；没有独立“成功 property get/reflect”全覆盖开关。

## 最低现成可执行组合

在 dispatcher 允许新 Chromium capture、迁移检查通过且 `chromium-status=ready` 后，wrapper 现成组合为：

`capture-start --mode interactive --preset env-hooks --transport native --duration-seconds 90`

具体等效设置：`headless=false`；http/scripts/hooks/console/exceptions=true；contexts 在 native 下 suppressed；opcode/jsCallDetail/nativeDetail/wasm/cpuProfile/nativeTimeline/rawCdp/objectSnapshots=false；maxBytes=1073741824，maxBodyBytes=16777216，maxEvents=200000（wrapper 默认）。提权父进程确有需要才 `--do-not-de-elevate`。

这是最低有用的 DOM create/query 身份链 + 完整响应对照，不是最低充分的 attachShadow 溯源。90 秒是上限，完成假设窗口立刻 capture-stop；无需等 duration 到点。不能把 gated 开关开到目标访问之后，以免丢创建起点。

## 需要扩展后才能组合的设置

runtime collector 的现成 scenario `env-protocol` 已组合 hooks + JSCall/Native detail + own-storage snapshots + HTTP/scripts + correlations + redirectBodies，transport=native、opcode/wasm/CPU/timeline/rawCDP=false，预算 1 GiB/1000000 events/16 MiB body，默认时长只有 10 秒，应覆盖为 90 秒。

但当前 `mcp/v8trace-mcp/src/chromium-launch.ts` 不转发 `correlations`、`redirectBodies`、object snapshot 及其深度参数；`capture-start` CLI 只接固定 7 个 wrapper presets，不接受 runtime scenario/custom channel flags。wrapper 的 `jscall-detail`、`native-detail`、`full-compare` preset 又都关闭 hooks，不能直接等同 `env-protocol`。因此不得给 wrapper 偷拼这些参数，也不得直接 collector 开采后默认登记 browser fact。

若选择 Chromium 为此问题的充分取证面，先做独立工具合同扩展切片并测试上述参数转发/manifest/hash/gates，再启动；仍需明确新增观察如何证实 DOM tag 与 attachShadow receiver，detail/snapshot 不自动完成该义务。当前默认 Firefox DOMTrace 更贴近这项缺口。

## 预期产物与验收

最低组合：`capture/events/env.jsonl`、`http.jsonl`、`script.jsonl`，源码/正文 blob 与 catalog、`launch.json`、`coverage.json`、`gaps.json`、`summary.json`、wrapper run/index/receipt。

有 detail/correlations 扩展后：`events/jscall.jsonl`、`native.jsonl`、`detail-summary.json`、`catalog/calls.jsonl`、`script-index.jsonl`、`hook-spans.jsonl`、`correlations.jsonl`、`correlation-summary.json`。只报告明确 identity join；同步包围和 URL/时间候选不提升为因果父链。

逐一核查 top-level challenge document、page-host FO、CF/iframe FO、最后两个 cf-chl-out 响应、业务 document response 的 requestId/realm/body pointer/hash/length/completeness；解码边界是外部响应证据，不做密文字节归因。还须覆盖动态 iframe/eval 对应 process/isolate/context/source，native scope-only 不自动当精确 iframe 归属。正文缺失、stream sequence gap、criticalGapCount>0、io/flush 失败均保持 partial。

完成后只在三 gates 通过、raw 非空且 integrityReceipt 完整时登记该独立 plane。浏览器成功、表单出现或 POST 200 不改变本地 `localReproduced/requestBoundaryAligned/serverAccepted`；同 lease 的业务 readback 仍独立验收。

## 已核对的源

- `skill/web-reverse/references/v8trace-chromium-capture.md`
- `mcp/v8trace-mcp/config/capture-presets-chromium.v1.json` 与 runtime lock
- `mcp/v8trace-mcp/src/chromium-launch.ts`、`chromium-capture.ts`、`cli.ts`
- 锁核的 `app/v8-trace/{hooks,detail,collector,native_collector,browser,correlations,cli}.js`、`scenario_presets.json`、`chromium/v8trace-opcode.json`
- `agent-notes/20261003-v8trace-headed.md` 与 `evidence/web/v8trace-chromium/headed-20261003/capture/launch.json`

遗留：未采集，未做 runtime hash 检查；wrapper 组合能力不足，主线 stale HEAD/合同迁移尚待主线程核验。
