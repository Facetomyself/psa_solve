# PSA fix_transport 正式执行回执（2026-09-30）

## 本轮结论

本轮发现并修复了**真实 transport 漂移**：Gecko 默认 `network.proxy.type=5` 读取已开启的 Windows 应用 HTTP 代理，native Necko 因代理拒用 Alt-Svc/HTTP3；不是 h3 mapping 丢失或 QUIC 超时。只在 Gecko 进程内设置 `network.proxy.type=0` 后，同锁定 runtime 的 5 条 FO 实际全部恢复为 h3。**业务仍未推进到 form / cert document POST，目标未完成。**

原 Windows 代理配置、TUN、urllib fresh-fetch 路线和所有其他真实补丁均未改；facts/active-baseline/workflow 合同未由本切片改写。没有提交或推送。

## 授权与执行范围

实际 `web_case.py next` 给出 `fix_transport / turnGate=blocked`，并指定阅读 risk-analysis/request-chain；本切片只完成这个 action。未创建新 action/profile/dispatcher，也未消耗或修改 v2 diagnostic claim/budget。

| phase | fresh 材料预算 | live engine 预算 | 可变面 | 终态 |
| --- | --- | --- | --- | --- |
| transport diagnostic | 1 / 用尽 | 1 / 用尽 | 在原 v2 runner 外新增 4 个 chrome-only effective-pref 快照和 native MOZ_LOG；不改目标或 page hooks | CLI/engine exit 0；无 timeout |
| 同 transport repair（父线程依据日志追加审阅） | 1 / 用尽 | 1 / 用尽 | 仅 `network.proxy.type=0`；同一快照族加 proxy.type 读回；其余变量保持 | CLI/engine exit 0；无 timeout |

固定 scope/argv SHA 在 spawn 前回报，启动后回报 PID 并持同 exec handle 等终态：diagnostic wrapper/CLI PID 33640/51044（exec 36332）；repair 32460/16296（exec 72818）。这些均已终止，没有活进程句柄待接。

- diagnostic run：`evidence/web/transport-diagnostic/e0b71e462e87439696301f2b211a7ea1/`，argv SHA `8ecf4b99293fdf8770e0769b0bbea2b1ef880950f66f65a2041e07c31ca2c84e`。
- repair run：`evidence/web/transport-diagnostic/3355e716c80b4c60b07c8caa5c2d2a57/`，argv SHA `6d532e7793216823c66b33ace166fffe559d5330e3e7b0e351b2df15f02e91d7`。
- 两次均使用同一 Gecko 135 binary/library lock、UA155 override、HTML/material 导入、history 与其他真实修补、原可信 click/pointer、`MOZ_FORCE_DISABLE_E10S=1` / `MOZ_FORCE_DISABLE_FISSION=1`。
- fresh 材料复用已存 wrapper.fetch_fresh，UA135、CookieJar、opener/系统代理处理原样不变。spawn 前独立目录的 challenge/orchestrate/cookie/input 全部做 SHA 校验，固定 argv 绑定 input/source/hash；不回放历史 response。
- `MOZ_LOG=timestamp,sync,nsHttp:5,nsSocketTransport:5,neqo_transport:5,neqo_http3:5` 写独立 restricted 文件；没有 debugger、Worker 插桩或 response/body 改写。
- 所有诊断数据和 raw Cookie/body/nonce 只在 gitignored evidence 目录；本文只保留脱敏结论和 hash。

## 原因证据：为何 retained mapping 仍 h2

诊断轮四阶段快照证明：HTTP3 enable 为 true，backup timer 5000，带引号 page-host h3 mapping 与 force-use 值在 runtime init 前后、pump 末完全保留；native 日志也三次明确读取该 mapping。

真正阻断在 connection admission：native 日志 12 次 `AltSvcMapping::ProcessHeader ignoring due to proxy`；目标 host connection entry 包含 HTTP loopback proxy signature，`aNoHttp3=1` 共 24 次。没有 `Http3Session` 日志，5 条 FO 的真实 `protocolVersion` 都 h2。这里不是“尝试 QUIC 后超时”的证据。

只读来源核验：代理环境变量为空；Windows `ProxyEnable=1`，配置匹配 native 所见 loopback endpoint；同锁定 runtime 的无目标网络 canary 显示 `network.proxy.type` 默认 5，init 前后不变。**先前文档的“应用层 direct / 第一包已 h3”是旧快照，不能代表这次运行。**

原因范围：这条链能解释当前 H2/H3 transport 差异，不解释 missing form 的全部根因。

## 修复验证：真实 channel 与业务轴分开

修复源码对诊断 variant 的 exact diff 已验证：唯一行为变化是在现有 chrome pref block 加 `prefs.setIntPref("network.proxy.type", 0)`；另一个差异仅为既有 chrome 快照读取该 selector。page/source/hooks 无变化。

- effective proxy.type：设置前 5，既有 pref block 后 0、profile init 后 0、pump 末 0；HTTP3 mapping 仍匹配真实 page host。
- native：proxy-reject 0、实际目标 HTTP-proxy dispatch 0；实际 direct target dispatch 12，其中 h3 dispatch 9，出现 2839 条 `Http3Session` 日志。计数使用精确 `nsHttpConnectionMgr::DispatchTransaction [`，不把 `TryDispatchTransaction` 算实际 dispatch。
- **5 条 FO 全部实际 `protocolVersion=h3`**（page 2 / widget 3，altUsed=true）。其他 `/g/chains/` 仍 h2 正常，不宣称所有请求都必须 h3。
- widget `interactiveEnd,complete`；site partition bucket 观察到 `cf_clearance`；forms=0、submits=0、没有 cert document POST。
- 没有 same-session business content readback，因此 `localReproduced=false / requestBoundaryAligned=false / serverAccepted=false` 保持未通过。
- 运行后 Windows `ProxyEnable` 与 ProxyServer SHA 和诊断前完全相同，修复只影响独立 Gecko 进程，未改系统/TUN。

对 transport 的单变量修复已经验真；对业务卡点，只能确认**仅修 transport 不足以产生 POST**。立即停止 transport 相邻 prefs，不继续猜开关。

## 新 stable clean 副本（未单独 live 复跑）

`diagnostics/clean-baseline-20260930/ruyidom_bridge.stable-transport.js`，SHA `a6f0e51a8b8c99019678a508385cc21f66fd3205e08c512d3ccc8888a32433d6`。

从原 clean SHA `32cef74e67164611750ac2870546a2a4283f8b519ec4756e3a8f949fa3c0cd94` **只增加 1 行 / 49 bytes** `network.proxy.type=0`。原 clean、original、manifest 与历史 v2 profile/source hash 均保持不变。

反向证明：从本轮 live repair variant 精确删除 chrome snapshot helper、4 个 snapshot calls，以及 stock v2 相对 clean 的命名 capability 插入片段后，结果与 stable 副本 **byte-equal**。原嵌入式宿主 hook 与 clean embedded hook 也 byte-equal。static outer + embedded JS 语法检查均 exit 0。

stable 没有 chrome-pref 快照或末态 capability probe；原 clean 的旧 atob/Map/RTC/navigation 等观察与 global Proxy bridge仍原样保留，**不是零插桩 runner**。这个副本尚未单独 fresh live 重跑；h3 行为依据来自本轮使用同一 selector 设置的 live variant，不伪称 stable 全链已验收。

建议 workflow runner/evidence 当前入口采用 stable 副本与 repair machine receipt；本切片只建议，不直接改 `workflow-artifacts.v1.json` / active-baseline / facts。机器等价与验证详见 `diagnostics/clean-baseline-20260930/stable-transport-manifest.json`。

## 剩余卡点与下一证据

transport 已修，仍缺 **clearance response → DOM branch → form/submit 或排障 DOM** 的同会话因果绑定。现有 watcher 只记录少量计数/shape；清关长度类、eval.this identity、site cookie 名均不能代替因果 receipt，也不能当服务器接受。

下一刀应在正式 reviewed 门禁下使用已准备的 response-to-DOM causal observer，或单独审查 native-entry provenance；不混入这次 transport 操作。不得枚举新 getter、改 opaque 字节、重放成功 response、把不同 session 的 material 当同一输入。

父线程可凭本轮 receipt CAS 回 `firstDivergence=environment-gap / experimentHygiene=stop-search`，保留验证过的真实 transport patch；`hostProbe/body` 不动，所有完成轴仍 false。本切片没有写 facts，当前期望 revision 为 2（执行前仍需重读）。

## 可复核 artifacts / log hash

- cause：`agent-notes/20260930-transport-live.cause.json`，SHA `46c2f08246e4a6796be1f04c753538a67851f2225747ef442139982ec89aba79`。
- repair：`agent-notes/20260930-transport-live.repair.json`，SHA `7d9f3c348490722cfadc444cd2d01f9fb90b229ac48759b56cc511d99c5c3a42`。
- closure：`agent-notes/20260930-transport-live.closure.json`：两次 fixed argv/time/exit、12 个 raw hash 复核全部通过，原 facts SHA 未变。
- diagnostic native main log：31027347 bytes，SHA `54395c9682925b87c35c460b2652d5bfc7a2a5175f19dd5ce6a1cdc3e2126ef0`。
- repair native main log：42637765 bytes，SHA `3d7f0389447740335c53fe69a7a4d61cd4d66a77f1aec27b24c498842905009a`。
- live状态：`agent-notes/20260930-transport-live.state.json`；repair状态：`agent-notes/20260930-transport-live.repair.state.json`。

限制：urllib-UA135 fresh fetch可能仍采用系统应用代理，而 repaired Gecko 使用 engine-local direct；这仍是 logical material/Cookie handoff，**不是同 TLS / 同导航 provenance**。MOZ_LOG 同步日志也有 timing/IO 观测扰动；不得依据它重建真实耗时常量。此前 native/eval synthetic canary 使用的 fission env名字与历史 wrapper不同，本轮正式两 phase 均已改为历史实际 `MOZ_FORCE_DISABLE_FISSION`；该 synthetic 只支持所测 realm/API能力，不升级为完整 challenge parity。

## 状态字段收口

原 fresh-generator 在抓材料阶段将 `onlineExecuted=false` 写入共享 phase state；本 wrapper 初版只更新了 `targetNetworkExecuted` 与 spawn/exit 字段，导致遗留显示不一致。现已凭两份 `execution-receipt.spawned=true / exitCode=0` 将两 phase 的 `onlineExecuted` 纠正为 true、terminal 为 completed，保留历史 CLI PID 51044/16296 且 `cliPidAlive=false`、wrapperPid=null；历史默认值与原因仍留在 state。wrapper 的 spawn/terminal 状态同步也已修正，不会再让后续恢复误判成未跑。未重启或新增线上运行。
