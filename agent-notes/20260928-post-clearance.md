# 20260928 post-clearance

run `rt_20260928075623_d3a207a25f`。源：`raw/http_packet/*.http_packet.json`（149，meta.seq / startMs / endMs）。不写 cookie、ray、query、证书号、body。

- 最后一次 POST `/fo/` 200（Set-Cookie 名含 `cf_clearance`，seq 28，endMs）到证书页 POST 200（seq 29，startMs）之间：请求 **0** 条；时间跨度 **0** 秒（端点差 24ms，取整为 0）。两包之间无重叠 start。
- 区间内请求：无。method、path 模板、host 类、status、content-type 均无条目（content-type：缺）。
- 区间内没有 `/g/chains/`、`/eb/`、turnstile、document 导航。已写入包里 turnstile 只有 seq 18（script）和 seq 21（subdocument），都在这次 `/fo/` 之前；`/eb/` 为 0。`/g/chains/` 只出现在 skipped background（45 条中 40 条 GET，host 类 other，无时间戳）。
- 证书页回读是 **POST** 200，不是 GET。host 类 page，content-type `text/html`，requestKind/contentPolicyType 均为 document，path 模板 `/cert/{id}/psa`。与 `/fo/` **不同 path**（`/fo/` 为 `/cdn-cgi/{id}/h/b/fo/{id}/{id}/{id}`，xhr，`text/html`）。与更早的证书页 GET 403 同 path 模板，方法从 GET 改为 POST。
- 结论：clearance 名落地后，页面没有再发 fo、turnstile、eb 或已记录的 chains，下一跳就是同一证书 path 的 document POST（24ms 后）。本地已有同会话 `cf_clearance` 仍无证书页回读，缺口不在这段中间请求，而在把 clearance 消费成这次 document POST。chunk/第三方请求都在该 POST 的 startMs 之后。
