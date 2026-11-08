# fo response extract

- case: psa-cf-5s-shield-20260815
- sourceRun (browser): rt_20260928075623_d3a207a25f
- materialRun checked: rt_20260928061614_ee71af43b2 counts={'D:\\reverse_ENV\\workspace\\psa_solve\\challenge-material\\rt_20260928061614_ee71af43b2\\raw\\http_packet': 0, 'D:\\reverse_ENV\\workspace\\psa_solve\\evidence\\web\\ruyitrace\\rt_20260928061614_ee71af43b2\\raw\\http_packet': 4}
- found: 4 POST /cdn-cgi/challenge-platform/*/fo/ responses with body
- status sequence: [200, 200, 200, 200]
- bodyBytes sequence: [106880, 798124, 6620, 3792]
- sha256: ['dddfd899ec3ae265023097e79bfb616506da8d736090941b69a2bde0a2532441', 'aa2c4e24b77ea46a3c9298433a6f6cfb8af5df53d0066c977386582a5bbafb36', '0653f37f6edbfb23a8e1e754c46172336737885a820068849e1aee6c816d2988', 'b4044fccfe2d7d743aec90ee75989ad199f0233672c785eaab65d700cca342cd']
- headerNames per response: [['date', 'content-type', 'cf-chl-gen', 'timing-allow-origin', 'set-cookie', 'content-encoding', 'server', 'cf-ray', 'alt-svc', 'X-Firefox-Spdy'], ['content-type', 'cf-chl-gen', 'timing-allow-origin', 'content-encoding', 'date', 'server', 'priority', 'cf-ray', 'alt-svc', 'server-timing'], ['cf-chl-out-s', 'cf-chl-out', 'content-type', 'timing-allow-origin', 'content-encoding', 'date', 'server', 'priority', 'cf-ray', 'alt-svc', 'server-timing'], ['cf-chl-out', 'content-type', 'date', 'cf-chl-out-s', 'timing-allow-origin', 'content-encoding', 'set-cookie', 'set-cookie', 'server', 'priority', 'cf-ray', 'alt-svc', 'server-timing']]
- setCookieNames per response: [['__cf_bm'], [], [], ['cf_clearance', '__cf_bm']]
- body files newly created: 4 under diagnostics/fo-responses/
- reused existing body paths: 0
- note: these are captured HTTP /fo/ responses for offline experiment; NOT serverAccepted.

## Replay

- 两次离线运行把 manifest 按序交给资源处理器。只用到第 1 条：status 200，responseBytes 106880。`foReplay=4`，`foReplayServed=1`。
- 请求仍是 POST，同一路径模板，header 名 `cf-chl`、`cf-chl-ra`，body 2306 字节。sha256 两次不同。
- 页面随后抛 `InvalidCharacterError: String contains an invalid character`。script 站点是 eval line 1 column 287。没有第 2 次 `/fo/`，eb=0。
- 不回放时同一页面会连发 3 次。回放把链截断了。异会话响应不能当作本次求解结果。
- 默认 `bridge-input.json` 不再指向 manifest。代码仍保留 `foResponseManifest`，需要时才打开。
- 不是 serverAccepted。web-case 仍是 patching。

