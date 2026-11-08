# Shadow options 静态恢复 / 2026-10-20

## 结论

**该 canonical source 的同一调用明确为 BODY.attachShadow({mode: 'closed'})。** 这不是运行目标 decoder 得到的值，而是以同源已观测 API/receiver 为锚，对纯字面量表进行索引同余约束恢复。没有执行目标、decoder、VM、浏览器、网络或 Node canary；没有修改 runner/gate/facts/goal/next。

本拍 dispatcher 仍 refuse_host_enumeration / blocked，无运行句柄。机器回执：`diagnostics/shadow-options-static-20261020/options-receipt.json`；可复跑静态脚本 `recover_options.py`。

## 1. 输入与精确数据流

- 输入 packet SHA-256 `761ace226909224c788e98aa7a3533b0a7f067a8aee594f1bb5495f700db925f`，精确路径在回执；该输入是上轮锁定的原始历史 frame packet 快照。
- 原始首段 inline SHA-256 `05102bb5158cd0ba9a41329021f124cad8778a9a556db9a0e802b11c07115262`，238636 chars。脚本 assert 全 ASCII，因此本报告零基偏移等于 UTF-16 code units，不混插装后偏移或 HTML 文档前缀。
- It 起点：210156；b 初始化/赋值链起点：213646；唯一 attachShadow call expression 起点：213698。
- 精确相关表达式：`b={},b[bf(CW.ID)]=bf(CW.Ip),h[bf(CW.IV)][bf(CW.Iy)]=x[bf(CW.IZ)][bf(CW.IM)](b)`。
- It 内 literal CW 提供 ID=2043、Ip=1760、IZ=605、IM=1366；bf=aH，外层 aH=a。
- a 的静态函数体是减 261、从 I() 的 cached literal array 取一个单元并返回；本轮只读取并断言函数文本形状，不调用它。

## 2. 没有执行 decoder 的恢复方法

I 函数持有一个无反斜线转义、无模板插值的字面量，范围 `[190190,204928)`，随后按分号 split 得 1979 个单元，并缓存同一数组。本轮 Python 只分割这段静态文本。

旋转以 r 表示。decoder 参数 n 对应未旋转字面量表的单元 `(n - 261 + r) mod 1979`。

### 同源事实锚定，不猜旋转次数

| 锚 | decoder n | 未旋转单元位置 | 得到 r |
|---|---:|---:|---:|
| 同一调用的实际方法 attachShadow | 1366 | 1328（唯一） | 223 |
| 同一调用实际 body getter | 605 | 567（唯一） | 223 |

两项独立约束交集仅有 223。它们来自 canonical browser 的 BODY getter/attachShadow 与已对齐唯一 call-site，而不是从期望 mode 反推旋转。另用 x 的 global-document 字段 n=2153 验证单元136为 document，结果一致。

**证明性质**：fact-assisted static proof；没有运行 bootstrap 的 parseInt/shift 循环，也没有把该循环翻译成 Python 执行。依据是同 source/call-site 已观测 key 与同一 cached string table 的索引约束。结论仅适用于这个精确 source，不推广到轮换脚本。

### options 最终恢复

| 角色 | 表达式 | n | 未旋转单元 | 字面量源码偏移 | 结果 |
|---|---|---:|---:|---:|---|
| key | bf(CW.ID) | 2043 | 26 | 190379 | mode |
| value | bf(CW.Ip) | 1760 | 1722 | 203062 | closed |

b={} 后只有这一项配置，随后直接把同一 b 传入已配对调用；中间相关 computed lookup 使用同一个只读取值 decoder。恢复的局部 options 为 `{mode:'closed'}`；未声称浏览器所有 optional 默认值、后续新版本配置或整个业务分支都已恢复。

## 3. mode 不是必须硬编码的实现阻塞

attachShadow(options) 应在运行时从传入对象读取 options.mode，验证 open/closed 并返回对应 root。正确实现不需要预先知道历史脚本会传哪一个值，更不应写死 closed 或复制历史 options。

因此，上一轮“mode 未知”是一项**证据完整性缺口**，不是“必须拿到 mode 才能写通用正确行为”的必要条件。独立模型支持 open/closed 只证明这两条单元分支存在，不能反过来证明浏览器具体传参；本轮才补上该具体调用的 closed 证据。

closed 的已知消费合同仍是：调用者持有返回 root，向其中 append STYLE/DIV/IFRAME、在 root 子树按 #id 查已创建节点；closed 不妨碍调用者直接使用返回 root，也不要求 host.shadowRoot 暴露它。上轮 3 append / 6 query 数据流回执继续有效。

## 4. 只核对与当前精准缺口有关的合法记录/验证路径

- `skill/web-env-patcher/references/existence.md`：browser 已触达 + local 缺失即可构成该项 existence-miss；BODY.attachShadow 的双条件已成立，不需要再采 constructor/descriptor 或静态猜更多宿主字段。
- `skill/web-reverse/scripts/web_case.py:1351,1400` 的 dualCondition 是 allow-listed 可记录事实；正式入口 `fact record --key dualCondition --value true --evidence <精确证据路径> --sha256 <真实hash> --expected-revision <实时revision>`，参数合同在 `:3991-4002`。本 slice 明确不改 facts，因此仅核对，不调用该写入口。不要创建新的 ShadowOptions fact key。
- 记录 true 只是存证，不意味着解锁。`:2701-2703` 的 hygiene 提前返回仍在 `:3079` 之后的 env dualCondition 检查之前；stop-search 的 `:2516-2524` 拒绝不会被新 options 或 dualCondition 自动越过。
- 当前精准缺口不是相邻字段猜测，但当前 gate/dispatcher 没有为它提供合法的 challenge 行为修正/复跑 action；同源新 options 是代码结构事实，不是新的外部请求边界差异，不可记为 boundary-moved、不可把 hygiene 改 ok。
- 既有 reviewed diagnostics 固定旧 RuyiDOM runner，不是可任意传入 Node attachShadow 实现的通用入口。没有新执行授权就不能拿该入口自报 profile 启动。

## 5. 收口：本轮之后是否还有同类静态动作值得做

本轮已消掉当前局部 options 的未定依赖。再对 mode 做同类静态任务没有价值；receiver→参数→root append/query/identity 合同已足够明确，下一步需要的是**受准的单一 BODY.attachShadow 行为集成与固定输入复跑**，而不是另一轮 source/参数审计。

当前规则下尚可做正式 dualCondition 记账/证据归档，但它不会推动求解。除这些记账动作外，没有已获 dispatcher 放行的目标执行/补丁对照动作；本 slice 不能继续动态推进，明确停在这里，不发明下一轮相似静态任务。

尚未达到 Node fresh session 自然请求、目标提交、parity、同 lease 独立 readback 验收；没有写“已通过”或“不可模拟”。RuyiDOM 五跳后排障仍是另一条独立因果链，不能拿本轮 Node 参数恢复冒充解决。

## 正式 dualCondition 存证回执

已先读取 fact record --help、allow-listed facts/normalize/证据哈希校验逻辑及 workflow gate schema，然后通过正式 CLI 绑定上述 6 份不可变机器证据及逐份真实 SHA-256，CAS expected-revision=4，记录 dualCondition=true。未手编 facts。

执行结果：{"recordExitCode": 0, "beforeRevision": 4, "afterRevision": 5, "dualCondition": true, "hygieneUnchanged": true, "workflowHashUnchanged": true, "businessAxesUnchanged": true, "nextExitCode": 0, "action": "refuse_host_enumeration", "turnGate": "blocked"}。原始 stdout/stderr 和核验回执见 `diagnostics/shadow-options-static-20261020/dual-condition-record*`，后续 next 输出见 `dual-condition-next.stdout.json`。证据仍精确限于已定位的同源 BODY.attachShadow 存在性缺口，不代表所有环境项均已满足双条件。

该存证没有解除卫生暂停，没有放行动作；未执行目标。下一步不再追加同类静态审计或重复 record，当前真实阻塞仍是 dispatcher 对该已定位 surface 的行为验证未提供匹配可执行动作。
