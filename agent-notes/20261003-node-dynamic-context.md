# PQak3 / WHtx4 动态上下文分析（2026-10-03）

## 结论

`PQak3` 不是当前证据支持的外部 host API，也不是可以从 Turnstile resource 直接导出的固定函数名。它是同一 orchestrate 位置的未声明 free identifier：fresh source 使用 `PQak3`，旧 229KB source 使用 `WHtx4`；二者都没有 `var/let/const/function/class` 或 `window/globalThis` 定义。这个名字变化首先证明 source/runtime/material mismatch，剩余候选是动态 `eval`/`runProgram` 输出或跨 realm/global mirror；现有静态和脱敏 trace 还不能在这两者之间定案。

## 输入与哈希

- RuyiDOM fresh orchestrate：`challenge-material/rt_20260928061614_ee71af43b2/chl-page-orchestrate.js`，238694 bytes，SHA-256 `aa2b09a484f556d195376d66d478e974c656de976e50a00f09912cbbf01a0fe3`。
- Node 旧 source：`challenge-material/chl-page-orchestrate-fresh.js`，历史 canary 记录约 229681 bytes、SHA 前缀 `cdc46f...`；当前磁盘文本读取为 229683 bytes、SHA-256 `cdc46f960d47559055f58684c52e6eb65bfd2047102003932a5aa70d05a25a43`。报告沿用 canary 的 source identity，不把两个字节数混成同一输入。
- 当前 browser 对照里的 Turnstile API：`diagnostics/live/turnstile-api.js`，86732 bytes，SHA-256 `76763bb46224400a11af989831d62d06629aba6f67d50cac96afae4a590adf59`。
- RuyiDOM bridge：`diagnostics/ruyidom_bridge.js` SHA-256 `ce5bfbeecc44a70fa1d6e435084b1cf1e229ec1ea6e67dce7cbf8ac6b8f25e70`；transport-fixed 副本 SHA-256 `52503fd09a64b307cc6fdae7a8417a096cd2b4df9ff2c47ce8e72e00f8d6f5d9`。

## 静态 occurrence 事实

| 输入 | `PQak3` / `WHtx4` | 位置与形状 | 定义检查 |
|---|---|---|---|
| fresh RuyiDOM source | `PQak3` 1 次、`WHtx4` 0 次 | offset 123215 左右；形状为 `...eO = J[decodedCall](PQak3, eO)`，位于字节/摘要处理段 | 未发现声明、赋值、`window.*` 或 `globalThis.*` 定义 |
| 旧 Node source | `WHtx4` 1 次、`PQak3` 0 次 | 同类字节处理段，形状为 `...Ie = J[decodedCall](WHtx4, Ie)` | 未发现声明、赋值或 Window 定义 |
| `diagnostics/live/orchestrate.js` / headed copy | `PQak3` 各 1 次 | 同一类调用位置 | 未发现声明 |

Fresh source 还有 4 处 `runProgram` 标记和 1 处间接 `(0,eval)`；没有可见的 `function PQak3` / `new Function` 静态声明。`xdiN1` 在 fresh source 主要作为字符串表内容出现，不是可直接当作 Window API 的声明。

## 动态资源 / RuyiDOM 事实

- Node canary `v8-20261003130747-4pwon9` 执行同版本 Turnstile API 时，先因 `HTMLScriptElement` / `document.currentScript.src` 缺失失败；补 resource identity 后达到 `turnstileEval=ok`。
- `v8-20261003131028-kt767g`、`v8-20261003131931-dbzjwx` 继续补当前 script/resource 语义；后者再提供 `performance.getEntriesByType() -> []` 后，Performance API 缺口消失，但 fresh orchestrate 仍停在 `PQak3 is not defined`，`send_count=0`、FO boundary=0。
- 因此 `PQak3` 不是“Turnstile API 文件没有执行”的直接结果，也不是单独的 `performance.getEntriesByType` 缺口。资源执行已经跨过，名字仍未生成。
- RuyiDOM bridge 历史事实是：orchestrate resource → Turnstile API resource → Window/global mirror（`xdiN1` 一类注册，sloppy IIFE 的非 Window global 与 Window 对象同步）→ 3 个 `/fo/` 请求形状；旧日志明确没有定义 `window.KP`。这说明 Node 当前缺的是资源 loader、独立 realm/currentScript 和跨 realm assignment/identity 合同，而非一个可硬编码的 PQak3 函数。

## 分流判断

- **外部 host API：低可能。** `PQak3` 不对应浏览器对象/方法命名，也未被 RuyiTrace 以 host receiver 形式观察；静态 occurrence 位于内部 byte/crypto-like 处理调用。
- **Turnstile resource export：未证实且当前不支持。** Turnstile API canary 执行成功后仍没有 `PQak3` 定义；不能从资源文本或历史 token 推导。
- **`runProgram` 动态生成：候选。** fresh source 有多处 `runProgram` 和间接 eval，`PQak3` 调用位于其相邻内部处理路径；但没有 define/return trace，不能声称已确认。
- **跨 realm / source-context mismatch：高置信。** 旧 source→`WHtx4`、fresh source→`PQak3`，且 Node 直接 eval 单一 global；RuyiDOM 则有资源执行和 Window/global mirror。当前最可靠结论是“动态上下文缺失”，不是“host getter 缺失”。

## 下一刀：Node 证据采集（不硬编码）

1. 锁定同一 fresh HTML、orchestrate、Turnstile resource 的 SHA/epoch；Node 不再混用旧 229KB source。
2. 仅在 Node 诊断副本里记录动态执行边界：每次 `eval` / Function-constructor 的 source 长度与 hash、定义 realm、返回值类别和新增 global property 名（只记录 `PQak3`/`xdiN1` 的 name/hash，不落源码/密文）；同时记录 `runProgram` call/return class 与前后 global diff。
3. 给每个 realm 记录 `Window/global/self` identity、`currentScript.src`、script load order，以及 `xdiN1` 类 mirror 的 assignment direction / descriptor / `toString`；不要直接写 `window.PQak3 = ...`。
4. 以“出现 `PQak3` 的 define 事件且随后 call 能继续”为局部 discriminator；若没有 define 事件，转查 runProgram 返回/闭包作用域，不切换到相邻 host getter。
5. 证据形成后再决定一个 external-host surface；在此之前保持 `requestBoundary=0`、`serverAccepted=false`，不把 canary `targetExitCode=0` 当成功。

## 限制与证据路径

现有 Node run `v8-20261003121849-1ykah1` 的 `ReferenceError: PQak3 is not defined` 只证明当前 stub/realm 在该 free identifier 处停住；没有 FO、response、cookie 或 form boundary。`PQak3` 的实际生成函数、参数、闭包作用域和跨 realm producer 尚未被现有 browser fact 公开。不得从 `runProgram` 标记、Turnstile API 资源或 source occurrence 直接反推其实现。

- source / AST：`challenge-material/rt_20260928061614_ee71af43b2/chl-page-orchestrate.js`、`diagnostics/live/orchestrate.js`、`agent-notes/deobf-ast/output.js`
- Node canary：`agent-notes/20261003-node-performance-rerun.md`、`evidence/web/v8trace/v8-20261003121849-1ykah1/`、`v8-20261003130747-4pwon9/`、`v8-20261003131028-kt767g/`、`v8-20261003131931-dbzjwx/`
- Turnstile resource gate：`diagnostics/live/turnstile-api.meta.json`、`turnstile-api.gate.json`
- RuyiDOM/resource/realm：`agent-notes/20260928-ruyidom-bridge.md`
- 当前 Node 诊断限制：`agent-notes/20261003-node-env-gap.md`

## 新增：Turnstile iframe realm（2026-10-03）

- `turnstile-api.js` 仅是 API 壳；RuyiTrace `000010_GET_200...` iframe HTML 的 inline script 为 238636 bytes，并包含 `PQak3`、`xdiN1`、`runProgram`。
- Node 独立 frame canary `v8-20261003151936-i5rosl` / `v8-20261003152132-h2taqe` / `v8-20261003152520-xgv5ln` 加载该 inline script 后 `frameEval=ok`、`_cf_chl_opt` 21→37，但 `framePqType=undefined`、`framePqOwn=false`。
- frame 真实读取 `PQak3` 后先后暴露 `parent.postMessage`、`innerText/querySelector` 等宿主面；这些补齐只推动了执行，不产生 `PQak3` define。最后仍在 DOM/状态分支 TypeError，未到 FO boundary。
- `runProgram` 动态 source 已取证：`function(KO,Ig){return Ig=Dk,new KH(KO)[Ig(F3.K)](0,53,[])}`；`xdiN1` 是队列写入函数，`BGgf6/SSvM5/HxNX2` 是 identity/trusted-types helper。所有 define 的 function source 均不含 `PQak3`。
- 判定更新：剩余缺口是 iframe 独立 realm + DOM/worker/message + FO response/callback 生命周期；不能把 `PQak3` 伪造为普通 Window API，也不能把历史 opaque FO body 回放到 Node。

## 静态辅助：PQak3 的上游函数与最小观测点

对 fresh source 做纯文本/结构定位（未执行目标）：

- `eY=function(K,S8,t6,J,I,eQ,eH,eB,eO,er,eV,eZ)` 定义约在 offset `121558`；`PQak3` 调用约在 offset `123215`，形状是 `eO=J[decodedCall](PQak3,eO)`。因此当前最窄的上游函数是 `eY`，不是 `runProgram` 直接调用点。
- `eY` 在内部把 `eO` 处理成至少 16 个索引项（后续读取 `eO[0]..eO[15]`），再把生成的数组以 `join("")` 类路径收口；可推断 PQak3 返回值需要“可索引、至少 16 项、项可参与位运算”的形状，不能推断其算法或原始 byte。
- 两个静态 caller 已定位：较早状态机 `case 8` 走 `eY(ex)`（约 offset `14554`）；较晚 response/telemetry callback 走 `eY(J)`（约 offset `204759`）。Node canary 应记录 caller site、入参脱敏 shape（constructor/class、own-key count、长度类）和 `eY` 返回 `typeof/class/length`。
- fresh source 的 `runProgram` occurrence 为 4 个：可执行调用约在 offsets `139136`、`188726`、`204328`；另一个 occurrence 位于字符串表，不应当作 call site。每个 call 只记录 payload length/hash、return class/typeof、是否写入新 global/closure、是否产生 callable return。
- offset `204328` 的静态分支对 `eN=runProgram(...)` 做 `typeof eN === "function"` 检查并在通过时调用 `eN(J,F)`；这证明某个 VM 程序结果**可能是 callable**，但不证明 `PQak3` 或间接 eval 返回 function。
- 唯一间接 eval 在 offset `52233`：`eH=(0,eval)(Dk(F4.eV))`，结果随后放入 VM/class `KH` 的状态表槽。其 return `typeof/class/realm/source-hash` 未被静态文件证明，Node 应捕获 `source length/hash → return type/class → target slot`，不能默认 function/string/undefined。
- computed `Function[...]` 取值约在 offset `52387`，并有 `new(Function[...])(...)` 动态构造路径约在 offset `85768`；另有 obfuscated constructor path 约 offset `204121`。Node 只记录 constructor site、arg count、source hash、returned constructor/class 和 realm，不把它们直接命名成 PQak3 producer。

### 最小 Node canary 字段

`sourceSite`（上述 offset/稳定 hash）、`realmId`、`currentScript/srcClass`、`evalOrFunction` source length/hash、`receiverClass/prototypeClass`、`argsShape`、`returnType/constructor/length`、`indexed0..15 type-only`、`newGlobalNames`（只允许 PQak3/xdiN1 name）、`toStringHash`、throw name。判别条件是出现真实 `PQak3` define 或闭包 return 后，`eY` 可完成并继续；没有 define 时优先查 `runProgram` return/闭包作用域，不切换到邻近 host API。
