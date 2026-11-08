# 2026-09-28 有头复看：无感通过

Case: `psa-cf-5s-shield-20260815`. Run: `rt_20260928075623_d3a207a25f`. 没有 cookie、token、ray 或 body 原文。

## 不是无头

- `request.json` 的 mode 是 `interactive`。RuyiTrace 3.3.0，`dom-observe`，`fingerprintMode=baseline`，proxy direct。
- 文档请求的 UA 产品是 Firefox，字符串里没有 headless。
- profile 的 `prefs.js` / `user.js` 里 headless、marionette、webdriver、remote.enabled 计数都是 0。
- event 分区没有 click / pointerdown / mousedown。命中 “click” 的三行是 `eventListenerAdds`，不是点击。

## 这次实际发生的事

从第一笔文档请求起约 7 秒：

| 顺序 | 方法 | 状态 | 是什么 |
|---|---|---|---|
| cert | GET | 403 | `cf-mitigated: challenge`，标题 Just a moment...，set-cookie 名只有 `__cf_bm` |
| orchestrate | GET | 200 | `application/javascript` |
| turnstile api.js | GET | 200 | 挑战脚本 |
| `/fo/` | POST | 200 | 请求 `content-type: text/plain`，响应 `text/plain` |
| turnstile frame | GET | 200 | widget frame |
| `/fo/` | POST | 200 | 同上，响应 `text/plain` |
| `/fo/` | POST | 200 | 响应变成 `text/html`，带 `cf-chl-out` |
| `/fo/` | POST | 200 | 响应 `text/html`，set-cookie 名含 `cf_clearance` 和 `__cf_bm` |
| cert | POST | 200 | 没有 `cf-mitigated`，标题 Cert Verification。set-cookie 名是站点自己的 `psa-locale`、`env` |

没有 `/eb/`。`jsd` 在证书页之后才出现（302 一次、200 两次），不是这次通过的门槛。

## 和上一轮的关系

`rt_20260928061614_ee71af43b2` 也是 interactive。cert 同样是 GET 403 然后 POST 200，标题同样变成证书页；`/fo/` 四次 200，一次响应带 `cf_clearance` 这个名字；`eb=0`。两轮都是浏览器自己无感走完，不是这轮突然变成无头。

## 和本地补环境的关系

浏览器不需要人手点选就会发出 `/fo/` 并回到证书页。本地 RuyiDOM 仍停在 orchestrate 内部的 `KP.call`，一次 `/fo/` 都没有。缺的不是点击。

索引已通过，receipt gate 停在 pending。没有把 case 标成 completed，也没有写 `serverAccepted`。
