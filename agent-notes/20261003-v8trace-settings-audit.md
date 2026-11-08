# V8Trace 设置与实际产出审计

日期：2026-10-03  
范围：只读 `mcp/v8trace-mcp` 的 CLI/profile 配置、`web-reverse` 的事实驱动 reference，以及 `psa_solve` 的三轮 Node evidence；没有开网络、没有改 runner 或合同。

## 结论先行

当前三轮 trace 的主要缺口首先是 **profile 没开**，其次是 **目标 runner 没触达/工具不会为普通 JS stub 自动生成 host fact**。工具本身的 `envcall`、`callback`、`request-call` 记录是能产出的；现有产物只证明这些通道在已识别调用上工作。`get/has/reflect/source/raw` 没有开启，所以不能用现有 run 判断成功 property read、descriptor 或 source 事实。`response` 也不是当前 Patched Node request trace 的能力：`request` 只记请求方法边界和摘要，不会凭空产生真实网络响应。

## 配置来源

- `tools/v8trace_run.py` SHA-256：`fdac011deb7adbc987a63f05efa77bb5aad5ddbc51dffe8b03ad92c084e87109`。
- `src/cli.ts` SHA-256：`b1a24706b9d6e57cbc487f478bc44aaf045c52dbe24a8af5a41df5bcea619463`。
- `src/constants.ts` SHA-256：`47fe67ca000cc109ca47eeaffe5282bc6388939eda400dbaa27613a5394ccd44`。
- 事实 reference `skill/web-reverse/references/v8trace-fact-driven-patching.md` SHA-256：`875c73820cf28703cb7df8c40ec283ffe7125c58a53cbb514866b2da90bde498`。

`dist/cli.js run` 只接受固定 `--profile`，没有把 Python runner 的自定义 `--trace`、`--source`、`--raw-trace`、`--context-get` 等开关直接暴露成 CLI 参数。因此审计和下一轮优先选正确 profile，不能在 `dist/cli.js` 上拼一个未声明的 trace 参数。

## Profiles 的实际开关

| profile | 实际 trace tokens | 自动打开的附加项 | 本案适用性 |
|---|---|---|---|
| `param-env` | `miss,construct,worker,envcall,write,throw,tostring,leak` | `throw_detail=true`、`throw_context=true`、window 50；`raw/source/get/has/reflect/callback/request` 均未开 | 环境读取候选，但看不到成功 property get 或 source |
| `callback-chain` | `miss,construct,worker,envcall,callback,write,throw,tostring,leak` | throw context 80；`get/source/raw/request` 未开 | 异步入口确认 |
| `challenge-fast` | `miss,construct,worker,envcall,request,write,throw,tostring,leak` | throw context 60、`request_evidence=true`；`callback/get/source/raw` 未开 | 请求方法边界 |
| `param-chain` | `miss,construct,worker,envcall,write,throw,tostring,leak,context_get` | `context_get=true`、throw context 80 | 只补 throw context 内成功 property read |
| `param-complete` / `env-complete` | `miss,get,has,reflect,construct,worker,envcall,write,throw,tostring,leak,source,noise` | `source=true`、`raw_trace=true`、throw context 80；仍没有 `request` 或 `callback` | 当前 IF 未知 receiver/property 的最小下一轮 |
| `callback-deep` | `miss,construct,worker,envcall,callback-deep,write,throw,tostring,leak` | throw context 80；没有 get/source/request | 只有 callback 参数链还不够时才用 |

所有这些 profile 默认 `no_analyze=true`，所以 run.json 的 `analysis_status=skipped` 是配置结果；`trace_index` 和 `round_summary` 仍然生成且 complete。它不是索引器失效。`effective_parser=fast`、`partial_trace_recovered=false`，三轮也没有 `max-events`/`max-per-site` 截断。

## 三轮现有 run 的证据

| run | profile / hash | 实际 kind 产出 | 关键状态 |
|---|---|---|---|
| `v8-20261003093112-o9509m` | `param-env`；`run.json` SHA `b26f6f1dec415c195a9ff8a5cf311d8bfc5651e612006d678c207cf1487efb4d` | `call=14, miss=39, throw=1, throw_context=50`；无 get/has/reflect/callback/request kind 文件 | `request_evidence_enabled=false`；0 request / worker / callback；TypeError raw index 1386 |
| `v8-20261003093211-o37wfl` | `callback-chain`；`run.json` SHA `43d1f7516a7cbaa455161bf1fac4cc9c3f3b9f3d60230d7be2f994eaa3dcd28b` | `call=14, callback=7, miss=39, throw=1, throw_context=80`；`callback.tsv` 存在 | timer `callback#2` register+enter；没有 callback exit，0 request / worker；TypeError raw index 1423 |
| `v8-20261003021537-lhw7em` | `challenge-fast`；`run.json` SHA `9003cb44f263389daf1ace6d75b1ab0015393d7fa1d73e9766a78db169954fcf` | `call=14, miss=39, throw=1, throw_context=60`；没有 callback kind 文件 | `request_evidence_enabled=true`，但 request summary 仍 `call_rows=0/send_count=0/reached_request_boundary=false`；request token只看到 Node `net.open`，没有 target request |

三轮 `analysis/trace_index/kinds/` 实际没有 `get.tsv`、`has.tsv`、`reflect.tsv`、`value.tsv`、`return.tsv`、`request.tsv` 或 `worker.tsv`。这对前三轮是“没有打开或没有发生”的合并结果；`callback-chain` 的 `callback.tsv` 证明 callback 通道本身能产出。`call.tsv` 则明确存在 args/return 摘要，例如 `EnvCallProperty/Return now`、timer、`Object.keys`，以及 Node `net.open`；因此 `envcall` 并非工具不产出，只是只覆盖它识别到的调用。

## 各类信号的能力边界

### Property get / call / args / return

- 成功 property read：前三轮未开 `get`，现有 `miss` 只表示缺失/undefined；不能从它反推成功读过什么。`param-chain` 的 `context_get` 只在 throw context 内记录成功 bytecode read，范围更窄。
- `has` / `reflect`：前三轮未开，不能审计 `in`、ownKeys、descriptor、prototype 等外观。
- method call：`envcall` 开启，但它是 V8Trace 识别出的 DOM/BOM/Object/native 方法边界，不是所有 JS function call。普通 JS stub 的 `document.createElement`、XHR/fetch wrapper 没有自动变成 envcall。
- args / return：对已识别 `EnvCallProperty` 有浅层 args，对 `EnvCallReturn` 有结果摘要；`call.tsv` 可见 `now`、timer、`Object.keys`、Node `net.open`。没有通用函数的完整 call graph 或所有 return 值。

### Source / stack

三轮都 `source=false`、`raw_trace=false`。`throw_detail` 只保留异常文本，`throw_context` 是抛错前的最近 V8 facts 窗口，不是 JavaScript 完整调用栈；当前 TypeError 的 stderr Node stack 在 evidence 外部文本里可见，但 index 中 throw 行的 `script/site` 为空。`param-complete` 才会打开 `source=true` 和 `raw_trace=true`，可提供更完整 source/raw facts；它仍不等于自动得到 target 的完整 stack。

### Async callback

`param-env` 和 `challenge-fast` 没有 callback token，所以 0 callback 是配置预期。`callback-chain` 产生了 7 条 callback facts：`callback#2` 的 timer callback register+enter，以及 `CallbackHelperThrow` 在 `IF` 中的 execution site；3 个 callback 只注册未进入。这证明 callback 通道工作，但当前 trace 仍没有 IF 内的 host method boundary。`callback-deep` 只在需要更深 callback 链时使用，不能替代 property/source tokens。

### Worker

三个 profile 都包含 `worker`，但 runner 没有真实 Worker/message，所以没有 worker facts。这里是“通道开了、目标没触达”，不是工具没实现。

### Request 与 response

只有 `challenge-fast` / `request-call` profile 打开 `request`；`request_evidence=true` 只让 summarizer 生成 request candidates/summary。它记录 XHR/fetch 方法边界（open、setRequestHeader、send、fetch 等）及 body/header 摘要，不能为 patched Node 创建真实网络 response、cookie 或 HTTP packet。三轮 runner 的 XHR/fetch 是本地 stub，现有 request summary 均无 target request；旧 challenge run 的 `RequestCallProperty open` 实际来自 Node `net`，不是业务 FO。要看 response 必须有真实 browser/RuyiTrace HTTP evidence 或显式 response fixture，不能靠 profile flag 补出来。

## 最小正确下一轮

当前 IF 未知 receiver/property 的最小正确 profile 是 `param-complete`：它一次打开 `get,has,reflect,source,raw_trace`，并保留 `envcall,throw,throw_context=80`。CLI 形式：

```powershell
& "D:\reverse_ENV\tools\node\node.exe" "D:\reverse_ENV\mcp\v8trace-mcp\dist\cli.js" run --project "D:\reverse_ENV\workspace\psa_solve" --case "psa-cf-5s-shield-20260815" --script "D:\reverse_ENV\workspace\psa_solve\v8trace_orchestrate_runner.js" --profile param-complete --allow-failure --cwd "D:\reverse_ENV\workspace\psa_solve"
```

这轮仍然是本地诊断，不能打开 response；只用于判断 IF 前后的 property/descriptor/source facts。异步入口已有 `callback-chain` 证据，不需要重复跑。若目标是请求边界，另用 `challenge-fast`，不要把 `request` 当 response capture。

## 证据路径

- `D:\reverse_ENV\mcp\v8trace-mcp\tools\v8trace_run.py`
- `D:\reverse_ENV\mcp\v8trace-mcp\src\cli.ts`
- `D:\reverse_ENV\skill\web-reverse\references\v8trace-fact-driven-patching.md`
- `D:\reverse_ENV\workspace\psa_solve\evidence\web\v8trace\v8-20261003093112-o9509m\run.json`
- `D:\reverse_ENV\workspace\psa_solve\evidence\web\v8trace\v8-20261003093112-o9509m\analysis\trace_index\kinds\call.tsv`
- `D:\reverse_ENV\workspace\psa_solve\evidence\web\v8trace\v8-20261003093211-o37wfl\analysis\trace_index\kinds\callback.tsv`
- `D:\reverse_ENV\workspace\psa_solve\evidence\web\v8trace\v8-20261003021537-lhw7em\analysis\request_summary.json`

最终判断：已有三轮不是“V8Trace 全面没产出”，而是 profile 有意保持窄且 runner 没触达大部分宿主边界。下一轮用 `param-complete` 才能审计成功 property read、reflect 和 source/raw；真实 response 仍不属于这套本地 Node trace 的可用产物。

## param-complete 实测补充

实际执行了上面的 `param-complete` 命令：run `v8-20261003100221-c54ooe`，runtime verified，trace index complete，33291 records，target exit 1。

这次 `get` 已打开并捕获到决定性链：

```text
_cf_chl_opt → yQYB9 → performance → getEntries → undefined → TypeError
```

throw context 的最后事实是 `performance.getEntries` 读到 `undefined`（seq 33151），随后抛出 `T[rv(...)][rv(...)] is not a function`。因此“trace 没开对”确实是前一轮的直接问题；开对后已经选出第一候选 external-host surface：`performance.getEntries`。这仍需要 browser/RuyiDOM 事实确认其返回对象、entry shape、时序和 descriptor，不能只塞一个空数组宣布修复。

证据：`evidence/web/v8trace/v8-20261003100221-c54ooe/analysis/round_summary.json`、`evidence/web/v8trace/v8-20261003100221-c54ooe/v8trace/index.jsonl`。

另做了同一 runner 的 `--trace all --raw-trace --source --throw-context-size 200` no-network 对照，run `v8-20261003102000-alltrace`：`call=1253`、`callback=7`、`get=30267`、`has=1287`、`throw_context=200`，trace index complete；仍然 `send_count=0`、`reached_request_boundary=false`，同一 TypeError。结论是开关打开后 trace 能力确实增加，工具没有“全局失效”；但它只能看见 runner 已执行的 JS/Node 边界，不能凭配置生成缺失的浏览器 response 或 host callback。
