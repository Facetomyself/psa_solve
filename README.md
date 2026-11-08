# PSA CF 5s 盾求解器

目标：`https://www.psacard.com`（Cloudflare managed challenge，"Just a moment" 5s 盾）的求解与采集。

**主线已生产化（ruyijs 引擎求解）**：`python scripts\demo6.py --solver ruyijs`——fresh-navigate 全链约 12s 到 cert readback，导出 `cf_clearance/__cf_bm` 给 curl_cffi（Firefox impersonate）同 IP+UA 复用，业务页 200。**clearance 跨引擎转移成立**（IP + UA 对齐即可）。
Node 补环境线已定性为 capture-only 事实采集（不收敛根因见下）；静态 payload 组装链研究进行中。当前状态与分析总览：`docs/status-20261107.md`。

## 当前状态（2026-11-07）

| 线 | 状态 | 一句话 |
|---|---|---|
| ruyijs 求解（主线） | **生产可用** | `runtime/solve_ruyijs.py`（独立 venv `D:\reverse_ENV\temp\ruyijs-test-env`，inner 0.2.2）；每解 ~12s；clearance 可跨引擎转移 |
| Node 补环境求解 | 已定性，不作为完成门 | 同字节同插桩下死于 FO r1 后第二层 VM 的键控解码（调用方 f8 无界自旋），非"慢"；维持 RuyiTrace/对照事实采集定位 |
| 静态 payload 组装 | **核心缺口已闭合** | v0 已隔离为离线加密器：纯 Node 零网络复现 FO r1 body（3,148B/7,042B 字节级相等）；剩 MZ 字段模板化（R2） |

## 核心结论（实验证据）

| 结论 | 证据 |
|------|------|
| **TLS 指纹是 CF 最重风控变量** | 同 IP 同时间：Firefox 指纹直通 200；Node/curl 原生 TLS 触发挑战且求解后验证仍被拒 |
| **cf_clearance 绑定 TLS 指纹 + 出口 IP + UA** | 非浏览器 TLS 带 clearance 全被拒；换 sticky 出口失效；ruyijs → curl_cffi(firefox) 复用多次实证 |
| **challenge 变体每会话随机化** | orchestrate 624,426/646,373/621,550B 轮换；handler/表长/种子/失败点漂移——跨会话序列比对无效，对拍必须消变体（同材料） |
| **atob 解码语义两侧等价** | 消变体后前 825 调用逐字节相同、0 输出差（ruyijs vs Node） |
| **Node 不收敛根因 = 键控状态错误的重试** | 同字节 FO trace：ruyijs 同循环 161 轮完成，Node 12.09M 次 = f8 第 4 次进入后无界自旋（yz 恒空、NaN 早退不触发） |
| **FO r1 body 不是 LZ 压缩** | 912 种解包变体全败、熵 7.9；实为 v0 内部加密 + 3B→4 符号自定义 base64 |
| **clearance 有服务端生效延迟 ~5s** | bypass 后立即请求 403，等待后通过 |

## 架构

```
workspace/psa_solve/
├── runtime/
│   ├── solve_ruyijs.py          # 主线：ruyijs 子进程隔离求解（生产入口；--counters-rewrite 模板改写）
│   ├── template_probe.py        # v0 入口定位 + MZ 计数器改写探针生成（生产版，OV2 收编）
│   ├── run.js                   # Node 桥：vm 执行 + 载荷捕获（capture-only；CF_OP_TRACE/CF_HOT_SNAPSHOT/CF_LOOPGUARD 插桩）
│   ├── code.js                  # Node 桥主入口：模块组装 + Proxy 垫底
│   └── lib/                     #   host-globals/host-dom/host-async/patches/transport
├── scripts/
│   ├── demo6.py                 # 当前演示/生产入口（--solver ruyijs 默认）
│   ├── demo.py / demo2.py       # 早期 Node 求解 demo / 风控自愈验证（历史）
│   └── fetch_material.py 等     # 材料抓取与实验脚本
├── diagnostics/                 # 诊断产物（gitignore 域，本地保留）
│   ├── atob-diff-20261107/      #   atob 对拍 / 同字节 FO trace / id15 语义 / f8 观测 / 静态 payload 验证
│   ├── ruyijs-fresh-navigate-*/ #   ruyijs 全链录制与 FO body
│   └── bridge-diag-*/           #   Node 桥在线对照
├── docs/
│   ├── status-20261107.md       # 状态与分析总览（当前权威）
│   ├── ruyijs-0.2.2-document-swap-race.md
│   └── web/                     # web-reverse 流程文档（index.md 为状态索引）
├── 补环境进展清单.md             # 时间线（最新进展条目，最上方）
├── analysis-progress.md         # 历史证据链（2026-09~11 单变量实验记录）
├── triage.md / report.md / findings.json   # case 流程文件
└── archive/                     # 已归档的过时文档
```

## 使用

### demo6.py — 生产求解（ruyijs，默认）

```powershell
python scripts\demo6.py                     # ruyijs 求解 → 导出 clearance → curl_cffi 验证
python scripts\demo6.py --solver ruyijs     # 显式指定
python scripts\demo6.py --counters-rewrite  # v0 入口 MZ 计数器模板改写（OV2 已验证链）
```

`--counters-rewrite`：求解前预抓材料 → `runtime/template_probe.py` 实时定位 v0 入口并
生成改写探针（4 计时值按模板 A=20/B=C=800/D=1500 内联改写；服务端已证不校验）→
load_page+put_resource 混合跑。定位失败或链不收敛自动降级原生 navigate 完整重跑
（summary `mode` 字段区分 `templated` / `templated-fallback` / `native`）。模板可用
env `PSA_COUNTERS_TEMPLATE=<json 路径>` 覆盖。

要求：ruyijs 独立 venv（`D:\reverse_ENV\temp\ruyijs-test-env`，不装 repo `.venv`）。

### Node 桥（capture-only，诊断用）

```powershell
# 材料回放 + 插桩（见 diagnostics/atob-diff-20261107/ 各脚本）
# CF_OP_TRACE=24,15 / CF_HOT_SNAPSHOT=1 / CF_LOOPGUARD
```

### Cliproxy 机房 IP 链路（可选）

```
本机 → ssh -N -D 127.0.0.1:18081 oracle-newapi-primary（SOCKS 隧道）
     → Cliproxy us.arxlabs.io:3010（Rand/sticky 账号）
     → psacard.com
```

Windows Clash TUN 对 gateway 3010 明文 CONNECT 系统性挂起——必须走 SSH 隧道。

## 补丁清单（Node 桥历史证据，evidence 见 analysis-progress.md / findings.json）

| # | 缺口 | 修复 | 模块 |
|---|------|------|------|
| P1 | window.UpvLO0 缺失 | XOR 流解密器（jcLw7 同构，字节码重建证据） | lib/patches.js |
| P2 | window.ZHfDS6 缺失 | 原生 eval 别名（toString 对比证据） | lib/patches.js |
| P3 | setTimeout 变长参数 | arguments 全量透传 | lib/host-async.js |
| P4 | document.cookie 覆盖语义 | cookie jar 增量合并（Set-Cookie 应用） | lib/host-dom.js |
| P5 | XHR 响应头/字段缺失 | getResponseHeader/responseURL/on* 事件等完整接口 | lib/transport.js |
| P6 | VM Proxy 探测 null target | Proxy 垫底（外部宿主面） | code.js |
| P7 | performance.getEntries 空/Observer Noop（11-07 对拍定站） | 三条目表 + __perfRecord + 真实 PerformanceObserver | host-globals/host-async |

## 风控判定纪律

1. 无感通过是多维得分——环境指纹 + IP 质量 + 行为特征共同决定，不把「IP 好/坏」当单一归因
2. 403（challenge）与 429（限速）是不同机制：求解解决前者；后者需频率控制/出口轮换
3. 浏览器 TLS 指纹是硬约束——采集与求解提交必须同指纹（Firefox impersonate）
4. 材料时效 5-10 分钟——过期 CF 拒收（400 + cf-chl-out）；CF 变体每会话轮换，跨会话材料不可混用

## 已知边界（如实）

- ruyijs 0.2.2 有 document 切换竞态缺陷（advance 抛 JSError 但 context 存活，调用方容错继续泵；详见 docs/ruyijs-0.2.2-document-swap-race.md）
- Node 求解不收敛是结构性的（键控流分歧在宿主读数值级，无 ground truth 不闭合），不再作为完成门
- 静态链：v0 加密器已离线复现（R1 完成）；剩余 R2 = MZ 24 键字段值来源模板化；D 类闭包键的跨变体稳定性未验证；turnstile widget 自有脚本（api.js/rch）载荷未覆盖（5,260B body 归属，独立 alphabet 实例）
- 行为指纹字段（性能基准/时间戳）为 Node 真实值而非浏览器值——收紧期可能成为下一变量
- `web_case.py next` 调度器当前因 facts 键（ruyijsLiveEmit）版本不匹配崩溃（工作区 HEAD 版 web_case.py 落后于 contracts）

## 文档地图

| 文档 | 角色 |
|---|---|
| `docs/status-20261107.md` | 当前状态与分析总览（先读这个） |
| `补环境进展清单.md` | 时间线流水（新条目在顶部） |
| `analysis-progress.md` | 历史证据链（2026-09~11） |
| `docs/web/index.md` | web-reverse 流程状态索引 |
| `triage.md` / `report.md` / `findings.json` | case 流程文件（10-05 快照，头部有更新注记） |
| `archive/20261107/` | 已归档过时文档 |
