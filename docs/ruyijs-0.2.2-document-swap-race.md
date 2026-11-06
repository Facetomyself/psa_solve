# ruyijs 0.2.2 缺陷报告：document 切换竞态使 advance() 抛 createElement receiver TypeError

**状态**：已定位机理（未提交上游修复）
**发现环境**：D:\reverse_ENV\workspace\psa_solve，2026-11-06
**影响版本**：0.2.2+inner.20261101191032（js.exe sha256 `5fb68b22…`）
**复现现场**：`workspace/psa_solve/diagnostics/ruyijs-fresh-navigate-20261103/run2_022.py`（首次 advance 即抛）
**严重度**：中——不破坏导航语义，但把一批本应在旧 document 上完成的任务变成未捕获 TypeError；对调用方表现为 advance() 随机抛错，需要容错绕过

## 现象

`Context.navigate(url)` 后 `advance(ms)` 在挑战页 document 切换点抛：

```
JSError: TypeError: 'createElement' called on an object that does not implement interface Document.
```

- 只在**真实网络导航**触发 document 替换时出现（`load_page` 不触发）
- 错误从 advance() 冒出，但 Context 存活：继续 checkpoint/drain_timers/advance，链路能走完（psa_solve 实测 FO×5 → form submit → cert 200）
- 同一 Context 后续 navigate 正常

## 根因链（读 src 确认，行号对 0.2.2 快照）

1. **旧 document 任务在导航提交后仍会跑**。挑战 JS 的定时器/XHR 回调注册在旧 document 上；`TopLevel::Advance`（`src/runtime/top_level.cpp:17-45`）创建新 `BrowsingContext` 并 `retire_(retireContext_, previous)`（`:39`）退役旧 document，但已入队的任务对象仍持有旧 document 的 JS 对象引用。

2. **退役只摘端口，不销毁 State**。`RetireTopLevelDocument`（`src/runtime/top_level_assembly.cpp:51-76`）对旧 context 只做 `SetScriptPort(nullptr)` / `RetireImageLoads()` / `RetireMessages()` 等**端口摘除**；旧 `document_model::Realm` 对象留在 `later_` 数组里活到 Context 关闭（`top_level.cpp:14-16` 析构才 pop）。旧 wrapper 对象是持久根（`state.h:76-79`："a connected node's wrapper is a strong root"），JS 对象还活着。

3. **但 wrapper 已不在"当前 document"语义内**。任务回调里 `document.createElement(...)` 的 receiver 是旧 document 的 JS 对象。`State::Find(JSObject*)`（`realm.cpp:131-137`）在本 State 的 wrapper 链里**仍能找到**它（没 dead、地址没回收）——问题不在这。

4. **真正的抛点**：receiver 检查走的是**调用方当前活跃 State**。`document.cpp:133` `Receiver(state, args, &kind)` 的 `state` 来自 `FunctionState(args)`＝方法安装时绑定的 native reserved slot（`conversion.cpp:60-62`）。当旧任务经过 **realm 迁移/跨界调用**（新 document 的全局执行旧回调，或跨 realm wrapper 转发）时，`args.thisv()` 的 unwrap 结果在新 State 的 wrapper 链里找不到（`conversion.cpp:67` `state.Find` 返回 null），落到 `:78-81` 的 brand 错误分支，抛出 Firefox 措辞的 TypeError：

   ```
   "'createElement' called on an object that does not implement interface Document."
   ```

   消息由 `WebKit::BrandText`（`runtime/web_kit.cpp:39-49`）拼装——这段措辞本身是为 Cloudflare per-member 指纹刻意复刻的（`web_kit.h:51-54` 注释明说），所以**这个 TypeError 也可能被挑战侧当成正常浏览器行为采集**，实际影响集中在引擎任务层而非页面观测。

5. **为什么错误从 advance() 冒出**：任务在 advance 驱动的事件循环里同步执行，未捕获异常沿任务边界上抛为 `JSError`。0.1.3（公开版）同流程不抛——它的 receiver 检查路径更宽松（未做 per-method brand 文案），旧 document 任务静默失败。

## 触发条件（最小模型）

```
navigate(A) → 页面 JS 注册 setTimeout/XHR 回调持有旧 document 引用
           → advance 驱动：导航提交（新 BrowsingContext 生效）
           → 旧 document 的回调在新 document 活跃窗口内执行 document.createElement
           → receiver 解析失败 → TypeError → advance() 抛 JSError
```

## 修复方向（供上游参考，按侵入度排序）

**A. 任务级隔离（最小改动，推荐）**：任务调度层（`execution_scheduling`）在导航提交后把"活跃 document ≠ 任务所属 document"的任务标记为 retired，调度时**静默丢弃**（对齐浏览器行为：旧 document 的 pending 任务在导航后不再执行）。落点：`TopLevel::Advance` 的 `retire_` 回调处给旧 Scheduling 队列发 drain/cancel 信号。`RetireTopLevelDocument` 已经是现成钩子，补一条 `owners.scheduling.Retire(global)` 对旧 document 任务的作用域即覆盖（当前只对 hash-change 全局做 Retire，`:55`）。

**B. receiver 宽容化（不推荐）**：`Receiver()`（`conversion.cpp:66-83`）找不到 wrapper 时降级返回 dead-view。会破坏 Cloudflare 指纹措辞的刻意设计（`web_kit.h:51-54`），且让本应失效的旧对象复活成僵尸——语义更差。

**C. 调用方绕过（当前 psa_solve 的做法，无需改引擎）**：把首个 `advance()` 包在 try/except 里，后续泵循环单独容错每个 advance。已验证可走完全链。上游修复前这是稳定 workaround。

## 复现要点（给上游写测试用）

1. 服务端返回带 `setTimeout(fn, 0)` 的页面，`fn` 内 `document.createElement('div')` 并保存到外部引用保证不被 GC
2. 页面 JS 500ms 后 `location.reload()`（触发同方式导航）
3. `ctx.navigate(url)` → `ctx.advance(2000)` → 观察 TypeError
4. 断言：修复后 advance 不抛、`fn` 或被静默丢弃（方案 A）或正常执行（若调度层判定任务属新 document）

## 附：与 psa_solve 案例的交叉证据

- 错误只在首个 `advance(10000)` 抛出一次（`boundary-022-longpump.json` 的 advanceErrors 数组长度 1），第二次 navigate 后的 advance 不再抛——与"旧 document 任务队列一次性排空"的模型一致
- 12 个 net 事件里 FO 轮全部 200、最终 cert readback 200——TypeError 只炸了任务批，不影响已发出的网络请求
