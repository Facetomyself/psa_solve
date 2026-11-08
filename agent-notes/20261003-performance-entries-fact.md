# Performance entries 提取事实

日期：2026-10-03  
Case：`psa-cf-5s-shield-20260815`  
目标：为 Node 首个 trace 缺口 `performance.getEntries` 提取已有 Firefox/RuyiTrace 行为合同；只读既有证据，没有新开网络或浏览器。

## 证据

- Firefox 主 run：`evidence/web/ruyitrace/rt_20260929103550_341b734038/`；receipt `integrity=pass`，raw root `980d1002ee040e0e513593a412600ad6ef2515b070a7a0b623659764b8b688c2`。
- Challenge orchestrate DOMTrace：`raw/domtrace/trace_process_46184.ndjson`，该进程中的 challenge frame URL 指向当轮 orchestrate；对应记录由 RuyiTrace 索引关联至 run。
- 同 run Node first-gap trace：`evidence/web/v8trace/v8-20261003100221-c54ooe/v8trace/index.jsonl`，`param-complete`，33291 records。
- 现有桥接参考：`diagnostics/ruyidom_bridge.js` 与 `diagnostics/causal-observer-transport-fixed/ruyidom_bridge.causal-observer.transport-fixed.js`。

## Firefox/RuyiTrace 事实

| 事实 | 证据 | 可确认内容 |
|---|---|---|
| Orchestrate 调用 `Performance.getEntries()` | process 46184，seq 101 | 无参数；返回类型为 Array；调用栈属于 PSA challenge orchestrate |
| 遍历返回项 | seq 104–119、122–136 | 先检查 `entryType`，随后读取 ResourceTiming 项的 `responseStart`、`requestStart`、`responseEnd`、`duration`、`transferSize`、`encodedBodySize`、`name` |
| 建立异步观察 | seq 140 | `PerformanceObserver.observe(...)` 被调用，参数为一个对象；receipt 未保留 options 的字段值 |
| Observer 回调使用 entry list | seq 634、2184、2282、83077、83188、102932 | `PerformanceObserverEntryList.getEntries()` 返回 Array；PSA challenge 代码读取其中 entry 的 `entryType` 和资源时间/大小字段 |
| 同轮 Turnstile 资源枚举 | seq 2211 | `performance.getEntriesByType("resource")` 返回 Array；随后的代码读取 entry `name` |
| 旁路应用采集 | process 31908 / 52748 | 其他页面脚本调用 `getEntriesByType("navigation"/"paint")`、`getEntriesByName("snaptr")`；这是 API 旁证，不等于 challenge 用法 |

## 脱敏限制

DOMTrace getter 事件对原始 timing 返回值记作 `null`，PerformanceObserver options 也只保留 `[Object Object]`。Descriptor 分区没有为该 challenge frame 留下可匹配的 `Performance.prototype.getEntries` descriptor 记录。因而本轮可以确认 API 类型、参数数目、返回 Array、字段读取顺序和异步 observer 使用；不能确认 entry 数量、URL/name 原值、`entryType` 的具体值分布、各 timing 数值、字节数、observer options、prototype descriptor 或 native `toString` 外观。

## 对 Node 的最小合同

1. `performance.getEntries()` 无参数，返回普通 Array；每个实际 resource timing 项至少应支持 `entryType`、`name`、`startTime`、`duration`、`requestStart`、`responseStart`、`responseEnd`、`transferSize`、`encodedBodySize`。
2. `PerformanceObserver` 是下游独立缺口：构造器接收 callback，实例有 `observe(options)`；回调给 `PerformanceObserverEntryList`，其 `getEntries()` 也返回 Array。
3. 页面读取这些条目来做行为/时序计算。不能用历史 3488/3792 长度、旧 URL、旧 cookie 或固定 token 合成 entries。
4. `getEntries()` 空 Array canary 只适合确认 execution boundary 是否越过；当前挑战文档已实际加载资源，因此空 Array 不是最终 parity 实现。

## 下一步

用独立 Node runner 副本加 `performance.getEntries()`，返回当前 runner 的空资源快照并计数；以 `param-complete` no-network 重跑，只看 IF 是否从“缺方法”推进到下一个真实缺口。预期结果只作为 canary 事实记录，不改基线 runner、不更新 environmentPatchGate 为 ready。
