# 10-23早间正式链与Node新分支运行态审计

## 范围与证据

09:32–09:37 +08:00只读快照，对照10-22晚20:04报告（最新40b28...于19:42:02结束）。主线程当前authorize_form_construction_surface / blocked是新授权，不是已成功提交。本slice没有next/record/run/目标/网络/测试/终止，没有改源码、goal、facts或原运行产物。

脱敏证据在 `diagnostics/morning-correction-audit-20261023/runtime/`：`formal-timeline.redacted.json`、`node-diagnostics.redacted.json`、`scope-and-consumers.redacted.json`、`processes.redacted.json`、`node-current-files.redacted.json`、`final-state-check.redacted.json`。不回传Cookie/token、完整命令或消息载荷。

## 1. 正式Gecko host链：只有2次新增失败baseline

40b28之后新增 **2次正式execution / 同1个scope c8e9652b...**：

| run前缀 | 正式终态 | variant/status | 外层timeout |
|---|---|---|---|
| a5c33751 | 10-22 22:14:05.944 | baseline / failed / exit1 | false |
| 7e398482 | 10-23 01:18:57.523 | baseline / failed / exit1 | false |

collector墙钟累计48.037秒，不含Node新分支、临时probe、模型/工具等待。无patched、completed正式终态。

两份raw独立实hash匹配且相同，仍是3:544、matched=false，仅host-diagnostic+summary，未捕获host-observation/wire/necko/resp。side均进入execution引用并匹配。它们并没有随着后续Node消息诊断变成新Gecko业务结果。

## 2. Node新分支确有独立产出，不应因未登记就全盘否定

20:04后项目出现 **8份psa-node-host-rerun.v1诊断JSON，合计18条不同(page/started/attempt) session记录**，来自post-iframe、worker2、apply、rearm、gap、exit、msg、inbound等目录。6条记录timedOut=true；其余包含exit0返回但未过业务读回的session。这18条是诊断记录数，不冒称正式collector执行数或独立验收数。

可观察的新信息包括第二个Worker的启动/返回、处理器安装、Reflect.apply内部循环采样、计时/tick推进及父页消息/表单计数；Node HTTP分支也有FO send→done/200的观测，而不再只是Gecko两行raw。这些是有价值的本地调试与传输现象，不是“因为无scope所以一律无效”。

但Node资料的覆盖/来源不足：

- 8份JSON均没有scopeId，runner仅为字符串runtime/run.js，没有runner/source/input/config/runtime的执行时hash链；path+sha文件引用数均0。
- 一些目录另有trace-summary.json，但最新post-msg/post-inbound目录只有自定义receipt，没有被哈希引用的stdout/stderr、原始事件、采集命令和执行时环境。
- 当前runtime/run.js、host-async.js、host-globals.js可以在本次快照锁hash，但不能倒签证明先前每个session实际使用了哪些字节。
- 因而它们不能和正式Gecko scope的旧输入/执行面合成一条“同baseline推进”因果链，也不能把鲜活页面获取/HTTP200直接升级为fresh-session一致、serverAccepted或Node完成。

本审计把这些Node结果标为“有观测，但provenance不足的独立诊断分支”，不假装已能重算所有循环计数或网络原始字节。

## 3. postMessage、入站队列、退出条件与HTTP POST必须拆开

- `postMessage`是窗口/Worker消息API，不是HTTP POST；worker启动后设置onmessage也不等于发送消息、父页派发或构造form。
- 9:18的post-msg修改是Worker入站队列：父侧发送早于处理器安装时先排队，处理器出现后再交付。本地夹具断言WORKER_INBOUND_OK只证明该局部队列用例，不证明真实目标调用了它。
- 9:30的post-inbound资料报告：相关样本Worker的onmessage已为function，但postMessage/timer/Atomics计数为0；其所计父postMessage、createElement、form、submit仍0。队列未被这条目标派发调用，没有证据把它认定为通往证书POST的缺失必要行为。
- post-exit的“退出”讨论是内部调用周期/Date.now间隔，不是HTTP响应验收，也不是操作系统进程exitCode0。约4200–4400万调用、周期20/22、tick停1/3是该诊断采样，不能据此直接恢复VM语义或点名一个host API。
- 超时被切断、stdout/stderr为0是另一种结果；不等于Node正常返回、也不等于服务器拒绝。post-msg记录22秒切断；inbound主页/抽样页分别16/12秒切断，不能把静默进程当已解决或崩溃。

## 4. FO有响应与业务接受仍分离

最新post-inbound内两条未启动第二Worker的session约3503/3504ms返回，exitCode0；其中09:26:05的记录有FO响应长度类20000+且同租约readback=403/challenge。post-exit也有类似退出为0、读回403的样本。

这些NodeHTTP观测说明某些样本确实到达请求响应阶段，但**不是证书document POST，更不是业务readback200**。不能用FO200或3500ms自然返回写完成轴；也不能因另一些样本长循环就抹掉已经观察到的HTTP阶段。

同样，Node资料certDocumentPost=false属于其采集/摘要覆盖范围，不是对机器全部网络的绝对证明；Gecko正式raw无网络行更不能否定Node另一路已经观察到的FO。

## 5. scope完整性与消费者：正式链未过期，也没有误放Node摘要

当前scope实际load_scope成功；5直接引用+13dependency共 **18文件全部实hash匹配**，未发现Gecko正式scope的runner/helper/库/资源漂移。state→execution、execution→side的实际verify_ref通过。

只读verified_classification仍拒绝（host cycle is not classified），_verified_host_pair=False，serverAccepted/localReproduced/requestBoundaryAligned三轴False。旧pair/classify未被新scope误当成功，也未见Node摘要被写成这三条正式事实。

这些检查只覆盖正式scope，不为runtime/lib新Node行为背书；未登记Node分支的版本/输入/采集环境仍需单独绑定。新authorize_form_construction_surface仅说明流程点名允许方向，不证明已有form或certPOST。

## 6. 活态、最后证据时刻与剩余限制

09:34进程快照没有PSA Node runner、xpcshell或firefox目标进程，最新正式PID已退出；state failed/pid=null，最终复读仍7e398。没有已知目标活句柄需继续poll，不restart任何东西。

当前Grok客户端23652、15528、54808存活，其中前两个各有ruyitrace/v8trace MCP；不将全部客户端强归PSA或推测并发写入。模型在线不等于目标在线。

最新正式执行终态01:18:57；最新Node诊断JSON落盘09:27:25，post-inbound笔记09:30:27。不同时间戳代表不同证据层，不要把新笔记时间写成正式baseline刚完成。

## 结论

**真实新增**：Node分支已产出Worker/消息/循环/HTTP阶段诊断，不能简单归成同一Gecko错误重复；正式scope绑定和side封存仍保持。

**未闭合/新偏差风险**：Node诊断未锁执行时runner/source/input/env/raw引用，不能跨runner升级fresh/accepted事实；Worker消息不是certPOST，入站排队夹具成功不等于目标实际派发；静默超时、exit0返回、FO200与readback403必须分别记账。

**当前验收仍未过**：正式链两次新增baseline都失败，Node也未给出可验证证书document POST及业务readback200。保持授权、局部机制与业务成功三者分离。
