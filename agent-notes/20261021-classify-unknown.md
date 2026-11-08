# 3028 的 unknown 不是标错的 SecurityError

2026-10-21。本拍只核对放行谓词 `_injected_blank_security_error` 和已发布采集器 `describeScriptError`。没有改 helper，没有重签 scope，没有重跑 baseline，没有写完成轴。

## 谓词

`_injected_blank_security_error` 要求同一条 side 同时是 errorName `SecurityError` 和 insecure true，再加上注入 about:blank、parentLine 1447、sourceLineLength 0、receiverState unknown、receiverId uncollected。缺任意一项就停在 `verify_host_execution`。

官方 baseline `ea18496ee8c9455191d9b0ba4f70602e` 的绑定 side 是 errorName `unknown`、insecure false。同一采集器先前对 `ca950504` 记过 `SecurityError`，对 `18a7b243` 记过 `TypeError`。采集器 sha 没变。

## 分类规则

`errorNameOf` 只从 `errorMessage` 里取以 `Error` 结尾的词；消息含 `NS_ERROR_` 时记 `nsresult`；否则记 `unknown`。`hasException` 且 `exception.name` 有值时，用这个名字覆盖。`insecureFlag` 只看 `errorMessage` 是否含 `The operation is insecure`，不看异常名字。

用已发布 `write_probe` 抽出的函数在 Node 里跑了四条，没有启动宿主：

- 没有 `Error` 词、没有 insecure 短语、也没有异常名字：errorName `unknown`，insecure false。这和 `ea18496e` 的 side 相同。
- 消息是 `SecurityError` 且含 insecure 短语：errorName `SecurityError`，insecure true。
- 消息仍无 insecure 短语，但 `exception.name` 是 `SecurityError`：errorName 会变成 `SecurityError`，insecure 仍是 false。回执是 `unknown`，所以这条覆盖没有发生。
- 消息含 `NS_ERROR_`：errorName 是 `nsresult`。回执不是这个值。

因此这条 side 不是把注入 `SecurityError` 标丢了。消息里没有 `*Error`、没有 `NS_ERROR_`、也没有 insecure 短语，异常名字也没有把 errorName 盖成 `SecurityError`。`20261021-history-forward.md` 已把同一 helper 的这条消息归成对属性 `length` 的权限拒绝。把这个身份改写成 `SecurityError` 会让放行谓词认错对象。本拍不改采集器，不改门。

## 完成轴

没有证书 document POST，没有同租约回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 仍是 false。`experimentHygiene` 仍是 `ok`。
