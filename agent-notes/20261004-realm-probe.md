# 2026-10-04 Dynamic Eval Realm Probe

## Scope

独立诊断副本：`runtime/realm-probe-canary.js`。仅包装现有 mirror runner 的大体量 `eval`，不回放 FO body，不写 `serverAccepted`，不修改默认 runner。

## Evidence

- `frameScriptLength=238636`
- `frameSha256=05102bb5158cd0ba9a41329021f124cad8778a9a556db9a0e802b11c07115262`
- `frameEval=ok`，`chlOptKeys=37`
- 首个异步错误仍为 `x[bf(...)][bf(...)] is not a function`
- 栈：`Timeout.It`，动态 `eval` source offset `214416`
- callback 顺序：`ij(0ms) -> onload(0ms) -> Li(0ms) -> It(0ms)`，均无参数
- gate 已进入：`iR -> iq`
- `foRequests=0`，`deliveryEvents=[]`，`PQak3=undefined`

## Conclusion

当前动态 eval 的 lexical `x` 不会通过 outer `window/global` proxy 暴露；外层 property/function wrapper 不能证明真实 receiver。该 canary 复现了 source-aligned async boundary，但尚未取得 closure-local property 名称。下一步需要在 eval realm 内做 source-level instrumentation，或取得同一 fresh browser fact 的 receiver/property 证据；不得继续盲补 global API。

## Restrictions

`replayedFoBody=false`; `wroteServerAccepted=false`。

## Follow-up

realm probe 已定位真实首错动态 eval offset（约 214416/214519，随 instrumentation prelude 改变），但 closure-local proxy 仍未捕获 property read。当前说明 eval realm 内的 `x` 是 lexical binding，不是 global property；需要 source-level rewrite 在目标表达式前插入 receiver/prop 记录，不能依赖 Proxy。

## Source context probe

realm probe now records source context around regex-matched `x[...]` sites, but Proxy still cannot observe lexical access. The decisive next artifact is the source context at the first `It` expression (~214519); instrumentation must rewrite that expression itself, preserving semantics and not touching opaque responses.

## Artifact status

source context is currently retained only inside child instrumentation; the parent canary intentionally does not copy it into runner records. The run still proves the same lexical closure boundary but does not yet produce a usable expression context artifact. No production runner changes were made.

## Source context extracted

Child artifact now contains exact source windows around 214k for both large evals. The orchestrate window is crypto/VM code; iframe window is Turnstile queue/response code. The first dynamic x-site must be selected by matching the actual error source offset, not a fixed absolute offset after prepending instrumentation. Artifact is now usable for precise source-level rewrite.

## Artifact export fixed

realm-probe 现在把 child 里的 `realmEval` source windows 通过 `probeLines` 直接导出到 `realm-probe-result.json`：orchestrate 238847 与 iframe 238636 两段窗口均可读。下一步可基于 source window 选择准确的 `x[...]` 表达式做 rewrite，不再依赖固定 offset 或外层 Proxy。

## Throwing x-call recorded

`function It` 里唯一会抛 `x[bf(...)][bf(...)] is not a function` 的调用是 `x[bf(CW.IZ)][bf(CW.IM)](b)`。诊断包装只改写这一处：先记下属性名和接收者，再执行原来的调用。

连续两次 `node runtime/realm-probe-canary.js` 记到同一条：

- property key: `attachShadow`
- receiver: `HTMLScriptElement`
- expression: `x[bf(CW.IZ)][bf(CW.IM)](b)`

边界未变：iframe `238636` / `05102bb5158cd0ba9a41329021f124cad8778a9a556db9a0e802b11c07115262`，`frameEval=ok`，`_cf_chl_opt` 37 个键，`foRequests=0`，`PQak3=undefined`，`serverAccepted=false`，没有回放 FO body。首错仍在 `Timeout.It`。这不是补环境完成，也没有把 `attachShadow` 补成宿主 API。

## Verdict

`no-browser-fact`。iframe `Timeout.It` 里的 `x[bf(CW.IZ)][bf(CW.IM)](b)` 在本地记到接收者 `HTMLScriptElement`、属性 `attachShadow`。这只是 Node 诊断读数，不是这条调用的浏览器事实。

下面两处都不算 iframe `function It` 的 browser fact：

- `ruyidom_cf_shield_v1.js` 的 `hostPanel` 只有 `typeof document.createElement('div').attachShadow`。
- Turnstile API 源码是 `var Gt = document.createElement("div"); var Xt = Gt.attachShadow({ mode: "closed" })`，接收者是 div，不是 `HTMLScriptElement`。
- 当前 run `rt_20260929103550_341b734038` 的 DOMTrace `raw/domtrace/trace_process_48444.ndjson` 第 98 行是 `type=call`、`interface=Element`、`member=attachShadow`。栈只有 `It`，列 233112，文件是该 run 的 turnstile iframe。`thisObj.class` 是 `HTMLBodyElement`，返回类是 `ShadowRoot`。更早三次 iframe 调用（`eE` / `cf` / `Fs`）同样是 `HTMLBodyElement`，不是 `HTMLScriptElement`。

这条 DOMTrace 证明 iframe `It` 在浏览器里对 `HTMLBodyElement` 调用了 `attachShadow`。它不是 `HTMLScriptElement` 的 receipt。`environmentPatchGate` 保持 `not-ready`，`patchCoverageIds` 仍为空。`runtime/mirror-canary.js` 不新增 `attachShadow`。纯node补环境未完成。

2026-10-05 新 DOMTrace `rt_20261005054520_0e24cdbc08` 只开 `dom-observe`：`MOZ_DOM_TRACE=1`、`MOZ_DOM_HTTP_PACKET_TRACE=1`、`MOZ_DOM_TRACE_ASYNC=1`、`fingerprintMode=baseline`。未开 `env-probe`、JSCall、opcode、`hostProbe`。`trace_process_52288.ndjson` 第 98 行是单帧 `Q` 列 172017，`Element.attachShadow`，`thisObj.class=HTMLBodyElement`，`returnObj.class=ShadowRoot`。`argsObj` 只有浅层 `Object`，没有 `mode`。同 run 另有 `xe`/`HTMLDivElement` 与 `o/</<`/`HTMLElement`。没有 `HTMLScriptElement` 的 call。writer `dropped_*=0`，`io_errors=0`，receipt gate pass。这仍不是 `HTMLScriptElement` receipt。

## Completion predicate

纯node补环境完成 requires all of the following for this external-host miss, and none of them exist for iframe `Timeout.It` `attachShadow` on `HTMLScriptElement`:

- browser-fact receipt: absent for `HTMLScriptElement` (`no-browser-fact`; the `typeof` probe, Turnstile API `Gt.attachShadow` on a div, and the DOMTrace `It` call on `HTMLBodyElement` do not count)
- gate ready: absent (`environmentPatchGate` is `not-ready`, not ready)
- cert-document request boundary: absent (no cert document POST from this call)
- independent readback: absent (no readback, so `serverAccepted` stays false)

纯node补环境未完成。

接受关闭的 `refuse_host_enumeration` 门：纯node补环境未完成。该门保持 `turnGate=blocked` 与 `no-new-host-surface`。2026-10-05 已按允许采完一份 `dom-observe` DOMTrace；iframe 调用是 `Q` on `HTMLBodyElement` returning `ShadowRoot`，对 `HTMLScriptElement` 仍是 `no-browser-fact`。不把 `serverAccepted` 写成 true。
