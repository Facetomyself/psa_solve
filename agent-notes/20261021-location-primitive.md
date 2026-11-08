# location 原语守卫后的官方 baseline

2026-10-21。已盖章动作是 `repair_submit_host_behavior`，`turnGate=blocked`。本拍只做这一处已有表面：`installSandboxIdentity` 里，仅当读取 `location` 或 `String(location)` 抛出 `SecurityError`，或消息含 `The operation is insecure` 时，才换上返回 `document.documentURI` 文本的原语转换。健康的 `location` 不动。没有新开宿主面，没有改门，没有改采集器，没有写完成轴。

回归 `test_shipped_sandbox_identity_location_comparison_survives_security_error`：1 个测试，0.038s，通过。

重签前 `verify_ref` 找不到 `D:\reverse_ENV\mcp\ruyidom-mcp\dist\cli.js`。治理分支已把该树暂存改名到 `tools/ruyidom`，索引里的 `cli.js` 与 HEAD 都是 sha256 `0e9f36ab7c12709276f268b89b2504e95d55c5847ca77f158b1428fb863460b1`。工作区 `tools/ruyidom/dist/cli.js` 已改过，哈希不同。本拍只把 HEAD 的 71 个 blob 写回旧路径，不改 scope 里的 CLI 路径，不改索引里的改名，也不提交。

scope 重签为 `2e241bf099f9f5c79338714383d0c8e73f9cc4a661cea4679358825946c2bdba`。helper sha256 `3292f11df1d4b906883bb96e801fb09b1e5ef7d90686e5c36d3fa54df3dc83d4`，路径仍是 `document-principal.js`。`load_scope` 通过。priorScope 是 `7eb3e7dd9771abb76ad703fa40fbeb16afcf8434e30dbb71b031f874bc986aa6`，其中官方 baseline 是 `dd3f7a2723a4487ea116c04c650425d9`。runner sha256 `31746c03fd9890d48317faec1e2aa5ff5f99c7d63e0ce27c87b0956a5fa54d8a` 未变。CLI sha256 仍是 `0e9f36ab7c12709276f268b89b2504e95d55c5847ca77f158b1428fb863460b1`。

官方 baseline `9d37d27a432f4e1fa6ea973ca8b31fe0`：status `failed`，exitCode=1，timedOut=false，pid 47072。startedAt `1792583767148085100`，finishedAt `1792583776226245700`，相差 9078160600 ns，约 9.1s。failure 是 `execution did not complete successfully`。stdout 与 stderr 都是空文件，sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`。argvHash `c59fda2ca207628d5f3692e404dbff1c72ac2a904c8980ecb1db27827030a87b`。execution.json sha256 `d9eace43d5a2b6eb1b7fdf40e4e5021a0daa1212112d7c87e01903fca364ed30`。

raw 222 字节，sha256 `534609ca23a0472c035bc74092454398420761e448eb632583db28adac35ac2c`，与 `dd3f7a2723a4487ea116c04c650425d9` 和 `356e17e4159e4aee8da0a6cc37d3d8c8` 字节相同。事件只有 `host-diagnostic` 和 `summary`。诊断是第 2 行第 3028 列，matched false，base 是 object，sourceSha256 `262a1bf5d34372c576dee9a5941b7ae491f20b496ed6108fb072ae632c6c36cd`。没有 `host-observation`。raw 没有请求行。`summary.ok` 为 true 只是摘要事件里的字段，执行状态仍是 failed。

side sha256 `685ff13888535deb1104f0743711177d14997cc5b1732d278f6317eb4345855e`，与 `dd3f7a27` 的 side 字节相同。base `object`，getEntries `function`，finished false，access、threw、receiverId 都是空。`scriptError` 只有 kind `other`、class `other`、line 2、column 3028。探针文件 sha256 换成 `5ad40e0797944436ac9228fc2a50389c402acd71bb883b0fd7480f382cd14d19`，side 和 raw 没有变。

这张回执仍停在第 3028 列，没有到 `HTMLFormElement.submit` 第 75507 列。没有证书 document POST，也没有同租约回读。把抛错的 `location` 原语换掉，没有移动官方列号，也没有改变 raw。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。本拍不再加另一个宿主 API。
