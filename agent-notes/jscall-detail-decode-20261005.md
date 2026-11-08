# JSCall detail 窄解码回执 / 2026-10-05

## 范围与状态

- 状态：done，证据增量成立；不是 Node 补环境完成，不解锁 dispatcher。
- run：`rt_20261005125421_1d84c46dcd`；已 completed；只读取其既有 indexed 文件。
- 未运行目标 JS、浏览器、网络、canary；未修改 runner、facts、workspace 状态。
- 可复跑数据处理脚本：`jscall-detail-decode-20261005/decode_subset.py`。
- 脱敏机器回执：`jscall-detail-decode-20261005/identity-source-subset.json`。
- 原始 decoder 人读输出留在该目录 `restricted/pid50068-values.txt`、`restricted/pid51372-values.txt`，不应发到对话或作为无审核输入。

## 输入完整性与执行

六份 bin/dict/detail 均按 receipt 核验 `indexed=true`、`indexMatch=true`、实际 bytes 和 SHA-256 一致；完整值见机器回执 artifacts。不是把未索引 `.bin` 当事实。

| pid | bin bytes / SHA-256 | dict bytes / SHA-256 | detail bytes / SHA-256 |
| --- | --- | --- | --- |
| 50068 | 1360912 / `9307a2bbdbcd94e42ba48fa43081e134157906b6c0ffc18a11395dcacc7ae066` | 525453 / `c1fe557ea0e54db058b330b8f47336bab4edd73bad3604934f8bf81cdd29df0f` | 1314744 / `69afb5d9f9ebf15796d7c5fdd6bf50760fd753aedddac7b152dc9d4f6e2dcad5` |
| 51372 | 177968 / `ca99e7bde4d77c5f787444f4da402c8526ef826c4d2230bcc89930557e62c71a` | 118937 / `58ea443fc99b0098d4a499a964225aaa0316952c2a0db98dcf788372cedc51e8` | 11548 / `5774b51ea8507ad77800e9bc7b3a89e14e282ffd26d644b29173b1fea5f590a6` |

两进程均实际调用仓库 `jscall_decode.py <bin> --dict <dict> --detail <detail> --values --output <restricted output>`，exit 0；完整命令保存在 JSON 的 decoder_command。普通 call 分别 42528 / 5561 条，trailing bytes 均为 0。随后复用同一解码器的 read_records/load_dict/load_detail/enrich 提取 flags；`--values` 的人读输出本身不包含全部 flags，不能靠字符串猜测 stable identity。

## 精确 call 与 DOM 对齐

| pid / DOM line | origin call / parent | 结果与 flags |
| --- | --- | --- |
| 50068 / 101 | 1030 / 900 | `get body` 的普通 call 找到；detail 没有该 call 的 slots。DOM 返回 HTMLBodyElement，不能伪称有 JSCall return detail。 |
| 50068 / 102 | 1032 / 900 | `attachShadow` 的 this/arg0/return 全为 stable identity-only，均非 truncated、unreadable；this 和 return 的 JS id 与 DOM 一致。arg0 的 JS id 也与 DOM argsObj 一致。 |
| 51372 / 83043 | 2687 / 2620 | `createElement` arg0 为完整字符串 `div`；return 为 stable identity-only，匹配 DOM HTMLDivElement。this 是 `?` 标记 unstable identity，明确排除 join。 |
| 51372 / 83044 | 2688 / 2620 | `attachShadow` this/arg0/return 全为 stable identity-only，均非 truncated、unreadable；this、arg0、return 的 JS id 与 DOM 一致。 |

iframe 链：同 pid 的 DOM getter return JS id/nativeId = attachShadow this JS id/nativeId；attachShadow 的 JSCall this 与 DOM this 再次 join。故 `get body -> HTMLBodyElement -> attachShadow` 在该 run 已证。getter 无 detail 不妨碍 DOM 内 identity 链，但不能声称全链每端都有 detail。

API 链：JSCall createElement return = JSCall attachShadow this = 两条 DOM 对应 JS id，且 DOM nativeId 相同；故 `createElement('div') -> HTMLDivElement -> attachShadow` 在该 run 已证。所有 join 都限定 run/pid；不是把 JS id 与 nativeId 直接比较，不 join `?`，不跨 pid 或跨 run。

## source 与调用图限制

- DOM iframe 调用位置：`df` line 1 col 207105 / 207126；parent 900 为 `df`，函数定义起点 col 203142。定义起点不是调用偏移。
- API DOM 调用位置：`xe` line 2 col 74781 / 74808；JSCall parent 2620 是 native `call`，它的 parent edge `parent_exact=false`，不能把它直接改名为 xe 或声称完整相邻调用栈。四个选中 native call 自身 parent_exact=true。
- fixture URL 去掉 session/path 动态标识与 query；不包含 nonce、Cookie、token 或目标代码。原始文件定位靠 run、pid、DOM line、call ID 与 source hash。
- 重新读取本 run HTTP packet，API response source chars=86732 / SHA-256 `76763bb46224400a11af989831d62d06629aba6f67d50cac96afae4a590adf59`；iframe 首段命中的 inline script chars=238893 / SHA-256 `eee05641ead359eed27d49331f02cab589feca0c6373b41305e03eb72e9870a7`。只匹配 hash，不执行代码。
- iframe 两条 df 顶层 source URL、API 两条 xe 及 Se source URL 均与对应 packet URL 精确一致。API 栈更深的 jj 属于另一个 orchestrate source，fixture 标记 exact=false；该祖先不能错误归到 API source。此处只证明同 run browser source，不是与历史 Node source 一致。
- 两个 attachShadow arg0 都只有 Object identity；没有 options 内容，无法从 detail 得出 mode、delegatesFocus 或其它配置。
- DOM producer `complete=false`、JSCall gate 排除、sources_unavailable 和 per-function 限额仍存在；receipt pass 和 decoder exit 0 不证明全覆盖。

## 阻塞与下一步

这份 fixture 是同 run browser identity/source 参考子集，不是 browser/local source-aligned parity fixture。历史 Node iframe source hash 与该 run 不同，且 local receiver creation/ownerDocument/identity 仍缺记录；不能据此给 HTMLScriptElement 添加 attachShadow，也不能直接宣布首错归因或进行受 blocked 禁止的试补。

主线程可登记已证的两条 identity 链与 detail 内容限制。下一步需要由 dispatcher 允许的 source-matched local provenance 取证：保留实际 tag、ownerDocument、receiver identity、creation/query 来源和 `receiver===document.body`，再判断 factory/document typing 单 surface 修正。业务闭环仍要求 Node 独立执行、请求边界 parity 和同 lease 独立 readback，浏览器成功不替代这些验收。
