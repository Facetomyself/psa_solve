# 2026-09-28 文档上下文

Case: `psa-cf-5s-shield-20260815`  
结论: blocked。未改文件，未再跑 Gecko。

## 双条件

- 浏览器事实：挑战页在站点文档里执行，不是 about:blank。
- 本地事实（上一轮 `20260928-ruyidom-rerun.md`）：`injectedScript` line 2 `SecurityError: The operation is insecure`，错误文件名是 `about:blank`。随后未放行网络，进程死于 `www.psacard.com`，fo/eb 未落盘。

## 现有入口

- `diagnostics/ruyidom_runner.js` 已有路径就是 `options.url = challengeUrl` 加 `secure: true`。这会进 RuyiDOM `_createOfflineURLDocument`。
- 该函数对站点 URL 调用 `createAboutBlankDocumentViewer(principal)`，再用 `setCurrentURIForSessionStore`。文档载体仍是 about:blank。引擎只改 `document.URL` / `documentURI`，没有把 `location` 换成站点文档的开关。
- runner 里没有别的「打开挑战 html 为安全站点文档」参数。不传 `url` 会落到临时 `file://`，那不是站点文档，本轮不用。

## 不能用的旧路径

- 2026-08-15 注释写明：about:blank viewer 上 `history.replaceState` / `pushState` 抛 SecurityError，init script 用它重写 URL。
- 这段包装和 Storage 原型包装只在 `ruyidom_cf_shield_v1.js`。同一脚本还有 opcode 插桩、UpvLO0/ZHfDS6 桩。按本刀约束不复制、不执行。
- 因此缺的现有入口是：不带 opcode 插桩的站点文档身份（或同等的 history 宿主包装）。diagnostics runner 本身没有这个入口。

未写 cookie、token、指纹。未放行网络。没有 fo/eb 新计数。不能声称 serverAccepted。
