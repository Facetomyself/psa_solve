# PSA CF 5s 盾补环境求解器

Cloudflare managed challenge（5s 盾）实验求解器：vanilla Node 补环境产出挑战求解载荷，
经浏览器 TLS 指纹（curl_cffi Firefox impersonate）提交获取 cf_clearance。
`serverAccepted` 实验记录于 2026-08-15（真实页面 200/159KB 回读）；项目总状态 `partial`
（生产 Sticky lease 接入、合同收敛与 Mac canary 未完成）。

## 核心结论（实验证据）

| 结论 | 证据 |
|------|------|
| **TLS 指纹是 CF 最重风控变量** | 同 IP 同时间：Firefox 指纹直通 200；Node/curl 原生 TLS 触发挑战且求解后验证仍被拒 |
| **求解链跨材料版本稳定** | 6+ 个挑战实例（不同 id/ray）零改动通过 |
| **cf_clearance 绑定 TLS 指纹 + 出口 IP + 会话** | 非浏览器 TLS 带 clearance 全被拒；换 sticky 出口失效 |
| **403（challenge）求解有效，429（限速）求解短暂恢复** | 429 恢复后约 7 请求复发——频率控制是本质 |
| **clearance 有服务端生效延迟 ~5s** | bypass 后立即请求 403，等待后通过 |

## 架构

```
workspace/psa_solve/
├── runtime/                    # vanilla Node 补环境（无第三方依赖）
│   ├── code.js                 # 主入口：模块组装 + Proxy 垫底 + 可选诊断
│   ├── run.js                  # 求解入口（vm 执行 + 载荷捕获 + 完成检测）
│   └── lib/                    # 模块（按宿主面拆分）
│       ├── config.js           #   运行参数与目标 URL 派生
│       ├── host-globals.js     #   window 别名/屏幕/navigator/performance/DOM 类
│       ├── host-dom.js         #   元素 stub/document/cookie jar（增量语义）/storage
│       ├── host-async.js       #   Worker（完整事件接口）/观察者/定时器/Blob
│       ├── patches.js          #   缺口补丁 P1-P2（UpvLO0 XOR 解密/ZHfDS6 eval 别名）
│       └── transport.js        #   XHR shim（真实网络+cookie/响应头浏览器语义+观测）
├── scripts/
│   ├── demo.py                 # 一键 demo：材料→求解→提交→验证（serverAccepted）
│   ├── demo2.py                # 持续采集+风控自愈验证（Firefox 指纹高频→求解→恢复）
│   ├── fetch_material.py       # 挑战材料抓取（403 页+orchestrate+__cf_bm）
│   ├── test_clearance_collection.py  # clearance 持续采集验证（sticky 出口）
│   └── burn_ip_reputation.py   # 快速请求破坏 IP 信誉（触发挑战实验）
├── diagnostics/                # RuyiDOM 诊断执行层（缺口定位工具，证据链归属）
├── challenge-material/<epoch>/ # 材料归档（manifest.json+页面+orchestrate）
├── analysis-progress.md        # 完整证据链与已知边界
└── findings.json               # 结构化发现（含 serverAccepted 证据）
```

## 使用

### demo.py — 单次求解验证（无参数）

```powershell
python scripts\demo.py                # 材料过期自动拉新 → 求解 → 提交 → 验证
python scripts\demo.py --fresh        # 强制拉新
python scripts\demo.py --cliproxy-rand  # 经 Cliproxy 机房 IP 级联（需 SSH 隧道）
python scripts\demo.py --url <URL>    # 复用其他目标（CF managed challenge 形态）
```

### demo2.py — 持续采集 + 风控自愈

```powershell
python scripts\demo2.py --count 200 --gap 0.15
# 不断请求（Firefox 指纹，session 复用真高频）→ 403/429 即调用求解代码 → 恢复采集
```

### Cliproxy 机房 IP 链路（可选）

```
本机 → ssh -N -D 127.0.0.1:18081 oracle-newapi-primary（SOCKS 隧道）
     → Cliproxy us.arxlabs.io:3010（Rand/sticky 账号）
     → psacard.com
```
Windows Clash TUN 对 gateway 3010 明文 CONNECT 系统性挂起——必须走 SSH 隧道。

## 补丁清单（evidence 见 analysis-progress.md / findings.json）

| # | 缺口 | 修复 | 模块 |
|---|------|------|------|
| P1 | window.UpvLO0 缺失 | XOR 流解密器（jcLw7 同构，字节码重建证据） | lib/patches.js |
| P2 | window.ZHfDS6 缺失 | 原生 eval 别名（toString 对比证据） | lib/patches.js |
| P3 | setTimeout 变长参数 | arguments 全量透传 | lib/host-async.js |
| P4 | document.cookie 覆盖语义 | cookie jar 增量合并（Set-Cookie 应用） | lib/host-dom.js |
| P5 | XHR 响应头/字段缺失 | getResponseHeader/responseURL/on* 事件等完整接口 | lib/transport.js |
| P6 | VM Proxy 探测 null target | Proxy 垫底（外部宿主面） | code.js |

## 风控判定纪律（本项目遵守）

1. 无感通过是多维得分——环境指纹 + IP 质量 + 行为特征共同决定，不把「IP 好/坏」当单一归因
2. 403（challenge）与 429（限速）是不同机制：求解解决前者；后者需频率控制/出口轮换
3. 浏览器 TLS 指纹是硬约束——采集与求解提交必须同指纹（Firefox impersonate）
4. 材料时效 5-10 分钟——过期 CF 拒收（400 + cf-chl-out）

## 已知边界（如实）

- 生产接入（Sticky lease 合同、Mac canary、parity/risk receipt）未完成——不得标 completed
- Node 求解链缺 eb 提交分支（fo 两轮 + clearance 已足够通过验证，多次实证）
- 行为指纹字段（性能基准/时间戳）为 Node 真实值而非浏览器值——收紧期可能成为下一变量
- 新版本材料 RuyiDOM 诊断路径有提交后 hk 崩溃（Node 路径无此问题）
- 字符串表 ZZ 偏移非全局统一——静态解码需按函数族确认
