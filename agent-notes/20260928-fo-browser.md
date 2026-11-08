# 2026-09-28 /fo/：有头浏览器顺序 vs 本地探针

Case: `psa-cf-5s-shield-20260815`  
Browser run: `rt_20260928075623_d3a207a25f`（interactive 有头复看）  
Material run: `rt_20260928061614_ee71af43b2`（同序对照）  
Local: `agent-notes/20260928-ruyidom-bridge.md` `/fo/` 节  
不写 cookie/token/ray/query/body 原文、证书号或完整 fo URL。

## 1. 有头顺序

HTTP（`raw/http_packet`，按 meta.seq）：

| 序 | 方法 | 状态 | 路径类 | 宿主类 | 备注 |
|---|---|---|---|---|---|
| 1 | GET | 403 | `/cert/{id}/psa` | psa | challenge 页 |
| 2 | GET | 200 | `.../h/b/orchestrate/chl_page/v1` | psa | |
| 3 | GET | 200 | `/turnstile/v0/b/{id}/api.js` | cf | |
| 4 | POST | 200 | `.../h/b/fo/...` | psa | 响应 `text/plain`；无 `cf_clearance` 名 |
| 5 | GET | 200 | turnstile frame（`.../turnstile/f/...`） | cf | 第一次 fo 之后 |
| 6 | POST | 200 | `.../h/b/fo/...` | cf | `text/plain` |
| 7 | GET | 401 / 0 | `.../pat/...`、`.../i/...` | cf | fo 链中段 |
| 8 | POST | 200 | `.../h/b/fo/...` | cf | 响应变 `text/html` |
| 9 | POST | 200 | `.../h/b/fo/...` | psa | `text/html`；set-cookie **名**含 `cf_clearance` |
| 10 | POST | 200 | `/cert/{id}/psa` | psa | 回到证书页；无 challenge 头 |

- `/fo/`：**4** 次，全部 **200**。`eb`：**0**。`jsd/oneshot` 出现在证书页 **之后**，不是这次过关门槛。
- 材料 run `rt_20260928061614_ee71af43b2`：同样 cert GET 403 → fo×N 200（含 clearance 名）→ cert POST 200，`eb=0`。

第一次 `/fo/` **之前**的宿主调用（同页 domtrace，`createOffer`/`setLocalDescription` 与首次 fo `send` 同 pid，ts 序）：

1. `Crypto.randomUUID`
2. `Performance.getEntries`
3. `PerformanceObserver.observe`
4. `RTCPeerConnection.createDataChannel` → **`createOffer`** → iframe 尺寸/sandbox/`contentWindow`
5. **`setLocalDescription`（createOffer 已 settle）**
6. 然后才 `XMLHttpRequest` open/setRequestHeader/send 打向 `/fo/`

`honk` 消息命中：**0**。首次 fo 之前没有额外的「等 fo 响应再 createOffer」；settle 在 fo **之前**完成。

`/fo/` 响应之后页面还要什么（顺序事实，不是猜响应体）：

- 读 XHR 完成态（readyState/status/response 路径在 fo 200 之后出现）
- 再发后续 `/fo/`（跨 psa/cf 宿主），中间拉 turnstile frame，以及 cf 侧 `pat`/`i`
- 最后一次 fo 响应带 `cf_clearance` 名后，**POST 回证书页 200**
- **不需要** `eb`

## 2. 和本地探针的差异

本地（bridge，无网，`served=false`）：POST `/fo/` **×3**；header 名 `cf-chl`、`cf-chl-ra`；body 各 2306；`createOffer` 1 次 **未 settle**；Worker 1；iframe 1；honk 0；onload 2。

| 项 | 浏览器（相对第一次 fo） | 本地 |
|---|---|---|
| randomUUID / getEntries / PerformanceObserver | fo **之前**已发生 | 探针有计数（与 fo 同轮） |
| createOffer | fo **之前**调用且 **已 settle**（有 setLocalDescription） | 有调用，**未 settle**，但仍发出 fo×3 |
| iframe | fo 前已建 | 有 1 |
| Worker | 链上有 Worker 面 | 有 1 |
| honk | 0 | 0 |
| onload | （Turnstile 链） | 2 |
| `/fo/` | ×4 且 **200** | ×3 且 **served=false**（无响应体） |
| fo 后 | 更多 fo + frame + clearance 名 + 回证书页；eb=0 | 停在空响应，无后续链 |

已在 fo **之前**对齐到「能发 fo」的：UUID/performance/RTC/iframe 路径本地也能走到发 fo。  
fo **之后**才需要、本地还缺的：对 `/fo/` 的 **200 响应消费**（浏览器在空响应下不会进入后续 fo / clearance / 回证书页）。createOffer settle 是浏览器 fo 前事实，但不是本地「发不出 fo」的闸；本地已发出 fo。

## 3. 结论（下一刀）

**先补「/fo/ 响应」（本地资源映射给出可消费的 200），不要先补「iframe 上的 createOffer settle」。**

顺序证据：

1. 浏览器在第一次 fo **之前**就 settle 了 createOffer，随后才 send fo；本地 **未 settle 也能** send fo×3 → settle 不是当前「过不了 fo 边界」的阻塞闸。
2. 浏览器四次 fo 均为 200，且 fo 200 之后才继续 frame/后续 fo/`cf_clearance` 名/证书页 POST；本地三条 fo 全是 `served=false` → 链停在 **响应缺失**。
3. 两边 `eb=0`、`honk=0`；不要把 eb 或新 trace 当下一刀。现有 run 已有调用顺序。

不在此笔记猜测或伪造 fo 响应体内容；只认定闸门是「有响应可被页面读到」。

## 证据指针

- `evidence/web/ruyitrace/rt_20260928075623_d3a207a25f/raw/http_packet/`
- `evidence/web/ruyitrace/rt_20260928075623_d3a207a25f/raw/domtrace/`（主序 pid 与 fo send 同文件）
- `agent-notes/20260928-ruyitrace-silent.md`
- `agent-notes/20260928-ruyidom-bridge.md`（本地 /fo/）
- `analysis-progress.md` Current State（rt_20260928075623 条）
