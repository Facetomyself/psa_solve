# 补环境完成规划（web-reverse 方法论）

Case: `psa-cf-5s-shield-20260815`

当前阻塞：`_cf_chl_opt.yQYB9` 应为求解回调函数，RuyiDOM 引擎里为 object
（ID 状态机 case '5' 调用 `yQYB9?.call(IG)` 失败，orchestrate 源码 180073）。

按 SKILL.md 纪律：每轮一个明确缺口、双条件依据（browser fact 证明真实使用
+ local fact 证明缺失）、environmentPatchGate 只允许外部宿主面、禁止
VM/opcode/bytecode 内部 patch、禁止字节集 diff。RuyiDOM 引擎执行层优先
（第 0 步已采用）。

## Phase 1：yQYB9 赋值历史捕获（1-2 轮）

**方法**：wrapper 在 403 页 init 之前对 `window._cf_chl_opt` 定义赋值观测
（defineProperty setter 记录每次整体赋值与字段级赋值）。

- 403 页 init 设置 18 字段（首次赋值）
- orchestrate line 1 补充到 33 字段（二次字段赋值）
- **观测 yQYB9 的赋值次数与类型**：若只有一次 object 赋值 → 函数注册段
  从未执行；若两次 → 注册段执行但被覆盖/回退。

**判定**：`window._cf_chl_opt` 是外部宿主面（window 全局）——setter 观测
属外部宿主面插桩，合规。

**证据**：赋值时间线（次数/类型/调用栈近似位置）写入 analysis-progress.md。

## Phase 2：yQYB9 函数注册段定位（2-3 轮）

**方法**：静态定位 orchestrate 内给 `_cf_chl_opt` 赋值的全部代码段。

- 已知 T 表 919 键 = "_cf_chl_opt"（插桩解码已确认）
- 搜 `T[rf(...)][rf(...)]=function` 模式（180073 之前的字段补充/注册段）
- 与 403 页 init 的 18 字段对照：33 字段中哪些是 orchestrate 补充的

**判定**：注册段是否在环境条件分支内。若分支条件依赖宿主探测（如
performance/画布/音频某项返回值）→ 该条件是"外部宿主面可补"缺口；
若依赖引擎不可复现状态 → 记录穷尽性证据（SKILL.md 判据），转路线。

## Phase 3：单变量补丁 + 复跑（1-2 轮）

按 SKILL.md：一次只补一个缺口，补后重跑 RuyiDOM 观察推进。

- 每轮：改 wrapper → ruyidom_run → 记录 case '5' 前后状态变化
- native toString 保护（如补的是函数形态）
- 不补 VM/opcode/WASM 内部（runProgram 的字节码不动）

## Phase 4：提交链闭合（2-3 轮）

case '5' 通过后：

1. 提交请求出现（XHR 或 navigation——bXxEG="navigation" 提示是导航提交）
2. 导航提交在 RuyiDOM 里：allowNetwork=true 时真实导航（location 赋值
   或 form submit）→ CF 服务器验证
3. 观测 cf_clearance 下发 → 引擎内闭环

## Phase 5：交付验收

- 引擎成功 ≠ serverAccepted：vanilla test.py 用引擎生成结果真实请求验证
- 落地方式按 `docs/web-reverse-landing.md` 矩阵声明（纯算/补环境/V8 RPC）
- 更新 landing/method.json + parity 记录

## 决策门（Phase 2 之后）

若 Phase 2 证明 yQYB9 注册依赖引擎不可复现的宿主状态（穷尽性证据）→
转 triage 路线 B（浏览器求解器注入 cf_clearance）。判定标准：
具体缺口项 + 对应接口 + 为什么外部宿主面不可表达。

## 执行顺序与预计轮次

| Phase | 轮次 | 工具 |
|-------|------|------|
| 1 赋值历史 | 1-2 | RuyiDOM wrapper setter |
| 2 注册段定位 | 2-3 | 静态搜索 + 插桩解码 |
| 3 单变量补丁 | 1-2 | RuyiDOM 复跑 |
| 4 提交闭合 | 2-3 | allowNetwork + 观测 |
| 5 验收 | 1 | vanilla test.py |

预计 7-11 轮可收敛或触发决策门。
