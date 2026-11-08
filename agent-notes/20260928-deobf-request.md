# 2026-09-28 orchestrate 外部边界

Case: `psa-cf-5s-shield-20260815`. 源未执行。没有 opcode trace，没有 `--trace`。

## Gate

- Profile: `ast-safe`. `next_skill`: `web-ast-deobfuscation`. Claim: `transform-only`.
- Gate: `agent-notes/20260928-deobf-gate.json`. 源 sha256/16 `aa2b09a484f556d1`，238694 bytes。
- Marker 里另有 `bytecode_container`、`dispatch_switch`、`function_constructor`，以及 `crypto_random` / `text_codec`。没有 opcode fixture，profile 没有升到 `jsvm-verifiable`。本轮不恢复 opcode，不拆 handler。
- 只跑了 safe AST（`references/safe-ast.md`）。产物在 `agent-notes/deobf-ast/`：`output.js`、`parse-before.json`、`parse-after.json`（均 `passed=true`）、`transform-report.json`。
- Pass：`normalize-computed-properties` 0，`fold-static-literals` 18，`prune-constant-branches` 0。`unsafe_passes=[]`，`target_code_executed=false`。源 JS 未覆盖。18 次折叠没有解开请求路径或字段绑定。

## 请求链

脚本里没有字面量 `orchestrate` 或 `jsd`。页面（只取字段与路径模板）内联脚本加载：

`/cdn-cgi/{id}/h/b/orchestrate/chl_page/v1?ray={id}`

ray 原值不记录。这是本文件的加载入口，不是本文件发出的请求。

字符串表里有一条路径前缀，长度 30，等于 `/cdn-cgi/challenge-platform/h/`。另外一条可读的 challenge-platform 只出现在说明链接 `%2Fcdn-cgi%2Fchallenge-platform%2Fhelp`，不是 fo/eb。

fo 模板字面量 2 处，eb 1 处，形状相同：

`/fo/2124045040:1790575218:{segment}`
`/eb/2124045040:1790575218:{segment}`

`{segment}` 长度 43，字符集是大小写字母、数字、`-`、`/`，其中恰好一个 `/`，没有 `=`。前面再拼一个间接属性（可能是上面的 `/h/` 前缀，索引被混淆，不能当成已证明的拼接）。冒号是源码里的分隔符。浏览器包路径类是斜杠形式 `/cdn-cgi/challenge-platform/h/b/fo/{id}/{id}/{id}`。源码里看不到 `:` 换成 `/` 的赋值，所以这三处字面量还不能写成已确认的线上 URL。

调用顺序：eb 在 `case "6"`，下一 case 组对象，再下一 case 把对象送进间接调用；case 号不是执行序。两处 fo 在不同函数，其中一处前面有 `1e3` 的定时注册和 `!iU()` 守卫。谁先谁后未知。jsd 不在本文件。

字符串表另有 `XMLHttpRequest`、`setRequestHeader`、`send`、`onreadystatechange`、`ontimeout`、`readyState`、`getResponseHeader`、`content-type`、`POST`、`application/json`。它们和 fo/eb 字面量不在同一语句，不能判断方法、header 或 body 绑到哪一条模板。

## 不透明参数

不还原密钥，不贴密文，不做逐字节对比。

| 载荷 | 容器 | 可见编码 | 喂给 |
|---|---|---|---|
| fo 对象 22 个混淆键（`EMLf9` 等） | 紧挨第一条 `/fo/` 字面量的对象，不是 query 字面量 | 值里有 `0`/`1`、空串、`undefined`、`JSON.stringify([])`，其余是间接读取 | 推测给该 `/fo/` 模板；header/body 未证 |
| eb 对象 6 个混淆键（`GKnll5`、`kGUg5`、`uEcTc9`、`uNkxd2`、`jKQT4`、`dwpd8`） | `case "7"` 的对象，内层还有一个键被间接解码的对象 | 未看到 base64/hex 字面量直接写在这些键上 | 紧挨 `/eb/` 那次间接发送；线上 eb=0 |
| 路径 `{segment}` | URL 模板中段 | 长度 43，含一个 `/`，无 padding `=` | 两处 `/fo/` 与一处 `/eb/` |
| 4 条纯 base64 形态字面量；49 条含 `$` 的不透明字面量 | 独立字符串 | base64 形态或 `$` 分段；无 hex 字面量 | 未知，未贴值 |
| `atob` → `Uint8Array`；`TextEncoder`；`crypto` 填 `Uint8Array` 再送进 `BigInt` | 与 URL 模板分离的函数 | base64 解码 / UTF-8 / CSPRNG | 未证明进入 fo 或 eb |
| 页面 `_cf_chl_opt` 键：`cFPWv` `cH` `cITimeS` `cN` `cRay` `cTplB` `cTplC` `cTplO` `cTplV` `cType` `cUPMDTk` `cvId` `cZone` `fa` `md` `mdrd` | 页面对象；脚本里有 `window._cf_chl_opt` | 原值不记录 | 这些名字也在 orchestrate 字符串表中各至少一次，但没有可见赋值把它们送进 fo/eb |

字符串表还有 `cf-chl`、`cf-chl-ra`、`cf_chl_rc_i`。没有可见的 header 赋值。

## 和浏览器事实对齐

指针：`evidence/web/ruyitrace/rt_20260928061614_ee71af43b2/evidence-run.json`。计数沿用同 run 的 formal 笔记，不重贴包体：orchestrate=2，fo=8，eb=0，jsd/oneshot=2。主文档 GET 403，`cf-mitigated=challenge` 一次。这只说明挑战窗出现，不是求解成功。

本地 RuyiDOM（`20260928-ruyidom-fresh.md`）在 eval line 2 抛 `TypeError: can't access property "call", KP is undefined`。stderr `/fo/`=0，`/eb/`=0。因此下面几项被这次执行失败挡住：

- 两处 fo 字面量哪一处真正发出，以及冒号模板是否变成浏览器里的斜杠路径
- fo 对象 22 个混淆键哪一个进 query、body 或 header
- `content-type` / `POST` / `application/json` 是否用在 fo
- `_cf_chl_opt` 各字段是否被读进该对象
- `atob`、`TextEncoder`、`crypto`/`BigInt` 的输出是否进 fo
- eb 分支为何在浏览器里是 0：脚本里有模板，但本地在 KP.call 已死，看不到分支被跳过还是没跑到

缺 opcode fixture。下一步有界实验是补 VM opcode trace，而不是再跑同一套 safe AST。
