# PSA Cloudflare 5s 盾无感求解 — 逆向分析报告

## 基本信息

| 项目 | 值 |
|------|-----|
| 目标 | PSA（www.psacard.com）Cloudflare managed challenge（5s 盾）无感求解 |
| 目标形态 | 403 challenge 页 + orchestrate 混淆 JS（229KB）+ 内嵌 VM（runProgram） |
| 分析时间 | 2026-08-15 |
| 分析深度 | L3（运行时定位） |
| 状态 | `partial`（缺口链定位完成，求解未闭合） |

## 目标概述

PSA 站点对无 cf_clearance 的客户端强制 Cloudflare managed challenge（"Just a
moment..." 5s 盾），采集器（curl_cffi）无 JS 求解能力导致 91-92% 请求被
mitigation。本 case 目标：在真实 Gecko 引擎（RuyiDOM）中执行 challenge 求解
JS（orchestrate），自动生成挑战提交并获取 cf_clearance，不触发交互式
Turnstile。

## 关键发现

### 发现 1: 挑战链完整形态（Reqable 真实浏览器抓包）

- **位置**: 浏览器访问 cert 页全请求序列
- **描述**: 当前 PSA 无感挑战 = Turnstile non-interactive 自动通过。提交链：
  403 挑战页 → orchestrate 加载 → 两次 `fo` POST（psacard.com +
  challenges.cloudflare.com）→ POST /cert 带求解结果 → 200 真实页。
- **证据**: 提交 URL 模板 `/cdn-cgi/challenge-platform/h/g/fo/{id}:{ts}:{hash}/{ray}/{token}`；`__cf_bm` 两段刷新；`cf_clearance` 求解后下发
- **置信度**: `high`

### 发现 2: 三环境缺口阶梯

- **位置**: Node（v8trace）/ iv8 / RuyiDOM 三环境执行 orchestrate 对照
- **描述**: 同一缺口链在三环境的不同深度断裂：
  - Node：`document.createElementNS` 等 DOM 缺口面过大（逐桩补齐不现实）
  - iv8：实测 `document.createElementNS`=undefined，修桩后静默退出
  - RuyiDOM：走最远（createElementNS ×3 + createElement ×41），崩于
    `_cf_chl_opt.yQYB9?.call(IG)`
- **证据**: iv8 domPanel 实测；RuyiDOM wrapper hook 计数；v8trace throw_context
- **置信度**: `high`

### 发现 3: IG.call 精确定位（插桩解码）

- **位置**: orchestrate 源码 180073（ID 状态机）case '5'
- **描述**: `T['_cf_chl_opt']['yQYB9']?.['call'](IG)`——yQYB9 应为求解回调
  函数，引擎里为 object（注册步骤被更早的环境分支跳过）
- **证据**: 用混淆器自身解码函数 rv 插桩输出 `_cf_chl_opt,yQYB9`；引擎
  实测 `typeof yQYB9 === "object"`；CDP 实测真实浏览器挑战后
  `_cf_chl_opt` 整体清除（求解期临时状态）
- **置信度**: `high`

### 发现 4: CF 规则升级时间线

- **位置**: 8 月 9 日（旧 trace）×5 vs 8 月 15 日（新 trace）
- **描述**: 8 月 9 日主文档全部直接 200、零 cf-mitigated 标记；8 月 15 日
  强制 managed challenge。同出口浏览器能过（1.1s 求解）、curl 被硬拦——
  判定维度是客户端 JS 求解能力，不是出口 IP
- **证据**: rt_20260809* 5 个 run 的 http_packet 全 ABSENT vs 新 trace 的
  cf-mitigated 响应
- **置信度**: `high`

## 架构概览

```
403 challenge 页（_cf_chl_opt 配置：cH/cN/cRay/cType=managed/cTplV=5）
  └─ init script（内联，nonce）
       └─ 动态加载 orchestrate（challenge-platform/h/g/orchestrate/chl_page/v1?ray=...）
            ├─ 字段初始化（_cf_chl_opt 18→33 字段）
            ├─ Pv：SVG 指纹元素创建（createElementNS + setAttribute cx/cy/r=15 + path d）
            ├─ IF：performance.getEntries 遍历 + PerformanceObserver 注册
            ├─ ID：entry 处理状态机（switch 字节码）
            │     case '5'：_cf_chl_opt.yQYB9.call(entry)
            └─ runProgram：内嵌 VM 执行器（加密字节码求解核心）
```

## 核心逻辑分析

### 求解链各阶段（RuyiDOM 插桩实测）

| 阶段 | 引擎状态 | 证据 |
|------|---------|------|
| 字段初始化 | ✅ 33 字段 | cfChlOptKeys |
| Pv SVG 指纹 | ✅ ×3 createElementNS | lastTag="path" |
| IF 性能采样 | ✅ getEntries/PerformanceObserver/ID 均 function | 插桩解码 |
| ID case '5' | ❌ yQYB9 为 object 非函数 | yqType="object" |
| 提交 | ❌ 未到达 | xhr=[] |

### 缺口根因假设

yQYB9 的函数注册（orchestrate 内部 `_cf_chl_opt[键]=函数` 的赋值段）在引擎
环境被更早的分支条件跳过。注册点未定位（下一步工作）。

## 环境与工具

- 浏览器证据：RuyiTrace 2.5.5 / Firefox 155（rt_20260815060651_eb196ed770，
  index/receipt integrity pass）
- 引擎执行：RuyiDOM gecko-xpcshell（Firefox 135 base，hash 锁）
- 本地诊断：v8trace patched Node 20.19.0（challenge-fast，1415 records）
- 快速验证：iv8 Community Edition 0.1.4（离线 V8 + DOM 仿真）
- 抓包对照：Reqable（用户浏览器真实提交链）
- CDP：js-reverse-mcp（调试 Chrome 9222，断点窗口不足未用）

## 结论

- `localReproduced` / `transportAdmission` / `serverAccepted`: 均未达
- 落地方式候选：浏览器求解器注入 cf_clearance（工程可行路径）
- 剩余工作：定位 yQYB9 函数注册点（orchestrate 内部，同插桩法可继续）
