# Crypto Parameters

Case: `psa-cf-5s-shield-20260815`

Encrypted, hashed, encoded, and derived parameters. Record algorithm class and input names here. Do not write raw keys, tokens, or ciphertext.

## Notes

- `/fo/` 正文是挑战运行时生成的不透明载荷。这里不还原算法，也不保存正文。
- 带 `cf-chl-out` 的清关响应是 base64。本地 `atob` 走 3488 到 2616 再到 1960，然后创建排障节点。有头的 3792 才进入建表。
- 建表分支才会用到初始页里的 `md` 和 `mdrd`。本地长度分别是 1215 和 426，因为 `createElement("form")` 没运行，所以没有抄进 hidden。
- 表单形态只作类别：`method` POST，`enctype` 为 `application/x-www-form-urlencoded`，三个 hidden，然后 `form.submit`。这不是已拿到的请求。
- 解码首字节是服务端选定的载荷类，不是宿主分数。`serverAccepted` 仍是 fail。
- 2026-11-02 ruyijs `rj_20261102062310_d7463f5c` 离线 `parameter-analysis`：canonical HTML 5755 B，hostSurfaces `console,net`，requestBoundary GET/POST count=4 matchedCount=2，eval 计数 formCount=0 inputCount=0 iframeCount=0 cookiePairCount=0。这不是 `localReproduced`，也不是 `serverAccepted`。未写 `parameterAnalysis`。

<!-- generated:crypto-parameters -->
| name | endpoint | location | kind | sourceKind | inputs | browserObserved | localReproduced | serverAccepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fo-body | page-fo | form | encoding | challenge-runtime |  | pass | pass | fail |
| fo-body | clearance-fo | form | encoding | challenge-runtime |  | pass | fail | fail |
| form-body | cert-document-post | form | encoding | challenge-runtime |  | pass | fail | fail |
<!-- /generated:crypto-parameters -->
