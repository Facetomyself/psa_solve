# 2026-10-20 浏览器 JS RPC 可行性

控制面探针，不是宿主补丁，也不写 `serverAccepted`。调度仍是 `refuse_host_enumeration`。

- 浏览器：ruyipage `151-proxy` 新配置档。出口：本机 Clash `127.0.0.1:7897`，不是 Cliproxy sticky lease。
- 目标：证书页。导航约 6 秒内从 challenge（title 长度 16）转到证书页（title 长度 27，正文文本长度 1894）。
- 页面内 `fetch(credentials=include)`：HTTP 200，未再跳转，body 长度 133745，页面类 `cert`，耗时 536 ms。
- 判定：这一条上，浏览器页面 JS 发请求可行。回执 `agent-notes/20261020-browser-js-rpc.json`。
- 边界：本回合没有并列打 curl-cffi，所以不能把「curl-cffi 正在被拒」写成已证实。Node 纯补环境和同 lease 的 `test.py` readback 仍未完成。
