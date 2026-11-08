# Node 补环境推进（2026-10-04）

## 本轮动作

- 对生产离线 iframe realm runner 增加了 constructor 观测字段 `constructorCalls`，记录 realm、构造器名、参数数量和参数类型/constructor/length；同时补齐了 `Event`、`MessageEvent`、`DOMException`、`FormData`、`Headers`、`Request`、`Response`、`EventSource`、`WebSocket` 的 native-like 构造器候选。
- 观测保持严格离线：没有网络、没有历史 FO body/cookie/token 回放，没有写 `PQak3`。

## 验证

`node runtime/run.js frame`：

- `frameEval=ok`、`chlOptKeys=37`
- `framePqOwn=false`、`framePqType=undefined`
- `throwName=TypeError`、`throwMessage=h[bb(...)] is not a constructor`
- `constructorCalls=[]`、`sendCount=0`、`boundary=boundary-unchanged`

## 结论

本轮新增 host constructor 候选没有被目标执行路径调用，也没有改变边界。当前错误是动态/混淆 receiver 的构造器调用，不等同于缺少某个已知 DOM constructor。继续盲补 constructor 不具备证据基础；下一刀必须捕获真实 receiver/property/descriptor/source-site，或取得同一 fresh session 的响应回调事实。

验收保持：`requestBoundaryAligned=false`、`localReproduced=false`、`serverAccepted=false`。
## 追加对照：浏览器 trace 约束

已有 Chromium frame canary 的 `construct.tsv` 在 TypeError 前只有 `Set/Map/WeakMap/WeakSet/Proxy/Uint8Array/URL/URLSearchParams` 等标准构造，未出现 `EventSource`、`WebSocket`、`Request`、`Response` 或 DOM 构造器。`get.tsv` 唯一相关 miss 是 `toJSON`，另有 `PQak3` 读取结果为 `undefined`。因此本轮补齐网络/事件 constructor 不是证据支持的修复，运行结果未改变。

当前最强事实：错误路径不是“缺少某个已知 Web API constructor”，而是本地独立 realm 与 browser frame 的动态上下文/响应生命周期仍不一致；继续补 constructor 应停止。

## 追加运行链事实

Chromium frame trace 的最后 10 个业务操作显示：

- `document` challenge UI 在 `classList.add` 后进入 `classList.remove`；
- trace 中 `classList.remove` 结果为 `undefined`，随后触发 `TypeError: IV[w6(...)][w6(...)] is not a function`；
- 这是浏览器对页面元素 `classList.remove` 的调用，不是 constructor 缺口。

本地 iframe runner 虽已具备 `classList.remove`，但错误仍是另一条 `h[bb(...)] is not a constructor`，说明当前本地脚本与该 Chromium canary 的执行分支尚未对齐，不能把 Chromium 最后异常直接当作 Node 当前异常的修复依据。下一步需要同一 source/同一 runtime 的操作序列，而不是继续加 API。

## 同源操作 trace 实验

- Node runner 现在记录 `frame.start` 与首个同步异常；运行结果确认 TypeError 是 inline script 同步执行阶段直接抛出，而不是 timer/response callback 后抛出：`operations=[frame.start, throw(TypeError)]`。
- 同一脚本仍为 238636 bytes，SHA-256 `05102bb5158cd0ba9a41329021f124cad8778a9a556db9a0e802b11c07115262`；没有进入 `classList` 操作、`send` 或 `postMessage`。
- 这解释了与 Chromium frame trace 的差异：Chromium canary 的 `classList.remove`/timer 异常属于更后阶段；Node 当前先在同步初始化分支失败。继续调 classList 已无效。

下一步应围绕同步初始化中的动态 constructor receiver 做 source-level trace（不补值），或切入真实同 session 响应生命周期；当前验收仍 false。

## source-aligned mirror 对照

Chromium frame canary 的实际入口不是纯 iframe realm：它先在同一 Node global 上执行 `windowMirror` bridge，使用 `Object.setPrototypeOf(global, bridge)`、`eval`、`Proxy` 与 `Object.defineProperty` 安装 `runProgram/BGgf6/SSvM5/HxNX2/xdiN1`，随后把 frame inline script 放进同一 eval realm。其 `construct.tsv` 显示最早同步路径包括 `Proxy`、`WeakMap`、`Map`、`Uint8Array`、`URL`、`URLSearchParams`，并在 frame 入口前完成多次 `Object.setPrototypeOf`。

当前生产 runner 使用两个隔离 vm.Context，且明确删除 Node leak，行为模型与该 canary 不同；因此不能把 canary 的后续 `classList` 事实直接用于当前 runner。已验证在隔离 runner 中增加 `HTMLScriptElement.prototype` 仍不改变同步 TypeError。下一刀应建立一个 source-aligned mirror 模式作为独立诊断分支，精确复现 bridge/eval/realm 关系，再比较首个异常；不改变默认验收 runner，不回放网络响应。
