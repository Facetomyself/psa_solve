# 2026-09-28 fresh RuyiDOM

Case: `psa-cf-5s-shield-20260815`

## 材料

- 来源 run：`rt_20260928061614_ee71af43b2`。新目录 `challenge-material/rt_20260928061614_ee71af43b2`。没有覆盖 `demo6-20260816-222208-3`。
- manifest 只记 sha256、字节数、sourceRunId、路径模板。
- challenge HTML：sha256/16 `030a1607fc7225a7`，5798 bytes，模板 `cert/{id}/psa`。packet sha256 与落盘一致，未截断。
- orchestrate：sha256/16 `aa2b09a484f556d1`，238694 bytes，模板 `{id}/{id}/h/b/orchestrate/{id}/v1`。packet sha256 与落盘一致，未截断。
- 对照 demo6 orchestrate `437c1820aeaaba6f`，227853 bytes。sha256 不同，不是同一份。

## 跑法

- CLI：`tools/ruyidom/run.ps1`。脚本：`diagnostics/ruyidom_runner.js`。
- `codeJsPath=diagnostics/NO_NODE_CODE_JS`（不存在）。没有注入 `runtime/code.js`。没有跑 `ruyidom_cf_shield_v1.js`。没有 `-AllowNetwork`。没有 cookie。`pumpMs=15000`。`challengeUrl` 只有站点 cert 路径，无 query。
- 没有新浏览器，没有新 capture。

## 观察

- exit `-2147483645`（与此前 `2147483651` 同一引擎退出码）。stdout 0 字节，没有 `{ok:...}`，wire 未落盘。
- fo 落盘：否（stderr `/fo/` = 0）。eb 落盘：否（stderr `/eb/` = 0）。
- 第一个 JS 错误：`ruyidom.js` eval line 2，`TypeError: can't access property "call", KP is undefined`。没有拆 VM。
- 随后 FATAL，按出现顺序：主机名 `challenges.cloudflare.com`，没有路径；主机名 `www.psacard.com`，没有路径。两行各重复一次。不能把主机名写成带 path 或 query 的 URL。
- 按约束停。没有放行全网。不能写 serverAccepted。web-case 仍是 `patching`。
