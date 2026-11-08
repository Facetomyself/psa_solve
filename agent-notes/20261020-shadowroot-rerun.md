# 同一条 RuyiDOM runner 重跑 / 2026-10-20

本拍只重跑现有 stable-transport runner 一次，看请求边界类。没有改 bridge，没有装 shadow surface，没有打开 `Document.createElement`，没有改 facts 或完成轴。

## 启动

- runner：`diagnostics/clean-baseline-20260930/ruyidom_bridge.stable-transport.js`
- SHA-256：`a6f0e51a8b8c99019678a508385cc21f66fd3205e08c512d3ccc8888a32433d6`（与预期一致，未改字节）
- 入口：`ruyidom_run_start` / `ruyidom_run_status`，`allowNetwork=true`
- run id：`ra86baf771dd24b9e803f`
- 材料路径沿用 transport repair 那份已有输入。trace 改写到本刀目录，避免追加旧 jsonl。`rerun-input.json`。
- 脚本结果 `ok=true`。会话层在进程已退出后把 exit 记成 -1，这不是超时，也没有第二轮。

## 边界类

证书 document POST：no。`forms=0`，`submits=0`。FO 计数为 0，没有 POST。

| 面 | method | url 类 | status | body 长度类 | 次数 |
| --- | --- | --- | --- | --- | --- |
| handler | GET | orchestrate script | 200 | 0 | 1 |
| handler | GET | favicon | 0 | 0 | 4 |
| response | GET | favicon | 200 | absent | 1 |

response 那条 favicon 的协议类是 h2。3488/3792 没有出现。runner 自己的 lookup 环是 remote=1、fission=1，起始 principal 类是 about:blank。dist runner 不写 e10s/fission 开关，本进程也没有继承关闭值。没有为此再跑一次，也没有新写 harness。

`businessAcceptance=not-asserted`。没有写 `serverAccepted`、`localReproduced`、`requestBoundaryAligned` 或 `experimentHygiene`。`hostProbe` 仍留 `awaiting-record`。
