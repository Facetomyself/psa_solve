# 2026-09-28 RuyiDOM 页面加载桥

Case: `psa-cf-5s-shield-20260815`. 没有 safe AST，没有 opcode，没有新 RuyiTrace，没有 `serverAccepted`。web-case 仍是 `patching`。

## 引擎通道

- `search_tool` 的本会话工具表里没有 `ruyidom_runtime_status` / `ruyidom_health` / `ruyidom_run`。已连接的是 ida-multi-mcp、ruyitrace-mcp、serena、v8trace-mcp。没有假装走 MCP。
- Fallback：同一引擎 CLI `tools/ruyidom/run.ps1`。未传 `-AllowNetwork`（`MOZ_DISABLE_NONLOCAL_CONNECTIONS=1`）。
- Doctor `-Cleanup -Json` 后 `ok=true`，fatal 空。锁定 hash 与 `mcp/ruyidom-mcp/README.md` 一致：ruyijs `c09e9a5379860a84…`，xul `96be85ca4ed47d4e…`，plugin-container `fb92120a0c164d72…`，mozglue `5b7e55bd4340f509…`。marker 在。
- Runner：`diagnostics/ruyidom_bridge.js`。输入 `-InputFile`。没有注入 `runtime/code.js`，没有改 orchestrate 字节码，没有定义 `window.KP`。

## 加载方式

- 挑战页 HTML 原样进文档（不删 CSP，不预包 history）。`url` 用材料里的 cert 文档身份。
- 页面内联脚本 `createElement` 后写 `src`。本地只应答这条路径模板的 script GET：`/cdn-cgi/challenge-platform/h/b/orchestrate/chl_page/v1`，body 来自落盘 orchestrate（sha256/16 `aa2b09a484f556d1`，238694 bytes）。
- `blockUnmapped=true`。别的 URL 不回放页面、不把 orchestrate 塞给其它 script、不向 `www.psacard.com` 或 `challenges.cloudflare.com` 提交。
- 引擎仍用 `ruyidom.js` 的 script 资源 eval 执行已映射脚本。这是页面 `src` 赋值触发的，不是 about:blank 上把 orchestrate 当字符串从第 2 行 eval。

## 未补 history 的一轮

- exit `-2147483645`。stdout 0。trace：`diagnostics/bridge-run1.jsonl`。stderr：`diagnostics/bridge-run1-stderr.txt`。
- 顺序：script GET orchestrate 本地 served（body 0）→ `SecurityError: The operation is insecure.`（about:blank injectedScript line 2）→ image GET `/favicon.ico` blocked → script GET 路径模板 `/{id}/v0/b/{id}/api.js` blocked（长度≥8 的段被收成 `{id}`，host 未记）→ eval line 2 `TypeError: can't access property "call", KP is undefined`。
- 随后 FATAL 主机名只有 `www.psacard.com`，两行都没有路径。没有 `challenges.cloudflare.com`。进程在 print 前退出。fo=0，eb=0。没有 XHR/fetch，header 名没有出现。

这轮抛错前的外部宿主错误就是 `history.replaceState` 的 SecurityError。页面加载器在设置 script `src` 之后调用它；文档身份仍报 about:blank。浏览器材料里的页面脚本确实调用 replaceState。按双条件只补这一个。

## 只补 replaceState 的一轮

- `patchHistory=true`。只包 `history.replaceState`：原函数失败则返回 undefined。`toString` 为 native-like。没有包 `pushState`，没有造 `KP`。
- exit 0。stdout：`diagnostics/bridge-run2-stdout.txt`。trace：`diagnostics/bridge-run2.jsonl`。
- SecurityError 消失。没有 FATAL，没有对两个站点的提交。
- 同一条 orchestrate script GET 仍本地 served。favicon 与 `/{id}/v0/b/{id}/api.js` 仍 blocked，bodyBytes 0，sha256 空。
- 计数：orchestrate=1，fo=0，eb=0，jsd=0，other=2，served=1，blocked=2。
- 第一个也是唯一的页面错误仍是 eval line 2：`KP is undefined`。`headerLog=[]`。
- probe：`typeof window.KP === "undefined"`，`kpOwn=false`，`_cf_chl_opt` 是 object、32 键（页面初值 16 键，脚本在抛错前写过），scripts=3，path `/cert/{id}/psa`，search/hash 长度 0。值未记。
- stderr 在 KP 之后还有引擎模块 `SessionStoreFunctions.sys.mjs` 加载失败。那是引擎文件缺口，不是 window/document/navigator 上的挑战宿主 API，没有补。

## Turnstile script.src

- 浏览器材料里的 script GET 是 Turnstile `api.js`（响应 sha256/16 `76763bb46224400a`，86732 bytes）。上一轮本地 blocked 之后，改成按该 pathname 回放 body。库初始化抛 `TurnstileError`：找不到 src 匹配其 api.js 正则的 script 标签。
- 原因在资源加载器：映射响应会在 eval 前拿掉 `src`。`Mt()` 先看 `document.currentScript`（间接 eval 为 null），再看文档里已有标签的 `.src`。原生 getter 在属性被移除后返回空串，不会读 `data-ruyidom-src`。
- 补丁只做这一面：把捕获 URL 的惰性 script 放进 head，第一次静态改写不回 body，避免被内联掉 src；随后的同源 script GET 才回放 `turnstile-api.js`。`beforeParse` 在页面 realm 里包 `HTMLScriptElement.src`：原生值为空时返回 `data-ruyidom-src` 或 `data-ruyidom-mapped-src`。getter 与 `history.replaceState` 的 `toString` 都是 native-like。没有改 orchestrate，没有定义 `window.KP`。

## 补完 script.src 的两轮

- 两次都是 exit 0，未传 `-AllowNetwork`。stdout 摘要一致。
- 计数：orchestrate=1，fo=0，eb=0，jsd=0，other=4，blocked=2，served=3。
- wire：惰性 Turnstile script GET `/turnstile/v0/b/{id}/api.js` served=false；orchestrate GET served=true；同一 Turnstile 路径再 served=true；favicon blocked；扫描又一次 served=true。header 名空。bodyBytes 0（这些都是 GET）。没有 `/fo/` 或 `/eb/`。
- probe：`window.KP` undefined 且非自身属性。`_cf_chl_opt` 33 键。`window.turnstile` 是 object。turnstileTags=2。src getter toString 含 `[native code]`。path `/cert/{id}/psa`。
- 唯一页面错误仍是 `TypeError: can't access property "call", KP is undefined`。TurnstileError 没有了。stderr 仍有引擎 `SessionStoreFunctions.sys.mjs`，不是挑战宿主 API，没有补。

## KP

- 不是 `window.KP`：源里没有 `window.KP`，也没有 `function KP`。抛错是计算属性取到 undefined 后再读 `.call`。页面函数 `xdiN1` 被 sloppy IIFE 写到了非 Window 的全局上，Window 上没有这个函数。
- 没有造 `window.KP`，没有改 orchestrate。整段 `"use strict"` 能把赋值落到 `self`，但同步回合不再结束，已撤掉。
- 现在的宿主面是编排脚本前面的原型镜像：get 的 receiver 固定为 Window，方法调用在 this 是编排全局时改回 Window，set 同时定义到 Window 和接收者。`Function.prototype.toString` 仍指向原函数。补完后 `xdiN1` 和 turnstile onload 都在 Window 上，页面错误消失。

## /fo/

- 页面隔间里包了 XHR/fetch（chrome 隔间赋值会触发 Xray，已不再从 chrome 写原型）。另外只计数：Worker、iframe、`RTCPeerConnection`、`createOffer`、blob URL、`randomUUID`、`getEntries`、message 里是否出现 honk。这些计数器的 toString 是 native-like。
- 离线进程会因真实连到页面主机被直接杀掉。`http-on-modify-request` 里取消通道，只为把摘要打印出来。取消不是解题响应。
- 两次 exit 0，未传 `-AllowNetwork`。计数都是 orchestrate=1，fo=3，eb=0，jsd=0，other=4，blocked=5，served=3。`errors=[]`。
- 三次都是 POST `/cdn-cgi/challenge-platform/h/b/fo/{id}:{id}:{id}/{id}/{id}`。header 名：`cf-chl`、`cf-chl-ra`。body 各 2306 字节。served=false。
- 第一轮 sha256：`d76be5c737123058b5799a884ee1d361d657d8fd452336d950a8dd14367c98d8`、`9f8a0cca462c88346477589ddbd35d1e1130b9b5bb87bcde2568d079512d52a1`、`8a39df821962dd591ca960bd5ef600ba1df21e5ccb157d7ce14ba198cab82fd7`。
- 第二轮 sha256：`c8ffd67394973bd4bc99a848d9e35dc13aa5287ba71dddfe7c7fe73bc11b0bdb`、`23025faf2297af7b4cbe882fcf483acc27346622274071987622cbea1a232596`、`be058c32d2c92eddf5a262982c29c6397db0e1916da6784523e4ee0726a0f4e2`。两次对不齐，body 含动态字段。
- 探针两轮相同：`window.KP` undefined。onload 调用 2 次。Worker 1，iframe 1，blob URL 1，`randomUUID` 1，`getEntries` 1，`RTCPeerConnection` 1，`createOffer` 1 且未 settle，ICE 0，honk 0。`_cf_chl_opt` 36 键。path `/cert/{id}/psa`。
- 没有 serverAccepted。web-case 仍是 patching。`/fo/` 没有本地响应体，挑战还不能走完。

## 请求边界

| 轮 | 方法 | 路径模板 | header 名 | body | 处置 |
|---|---|---|---|---|---|
| 两轮 | GET | `/cdn-cgi/challenge-platform/h/b/orchestrate/chl_page/v1` | 无（script src，不是 XHR） | 0 | 本地 orchestrate |
| 两轮 | GET | `/favicon.ico` | 无 | 0 | blocked |
| 两轮 | GET | `/{id}/v0/b/{id}/api.js` | 无 | 0 | blocked |
| script.src 两轮 | GET | `/turnstile/v0/b/{id}/api.js` | 无 | 0 | 第一次 inert，之后本地 api.js |
| script.src 两轮 | — | `/fo/`、`/eb/` | — | — | 未出现 |
| 镜像之后两轮 | POST | `/cdn-cgi/challenge-platform/h/b/fo/{id}:{id}:{id}/{id}/{id}` | `cf-chl`、`cf-chl-ra` | 2306，sha256 每条不同 | served=false，未提交 |

没有 cookie、token、ray 全值或 body 原文。
