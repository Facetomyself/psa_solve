# 2026-10-20 卡点对照

同一出口 `127.0.0.1:7897`，证书页。不写 `serverAccepted`，不改宿主补丁。

## 这一轮测到的

- curl-cffi `impersonate=firefox`（库内是 firefox147）两次都是 HTTP/2。响应 403，body 长度 5790，title 长度 16，页面类 `challenge`，有 `cf-mitigated`。显式 `http_version=V3` 仍协商成 HTTP/2（`httpVersion=3`，这是 libcurl 的 HTTP/2 代码，不是 30）。回执 `agent-notes/20261020-transport-cause.json`。
- 紧接着的 Firefox 151 也先停在同一类挑战页（title 长度 16），约 6 秒后转到证书页。页面内 `fetch` 为 200，body 长度 134554。回执 `agent-notes/20261020-browser-js-rpc.json`（07:58:59Z）。
- 07:49 的上一轮 Firefox 同样是先挑战、再进证书页。curl 的 403 不是把出口打进挑战模式的起点。

## 原因

裸的 curl-cffi GET 停在挑战文档上，因为它没有执行这道 managed challenge。真实 Firefox 收到的也是挑战，差别是它把挑战做完了。

这组对照没有测到「边缘只放行浏览器 TLS、单独拒绝 firefox147」。HTTP/3 也没有在这个 HTTP 代理上谈成。

Node / RuyiDOM 的原卡点还在：清关 `/fo/` 之后本地不建表单、不 `form.submit`，尾部是排障 DOM。调度仍是 `refuse_host_enumeration`。浏览器可以当 oracle，还没有被 Node 求解替代。
