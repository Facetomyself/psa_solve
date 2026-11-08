# 内核对照：本地求解与有头 Chromium — 2026-10-03

本地会话 `a7e045b6cf194921bb229b6741e59b8b`（transport-fixed causal observer）。有头目录 `headed-20261003`。只比外部边界。有头是内核对照，不是 browser fact。时间只保留先后，不当真实耗时。

响应长度是两套计数器：本地为 HTTP 活动在响应完成时的 extraSize；有头为 loadingFinished 的 encodedDataLength。不把这两列相减当成逐字节差。本地第 1、第 5 跳另有顶层 XHR 解码长度类。

## 1. 对齐表

五条 FO，顺序即跳序。头名只记有无。set-cookie 只记名字 `cf_clearance`。

| 跳序 | host 类 | method | status | 本地请求字节 | 有头请求字节 | 本地响应 | 有头响应 encoded | content-type | cf-chl-out | cf-chl-out-s | cf_clearance 名 | DOM 结果类 |
| --- | --- | --- | --- | ---: | ---: | --- | ---: | --- | --- | --- | --- | --- |
| 1 | page | POST | 200 | 2252 | 2380 | 活动 80867；解码类 106876 | 81560 | text/plain | 无 / 无 | 无 / 无 | 无 / 无 | 两边的 h2 都在这条之前，是插页 |
| 2 | challenge | POST | 200 | 4738 | 4748 | 活动 579588 | 575840 | text/plain | 未记 / 无 | 未记 / 无 | 无 / 无 | — |
| 3 | challenge | POST | 200 | 83372 | 92460 | 活动 88605 | 86784 | text/plain | 未记 / 无 | 未记 / 无 | 无 / 无 | — |
| 4 | challenge | POST | 200 | 86530 | 95735 | 活动 5071 | 8472 | text/html | 未记 / 有 | 未记 / 有 | 无 / 无 | 有头此跳已是 html 且头名在 |
| 5 | page | POST | 200 | 8695 | 9132 | 活动 2673；解码类 3488，标成 noform | 4953 | text/html | 有 / 有 | 有 / 有 | 有 / 有 | 本地 diagnostic；有头随后 form |

斜线左侧是本地，右侧是有头。第 2–4 跳的本地 `cf-chl-out` / `cf-chl-out-s` 不在顶层 XHR 头名表里，写成未记，不写成无。

证书 document：

| 侧 | 有无 | status 类 | 请求字节 | 响应 encoded | content-type | cf-chl-out | cf_clearance 名 |
| --- | --- | --- | --- | ---: | --- | --- | --- |
| 本地 | 无 | — | — | — | — | — | — |
| 有头 | 有 | 先 307，再 GET 403，form 之后 POST 200 | POST 2648 | GET 403 为 4139；POST 200 为 24653 | text/html | 无 | 该 POST 上无此名 |

307 只是证书路径上更早的 document 跳转类，没有单独的完成长度。证书 POST 200 不是 `serverAccepted`。

## 2. 仍然相同的边界

- 五条都是 POST，status 都是 200。
- host 类顺序都是 page、challenge、challenge、challenge、page。
- content-type 类都是 text/plain、text/plain、text/plain、text/html、text/html。
- 第 1 跳两边都没有 `cf-chl-out`、`cf-chl-out-s`，也没有 `cf_clearance` 名。
- 第 5 跳两边都有 `cf-chl-out`、`cf-chl-out-s` 和 `cf_clearance` 名，且都是 text/html 200。
- 有头的两条 h2 在第 1 条 FO 之前。本地插页 h2 也在 FO 响应之前。那不是清场之后的排障 DOM。
- 有头第 2、第 3 跳没有 `cf-chl-out` 名。本地这两跳未记，不能拿来当差异。

传输栈不是同一计数（本地 h3，有头 h2）。材料交接也不是同一 TLS。这次不把协议版本写成 DOM 分叉的原因。

## 3. 分叉点

分叉在第 5 跳响应之后，不在请求是否发出。

本地把这一跳的 `cf-chl-out` 标成 noform，解码长度类 3488。随后 DOM 类是 diagnostic：createElement 为 h2、p、ol，没有 form。`forms=0`，`submits=0`。证书 document 没有出现。

有头在第 4、第 5 两条 html 响应（都带 `cf-chl-out` 与 `cf-chl-out-s` 名）之后出现 form，然后才是证书 document POST，status 类 200。更晚还有 form，那些在证书 document 之后，不是这条分叉。

这是响应之后的 DOM 分支。本地走的是已标成 noform 的那份 html，不是运行环境里缺少 `HTMLFormElement`。有头钩子没有安装 `HTMLFormElement.submit`，缺绑定也不能证明这个方法没被调用。证书路径上的 document POST 才是有头的导航事实。

## 4. 已关闭

`__clickTs` 没装上。赋值和监听在同一个空 `catch` 里。`clickErr=missing`。`lookupRing` 有 `click:f0`、`ptr:8`、`click:f1:c1`，没有 `click:arm`。

观察到的点击是另一条 400ms 定时器上的 `tryClickWidget`，加上 `ptr:8`。第一条没找到 iframe，后来合成一次点击。这三条都不安装 `__clickTs`。

第 3、第 4 跳请求字节差是 9088 与 9205，约 9KB。不是可读点击轨迹。字段不对齐，保持不透明。旧草稿里把这个差归因到点击的那句作废。

## 5. 不主张

有头证书 document 的 200 不是本地 `serverAccepted`。这次有头采集也不是已登记 browser fact：`integrityConclusion=partial`，没有把 Chromium 平面写进事实。`experimentHygiene=stop-search` 仍在。`requestBoundaryAligned` 仍是 false。`ruyidom` 仍是 diverged。本切片不迁移合同，不重跑浏览器，不重跑 RuyiDOM。

## 6. 剩下的最小外部差异

清场那跳两边都已带 `cf-chl-out` 名和 `cf_clearance` 名，其后本地进入排障 DOM 且没有证书 document，有头则出现 form 再发出证书 document。
