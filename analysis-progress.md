# Web Analysis Progress

Case: `psa-cf-5s-shield-20260815`

## Update Discipline

- Read this file before changing a runtime shim, local reproducer, resource mapping, request shape, or risk plan.
- Rewrite it after each evidence capture, single-variable experiment, material failure reclassification, or completed batch. Keep only the current truth.
- Record evidence pointers and redacted hashes only. Do not write raw Cookie, token, account, proxy, challenge material, or browser profile data here.

## Current State

- 2026-11-07：**状态迁移总览（详见 `docs/status-20261107.md`）**。① ruyijs 线生产化：`runtime/solve_ruyijs.py` + `scripts/demo6.py --solver ruyijs`，fresh-navigate ~12s 全链，clearance 跨引擎转移成立（curl_cffi firefox 同 IP+UA 复用 → 业务 200）。② Node 桥定性为 capture-only：同字节同插桩（消变体）下死于 FO r1 后第二层键控解码——atob 前 825 调用逐字节相同、VM switch 逐 opcode 同构，失败点是调用方 f8 第 4 次进入后无界自旋（yz 恒空、NaN 早退不触发；ruyijs 同函数 183 进 183 出）；浅层缺口（performance 条目/Observer）已修（759→825），剩余分歧在宿主读数值级且无 ground truth。本文件 2026-09~10 的单变量实验记录多数已被"变体轮换实锤"重新定性（跨会话材料不可混用，当时多轮在线对拍作废），读时注意。③ 静态 payload 组装链进行中：FO r1 body = 明文对象（24 键）→ v0 内部加密 → 3B→4 自定义 base64；alphabet 可静态提取（b0 隐藏器），CfReverse LZ 配方已证不适用（912 解包变体全败）。④ 调度器 `web_case.py next` 因 facts 键版本不匹配崩溃（ruyijsLiveEmit），待对齐。
- 2026-11-03：hold_challenge 停点记账。`firstDivergence=challenge-state`，`challengePhase=stuck`，`humanActionPending=false`。ruyijs `rj_20261102191503_7445d1cb` cert-document POST count=0；load_page 仍是 GET_403 5787B formTags=0。seq-14 POST /cert/ 200 是输出不是 load_page。验证链无新外部事实。离开三选一未走。证据 `evidence/hold-challenge-d8297755-20261103.json`。
- 2026-09-29：主线改由 `web_case.py next` 驱动。RuyiDOM CLI 在线对照已跑完：清关 cookie 名在，证书 document POST 不在。分类 `environment-gap`，`requestBoundaryAligned=false`，`experimentHygiene=stop-search`。工作记录在 `docs/web/`。不再枚举相邻宿主字段。这不是 serverAccepted。
- 2026-09-29：本轮停在落文档，没有再改桥接，也没有新开挑战。发行版 `User-Agent` 仍保留。内层钩子长度 16738。证书 document POST 没有出现，业务页没有回读 200。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。有头清关前 `DOMRect` 九组还没作为一次联合实验跑过：高/宽/左/上依次是 67.69999694824219/896/192/304（两次）、65/300/192/304、再两次 67.69999694824219/896/192/304、243.6999969482422/960/160/128、772/1280/0/0、842/1280/0/0、842/1280/0/0。稍后另有 `top` 304 和 `right` 1088。高、宽、左、右以前分开改过并已撤回，这一轮没有把它们合在一起再跑。
- 2026-09-29：发行版 `User-Agent` 保留。有头清关前的资源列表里没有传输大小 200 到 400 的条目，也没有名字长度超过 200 且传输约 3200 的条目。这两档分开拿掉都进不了表单。这次从同一组列表接口里同时拿掉。探针 `hx2` 是 1。结束采样是 `0,28340,2534,81330,0`，约 300 和约 3200 都不在。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 218。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。过滤已撤回。桥接回到只保留发行版 User-Agent 的基线。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头清关前的传输大小集合里没有 200 到 400 这一档。本地结束采样常常有约 300。这次从 `getEntries`、`getEntriesByType`、`getEntriesByName` 和观察者 `getEntries` 里拿掉这一档，不改计时。探针 `h3` 是 2。结束采样是 `0,28282,81344,0,3203`，约 300 不在了，约 3203 还在。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 218。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。过滤已撤回。桥接回到只保留发行版 User-Agent 的基线。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头清关前 `MessageEvent.source` 九次都是对象。只在原生值为空时改回窗口。探针 `srcN` 是 13，`src0` 是 0，返回值没有改。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 218。`forms` 仍是 0，没有证书 document POST。getter 已撤回。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。同一档 200 到 400 的过滤先跑过一轮，探针 `h3` 是 0，结束采样是 `0,28282,2534,81343,0,3204`，这一轮列表里没有 200 到 400。过滤没有被调用，不能当成这一档已经证伪。过滤当时已撤回。
- 2026-09-29：发行版 `User-Agent` 保留。有头名字长度 146 的那条在清关前读到 `duration` 177.83999999999992 和 `responseEnd` 1554.72。这两个数以前分开改过，这次只在名字长度 140 到 160 时一起返回。探针 `n146` 是 2。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 218。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。两个 getter 已撤回。桥接回到只保留发行版 User-Agent 的基线。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头 `head` 的第一个元素是 `TITLE`。这次不改星号列表，也不在解析后搬节点。预先放入文档自己的 `base`，让引擎不再往 `head` 开头插第二个；身份脚本改到页面自己的 `script` 前面。结束探针 `hf` 是 `5:84`，`bp` 是 72，`head` 首位已经是 `TITLE`，`base` 仍在 `head` 里。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 218。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。放置已撤回。桥接回到只保留发行版 User-Agent 的基线。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头清关前 `NodeIterator.nextNode` 会走到元素和文本。本地多出来的 `base` 和身份脚本仍在树上。只让 `nextNode` 跳过这两个节点，不改星号列表。探针 `nx` 是 2。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 218。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。包装已撤回。桥接回到只保留发行版 User-Agent 的基线。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。同一轮新挑战只记录 `document.currentScript`，不改返回值。有头清关前两次都是脚本元素，随后 `src` 类别是 `98:104`。本地 `csN` 是 2，`cs0` 是 0，标签类别 `6:83`，`src` 类别 `98:104`，对得上，没有改 getter。这一轮第二次解码首字节已经是 218。记录包装已撤。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头清关前 `document.querySelectorAll('*')` 的 `NodeList.length` 是 47。本地只记录时是 49、49。这一刀在构造这个列表时临时拿开引擎 `base` 和桥接身份脚本，列表返回后再放回。探针 `qf` 是 2，长度变成 47、47。外层变成 3488，解码链变成 3488→2616→1960，第二次解码首字节是 218。`tsC` 是 0，`forms` 仍是 0，没有证书 document POST，也没有业务页 200。包装已撤回。桥接回到只保留发行版 User-Agent 的基线。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头清关前 candidate 里有 `srflx`。本地这次已经有原生 `srflx`（`sawSx` 是 1）。只在还没看到原生 `srflx` 时补了 4 条文档用地址的 `srflx` 事件，不改已有 host 行。探针 `syn` 是 4，`synF` 是 0，`ice` 从 40 变成 44。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节仍是 89。正文首字节是 106。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。补事件已撤回。桥接回到只保留发行版 User-Agent 的基线。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头 TCP host candidate 的端口都是 `9`，本地被动行仍是五位端口。这次只把 `TCP` 行的端口改成 `9`，不改 `tcptype`。探针 `p9` 是 20。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节仍是 89。正文首字节是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。桥接回到只保留发行版 User-Agent 的基线。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。2534 那条计时撤回之后，有头清关前下一批读取是 `setLocalDescription` 和 candidate。有头 10 段 host 行的 `tcptype` 值长度是 6（`active`），本地还会出现长度 7（`passive`）。地址改成 mDNS、host 改成 srflx 都已经撤回，这次只把 host 行的 `passive` 改成 `active`。探针 `tp` 是 20。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节仍是 89。正文首字节变成 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。桥接回到只保留发行版 User-Agent 的基线。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头名字长度 35、传输大小 2534 那条在清关前读到 `responseStart` 703.3（两次）、`requestStart` 620.2、`responseEnd` 703.34、`duration` 242.78000000000003。传输大小和 `encodedBodySize` 2234 本地已经一致，这次不改。只在名字长度 30 到 45 且原生传输大小 2400 到 2700 时一起返回这四个数。探针 `n35` 是 5，结束采样仍有 2534。外层变成 3488，解码链变成 3488→2616→1960，第二次解码首字节仍是 89。`tsC` 是 0，`forms` 仍是 0，没有证书 document POST，也没有业务页 200。四个 getter 已撤回。桥接回到只保留发行版 User-Agent 的基线。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。只读记录显示文档走查在 9 次 `SCRIPT` 之后才是 `4:72,4:72,4:66`。这一刀只在第一次读到 `HTML` 时把 `TITLE` 放到 `head` 首位，并把 `BASE` 留在末尾。探针 `bm` 是 1。记录末尾仍是 `4:72,4:72,4:66`，第三个还是 `BASE`。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 89。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。桥接回到只保留发行版 User-Agent 的基线。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。只记录 `tagName` 返回类，不改节点。探针 `tgN` 是 16。前 9 次是 `SCRIPT`，发生在文档走查之前，桥接的 `appendChild` 包装也会读这个属性。其后是 `4:72,4:72,4:66,6:83,5:84,4:77,4:77`。有头清关前的走查是 `4:72,4:72,5:84,4:77,...`，本地第三个仍是 `BASE`。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 89。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。记录 getter 已撤回。桥接回到只保留发行版 User-Agent 的基线。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。上一刀在解析期移动 `BASE` 后，结束顺序第三个仍是 `SCRIPT`。这一刀改到页面第一次读 `tagName` 时，把 `TITLE` 放到 `head` 首位，并把 `BASE` 留在末尾。探针 `bm` 是 1。记录到的前 12 次返回是 `5:84,5:84,4:66,4:66,4:66,6:83` 及后续 `SCRIPT`，不是有头从 `4:72,4:72,5:84` 开始的走查。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 89。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。`tagName` getter 已撤回。桥接回到只保留发行版 User-Agent 的基线。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头清关前 `tagName` 走查的前三个类是 `4:72,4:72,5:84`，离线解析第三个节点是引擎插在 `head` 开头的 `BASE`（`4:66`）。这次不删 `BASE`，只在 `DOMContentLoaded` 之前把它挂到父节点末尾。探针 `bm` 是 1，结束时前八个类是 `4:72,4:72,6:83,5:84,4:77,4:77,4:77,4:77`，第三个仍是 `SCRIPT` 不是 `TITLE`。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 89。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。观察器已撤回。桥接回到只保留发行版 User-Agent 的基线。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头名字长度 98、传输大小 28396 那条在清关前读到 `duration` 423.22000000000014、`responseStart` 1115.3599999999999、`requestStart` 1005.72、`responseEnd` 1117.8800000000001、`transferSize` 28396、`encodedBodySize` 28096。这六个值以前分开改过。这次只在名字长度 90 到 120 且原生传输大小 2 万到 4 万时一起返回。探针 `n28j` 是 7，结束采样第二条是 28396。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 89。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。六个 getter 已撤回。桥接回到只保留发行版 User-Agent 的基线。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头页面脚本在清关前读了一次 `window.windowGlobalChild`，接着读到 `innerWindowId`。本地安全文档上没有这个属性。只在页面 `Window.prototype` 上补了这个对象。探针 `wg` 是 0，页面没有调用这个 getter。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 101。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。补丁已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头导航条目在清关前读到 `responseStart` 406.95999999999998、`requestStart` 331.39999999999998、`responseEnd` 408.07999999999998、`transferSize` 3683、`encodedBodySize` 3383。早期 `duration` 两边都是 0，这次不改。只在 `entryType===navigation` 时一起返回这五个数。探针 `navJ` 是 6，结束采样第一条是 3683。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 101。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。五个 getter 已撤回。桥接回到只保留发行版 User-Agent 的基线。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头清关前的资源列表里没有名字长度超过 200、传输大小约 3200 的条目，本地结束采样一直有这一条。这次只从 `getEntries`、`getEntriesByType`、`getEntriesByName` 和观察者的 `getEntries` 里拿掉它。探针 `hx` 是 1，结束采样是 `0,28282,300,81250,0`，约 3200 那条不在了。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 101。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。过滤已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头名字长度 268、传输大小 81235 那条在清关前读到 `duration` 123.13999999999999、`responseStart` 940.62、`requestStart` 849.70000000000005、`responseEnd` 961.96000000000004、`transferSize` 81235、`encodedBodySize` 80935。这六个值以前分开改过，这次只在名字长度超过 200 且原生传输大小 7 万到 9 万时一起返回。探针 `n268` 是 7，结束采样是 `0,28340,300,81235,0,3206`，约 3200 的长名条目还在。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 101。`tsC` 是 1，`forms` 仍是 0，没有证书 document POST，也没有业务页 200。六个 getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头名字长度 99 那一条在清关前连续读到 `responseStart` 582.24000000000001、`requestStart` 487.92000000000002、`responseEnd` 648.51999999999998、`duration` 190.24000000000001、`transferSize` 83242、`encodedBodySize` 82942。这次只在名字长度 90 到 120 上同时返回这六个数。探针 `n98j` 是 7，结束采样第二条变成 83242，约 8.1 万那条仍在。外层是 3488，解码链是 3488→2616→1960，第二次解码首字节是 101。`tsC` 是 0，`forms` 仍是 0，没有证书 document POST，也没有业务页 200。六个 getter 已一起撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头名字长度 35、传输大小 2534 那条的 `duration` 原值是 242.78000000000003。先前改过的是另一条名字长度 35、传输大小 0 的 26.479999999999905。这一刀只在名字长度 30 到 45 且传输大小 2400 到 2700 时返回 242.78000000000003。探针 `d35` 是 0，结束采样是 `0,28282,300,81246,0,3205`，没有 2534 这一档，返回值没有改到。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 101。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头导航 `duration` 第一次是 0，清关前第二次是 1727.3800000000001。只在第二次且原值小于 1 时返回这个数。探针 `navD` 是 `1:0`，本地只读了一次，返回值没有改到。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 101。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头清关前 `decodedBodySize` 的直接读取次数是 0，名字长度 99 那一窗也没有这个字段。没有插入 getter。名字长度 90 到 120 上已经证伪的六个数值不变。先前 86732 是另一条资源的 `toJSON`，探针曾是 0。没有新开把 86732 套到这一档的实验。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头名字长度 99 的 `encodedBodySize` 是 82942。只改名字长度 90 到 120，不改 `transferSize`。探针 `n98b` 是 1，结束采样传输大小仍约 28282。这一轮外层是 3488，解码链是 3488→2616→1960，第二次解码首字节是 101。`tsC` 是 0，`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头名字长度 99 的 `duration` 原值是 190.24000000000001。只改名字长度 90 到 120，不改 `transferSize`。探针 `n98d` 是 1，结束采样仍约 28256。正文首字节变成 110。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 101，仍不是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头名字长度 99 的 `responseEnd` 原值是 648.51999999999998。只改名字长度 90 到 120，不改 `transferSize`。探针 `n98e` 是 1，结束采样仍约 28340。正文首字节变成 90。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节从 159 变成 101，仍不是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头名字长度 99 的 `requestStart` 原值是 487.92000000000002。只改名字长度 90 到 120，不改 `transferSize`。探针 `n98q` 是 1，结束采样仍是约 28340。正文首字节变成 113。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 159。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。只读日志里名字长度约 98 的脚本才是有头名字长度 99 那条。只把这一档的 `transferSize` 改成 83242，约 8.1 万的另一条不动。探针 `n98` 是 1，结束采样是 `0,83242,300,81342,0,3202`。正文首字节变成 116。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 159。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头名字长度 99 的 `responseStart` 原值是 582.24000000000001。只改名字长度 90 到 120。探针 `n98` 是 2。正文首字节变成 81。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 159。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。只读插桩记下清关前资源计时：字段、名字长度、首码点、原生数值，返回值不变。本地导航条目名字长度 8，`responseStart`/`requestStart`/`responseEnd`/`duration`/`transferSize`/`encodedBodySize` 都是 0。名字长度 98 的脚本传输大小约 2.8 万，不是有头名字长度 99 那条的 83242。名字长度 267 的传输大小约 8.1 万。名字长度 146 的 `responseStart`、`requestStart`、`transferSize`、`encodedBodySize` 已是 0。第二次解码首字节是 159。`forms` 仍是 0。没有证书 document POST。插桩已撤。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头导航 `responseStart` 原值是 406.95999999999998，本地是 0。只在 `entryType===navigation` 且原值是 0 时返回这个数。探针 `navRs` 是 2。正文首字节变成 65。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 159。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头导航 `responseEnd` 原值是 408.07999999999998，本地是 0。只改导航条目。探针 `navRe` 是 1。正文首字节变成 103。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 159。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头导航 `transferSize` 是 3683，本地是 0。只改导航条目，不改名字长度 146 的 0。探针 `navTz` 是 1，结束采样第一条是 3683。正文首字节变成 88。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 159。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头这条名字长度 146、传输大小 0 的资源，`responseEnd` 是 1554.72。只改名字长度 100 到 200 且传输为 0 的 `responseEnd`，不改它的 `duration`。探针 `re146` 是 1，名字长度 146。结束采样仍有 2534 和 3204。正文首字节变成 45。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 159，仍不是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头在清关前还读过一条名字长度 146、传输大小 0 的资源，`duration` 是 177.83999999999992。只改名字长度 100 到 200 且传输大小为 0 的 `duration`。探针 `d146` 是 1，名字长度 146。结束采样仍有 2534 和 3204。正文首字节变成 55。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 159，仍不是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头名字长度 35 的资源 `transferSize` 是 0。上一刀把 2000 到 4000 都改成 0，约 3202 也被改了。这一刀只改 2400 到 2700。探针 `ftz` 是 1，结束采样里 2534 变成 0，3203 还在。正文首字节变成 48。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 159，仍不是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头名字长度 35 的资源 `requestStart` 是 726.44。只改传输大小 2400 到 2700 这一档。探针 `frq` 是 1。结束采样仍有 2534 和 3202。正文首字节变成 51。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 159，仍不是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头名字长度 35 的资源 `responseEnd` 是 752.92。只改传输大小 2400 到 2700 这一档。探针 `fre` 是 1。结束采样仍有 2534 和 3201。正文首字节变成 55。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 159，仍不是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头名字长度 35 的资源 `responseStart` 是 726.44，读了两次。只改传输大小 2400 到 2700 这一档。探针 `frs` 是 2。结束采样仍有 2534 和 3204。正文首字节变成 78。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 159，仍不是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头名字长度 35 的资源 `encodedBodySize` 是 2234。只在传输大小 2400 到 2700 且原值不是 2234 时改。探针 `feb` 是 0，返回值没有改到。结束采样仍是 2534 这一档。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 159。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头名字长度 35 的资源 `duration` 原值是 26.479999999999905。只改传输大小 2400 到 2700 这一档，不改约 3200 的长名条目。探针 `fdu` 是 1。结束采样仍有 2534 和 3205。正文首字节变成 121。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 159，仍不是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头名字长度 35 的资源 `transferSize` 是 0，本地同档约 2534。只把传输大小 2000 到 4000 的 getter 改成 0。探针 `ftz` 是 2，结束采样里约 2534 和约 3202 都变成 0。正文首字节变成 83。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 159，仍不是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头导航条目的 `encodedBodySize` 是 3383。只在 `entryType===navigation` 时改成 3383。探针 `neb` 是 1。结束采样第一条仍是 0。正文首字节变成 80。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 159，仍不是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头这条大体积长名脚本的 `duration` 原值是 123.13999999999999，不是四舍五入后的 123.14。只改名字长度超过 200 且传输大小在 7 万到 9 万的那条。探针 `ndu` 是 1，名字长度 267。结束采样大条目是 81305，约 3203 的条目还在。正文首字节变成 70。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节仍是 159，不是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。上一刀把所有长名的 `duration` 都改成 123.14，连约 3200 字节的长名条目也改了。这一刀只改名字长度超过 200 且 `transferSize` 在 7 万到 9 万的那条。探针 `ndu` 是 1，名字长度 267。结束采样大条目是 81363，约 3201 的条目还在。正文首字节变成 88。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 159，仍不是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头在清关前把名字长度 268、传输大小 81235 那条脚本的 `encodedBodySize` 读成 80935。只改 `name.length>200` 且编码体积在 7 万到 9 万的那一档。探针 `neb` 是 1，名字长度 267。结束采样的大条目仍是 81351，约 3204 的长名条目没有被改写。正文首字节变成 83。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 159，仍不是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头在清关前把名字长度 268 那条脚本的 `transferSize` 读成 81235。只改 `name.length>200` 且原值不是 81235 的 `transferSize`。探针 `ntz` 是 2，名字长度都是 267。结束采样出现两个 81235，原先约 3202 的长名条目也被改成 81235。正文首字节变成 68。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 159，仍不是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头在清关前把名字长度 268、传输大小 81235 那条脚本的 `duration` 读成 123.14。只改 `name.length>200` 的 `duration`。探针 `ndu` 是 2，名字长度是 267、267，结束采样的大条目是 81355，正文首字节变成 80。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节从 250 变成 159，仍不是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头在清关前把名字长度 268、传输大小 81235 那条脚本的 `responseEnd` 读成 961.96。只改 `name.length>200` 的 `responseEnd`。探针 `nre` 是 2，结束采样的大条目是 81185，正文首字节变成 65。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 250，仍不是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头在清关前把名字长度 268、传输大小 81235 那条脚本的 `requestStart` 读成 849.7。只改 `name.length>200` 的 `requestStart`。探针 `nrq` 是 2，结束采样的大条目是 81174，正文首字节变成 104。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 250，仍不是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头在清关前把名字长度 268、传输大小 81235 那条脚本的 `responseStart` 读成 940.62。只改 `name.length>200` 的 `responseStart`，不改名字长度 99 的 orchestrate。探针 `nrs` 是 4，结束采样的大条目是 81191，正文首字节变成 107。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 250，仍不是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头在清关前把这条大脚本的 `transferSize` 读成 83242。只把原生传输大小 7 万到 9 万的 getter 改成 83242，不改约 2.8 万那条。探针 `ltz` 是 1，结束采样的大条目是 83242，正文首字节变成 84。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 250，仍不是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头在清关前把传输大小 83242 那条资源的 `encodedBodySize` 读成 82942。只把传输大小 7 万到 9 万这一档的 `encodedBodySize` 改成 82942。探针 `leb` 是 1，结束采样的大条目是 80577，正文首字节变成 75。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 250，仍不是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头在清关前把传输大小 83242 那条资源的 `requestStart` 读成 487.92。只把传输大小 7 万到 9 万这一档的 `requestStart` 改成 487.92。探针 `lrq` 是 1，结束采样的大条目是 81341，正文首字节变成 57。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 250，仍不是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头在清关前把传输大小 83242 那条资源的 `responseStart` 读成 582.24。只把传输大小 7 万到 9 万这一档的 `responseStart` 改成 582.24。探针 `lrs` 是 2，结束采样的大条目是 80296，正文首字节变成 81。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 250，仍不是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头在清关前把传输大小 83242 那条资源的 `responseEnd` 读成 648.52。只把传输大小 7 万到 9 万这一档的 `responseEnd` 改成 648.52。探针 `lrz` 是 1，结束采样的大条目是 80484，正文首字节变成 88。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 250，仍不是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头在清关前把传输大小 83242 那条资源的 `duration` 读成 190.24。只把传输大小 7 万到 9 万这一档的 `duration` 改成 190.24，不改约 2.8 万那条。探针 `ldz` 是 1，结束采样的大条目是 81325，正文首字节变成 54。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 250，仍不是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头清关前没有直接读 `connectStart`。只在传输大小约 2.8 万的条目上把 `connectStart` getter 改成 746.32。探针 `csz` 是 0，返回值没有改到。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 250，仍不是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头这条脚本资源 `toJSON` 里的 `decodedBodySize` 是 86732。只在传输大小约 2.8 万的条目上把 `decodedBodySize` getter 改成 86732。探针 `dbz` 是 0，返回值没有改到。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 250，仍不是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头这条脚本资源的 `requestStart` getter 是 1005.72。只在传输大小约 2.8 万的条目上把 `requestStart` getter 改成 1005.72。探针 `rqz` 是 1，传输采样仍是 28282 这一档，正文首字节是 88。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 250，仍不是 85。`forms` 仍是 0，没有证书 document POST，也没有业务页 200。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头这条脚本资源的 `responseStart` getter 是 1115.36。只在传输大小约 2.8 万的条目上把 `responseStart` getter 改成 1115.36，不改 `transferSize`、`encodedBodySize`、`duration`、`responseEnd`。探针 `rsz` 是 2，传输采样仍是 28340 这一档，正文首字节是 98。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 250，仍不是 85。`forms` 仍是 0，没有证书 document POST。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头这条脚本资源的 `responseEnd` getter 是 1117.88。只在传输大小约 2.8 万的条目上把 `responseEnd` getter 改成 1117.88，不改 `transferSize`、`encodedBodySize`、`duration`。探针 `rez` 是 1，传输采样仍是 28340 这一档，正文首字节是 111。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 250，仍不是 85。`forms` 仍是 0，没有证书 document POST。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头这条脚本资源的 `duration` getter 是 423.22。只在传输大小约 2.8 万的条目上把 `duration` getter 改成 423.22，不改 `transferSize` 和 `encodedBodySize`。探针 `duz` 是 1，传输采样仍是 28282 这一档，正文首字节是 83。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 250，仍不是 85。`forms` 仍是 0，没有证书 document POST。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头这条脚本资源的 `encodedBodySize` getter 是 28096，本地同档约 28040。只把 27000 到 29000 这一档改成 28096，不改 `transferSize`。探针 `ebz` 是 1，传输采样仍是 28340 这一档，正文首字节是 81。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 250，仍不是 85。`forms` 仍是 0，没有证书 document POST。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头对传输大小约 28396 的脚本资源直接读 `transferSize` getter，本地同档约 28340。只把这个区间的 getter 改成 28396，不改 `toJSON`。探针 `tsz` 是 1，结束采样含 28396，正文首字节变成 52。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节从 167 变成 250，仍不是 85。`forms` 仍是 0，没有证书 document POST。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头脚本资源 `toJSON` 的 `requestStart` 是 1005.72。只改这条返回值的 `requestStart`。探针 `rq` 是 1，调用 1 次，正文首字节变成 120。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节仍是 167。`forms` 仍是 0，没有证书 document POST。包装已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头脚本资源 `toJSON` 的 `responseStart` 是 1115.36。只改这条返回值的 `responseStart`。探针 `rs` 是 1，调用 1 次，正文首字节变成 66。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节仍是 167。`forms` 仍是 0，没有证书 document POST。包装已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头脚本资源 `toJSON` 的 `nextHopProtocol` 是 `h2`。只在这条返回值不是 `h2` 时改。调用 1 次，改写 0 次，本地已经是 `h2`。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节仍是 167。`forms` 仍是 0，没有证书 document POST。包装已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头脚本资源 `toJSON` 的 `contentType` 是 `application/javascript`。只在这条返回值不是该类型时改。调用 1 次，改写 0 次，本地已经是这个类型。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节仍是 167。`forms` 仍是 0，没有证书 document POST。包装已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头脚本资源 `toJSON` 的 `initiatorType` 是 `script`。只在这条返回值不是 `script` 时改。调用 1 次，改写 0 次，本地已经是 `script`。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节仍是 167。`forms` 仍是 0，没有证书 document POST。包装已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头脚本资源 `toJSON` 的 `responseEnd` 是 1117.88。只改这条返回值的 `responseEnd`。探针 `re` 是 1，调用 1 次，正文首字节变成 112。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节仍是 167。`forms` 仍是 0，没有证书 document POST。包装已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头脚本资源 `toJSON` 的 `decodedBodySize` 是 86732。只改这条返回值的 `decodedBodySize`。探针 `dec` 是 0，返回值没有改到。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节仍是 167。`forms` 仍是 0，没有证书 document POST。包装已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头脚本资源 `toJSON` 的 `encodedBodySize` 是 28096。只改这条返回值的 `encodedBodySize`。探针 `enc` 是 1，正文首字节变成 118。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节仍是 167。`forms` 仍是 0，没有证书 document POST。包装已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头脚本资源 `toJSON` 的 `transferSize` 是 28396。只改这条返回值的 `transferSize`。探针 `tx` 是 1，正文首字节变成 86。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节仍是 167。`forms` 仍是 0，没有证书 document POST。包装已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头对传输大小约 28396 的资源调用 `toJSON`，`duration` 是 423.22。去掉上次「小于 200 才改」的限制后，这次调用 1 次并改了返回值。正文首字节变成 99。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节仍是 167。`forms` 仍是 0，没有证书 document POST。包装已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头清关前读到的 candidate 是 12 段、带 `raddr`/`rport` 的 srflx。只把本地 `typ host` 行改成同样的 12 段形状。探针 `cs` 是 60，段数是 12，正文首字节变成 106。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节仍是 167。`forms` 仍是 0，没有证书 document POST。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头在清关前把 `document.scripts` 的长度读成 3。桥接的 realm 脚本和 turnstile 标签在页面脚本之前从树上拆掉，`BASE` 留着，长度 getter 仍返回真实长度。页面第一次读到的长度是 3，结束时脚本数也是 3，turnstile 标签仍是 1。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节仍是 167。`forms` 仍是 0，没有证书 document POST。拆节点和读取探针已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头在清关前调用 `Function.toString`，返回长度是 37 或 38。本地包装只在 `Function.prototype.toString` 命中自己包过的函数时改回同样的 native 文本。探针命中 0。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节仍是 167。`forms` 仍是 0，没有证书 document POST。包装已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。上一轮替换没有改到返回值。这次在 `RTCIceCandidate.candidate` 的 getter 里，读到 `typ host` 且还没有 `typ srflx` 时立刻改成 `typ srflx`。探针 `cs` 是 60，正文首字节从 53 变成 82。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节仍是 167。`forms` 仍是 0，没有证书 document POST。站点分区仍是 `cf_clearance`。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头在清关前读到的 `RTCIceCandidate.candidate` 字符串是 `typ srflx` 的 IPv4，长度 78 或 79。本地先读到 90 次 host，之后才有 27 次 srflx。host 读的时候还没有 srflx 可换，替换次数是 0，返回值保持原样。第二次解码首字节是 167。`forms` 仍是 0，没有证书 document POST。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头在 seq 84172 对一条 `transferSize` 为 28396 的资源调用 `toJSON`，其中 `duration` 是 423.22。本地同档传输大小是 28340。只在这条资源的 `toJSON` 返回值里把 `duration` 改成 423.22。探针命中 0 次。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节仍是 72。`forms` 仍是 0，没有证书 document POST。包装已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头在清关前把 `document.scripts` 的长度读成 3，且没有按下标取元素。只让 realm 脚本在设完标记后立刻从树上拆掉。结束时脚本数是 3，realm 标记仍是 1，外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 72。`forms` 仍是 0，没有证书 document POST。站点分区仍是 `cf_clearance`。拆节点已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头星号列表在 meta 之后是页面 `SCRIPT`。本地把 `BASE` 插在页面自己的 `script` 前，注入脚本放到 `</head>` 前，避免 `BASE` 占住这个位置，同时 `baseURI` 仍是 https。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节仍是 72。`forms` 仍是 0，没有证书 document POST。站点分区仍是 `cf_clearance` 这个名字。这处放置已撤回，注入恢复到 `head` 开头。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。72 字节那轮对齐 meta 之后，有头下一节点是页面自己的 `SCRIPT`，本地仍是 `BASE` 加注入脚本。`BASE` 移出文档树后 `baseURI` 会退回 `about`，不能删。只在脚本跑完后拆掉注入的 script 节点。第二次解码首字节仍是 72，`forms` 仍是 0，没有证书 document POST。这处改动和头顺序都已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头第五个 `Attr.name` 是 META 上的 `http-equiv`（类别 `10:104`）。去掉 realm 后本地对齐位置是 `href`（类别 `4:104`）。只把第一次读到的 `href` 改成 `http-equiv`，探针命中 1 次。第二次解码首字节仍是 174，`forms` 仍是 0，没有证书 document POST。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。`parentElement` 之后的窗口和消息面没有差：`isTrusted` 8/8 为真，来源类别 `33:104`，`isConnected` 21/21 为真，页面自己的 `contentWindow` 是 14 次且没有 null 或抛错，`parentNode` 前 8 次与有头一致。`DOMRect.height` 有差，本地前 8 次是 68.2、68.2、65、68.2、68.2、244.2、1010.5、1080，有头是 67.7、67.7、65、67.7、67.7、243.7、772、842。只改这一处，探针命中 8 次。第二次解码首字节仍是 174，`forms` 仍是 0，没有证书 document POST。getter 已撤回。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。表单前没有 `scrollX` / `scrollY` / `scrollTop` 读取。`DOMRect.right` 只读了一次，有头是 1088，本地同一条 896×68 矩形的 right 是 1408。只在四舍五入为 1408 时返回 1088。探针 `rg` 是 1。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节从 73 变成 174，仍不是 85。`forms` 仍是 0，没有证书 document POST。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。`history` 在表单前只拿到对象，没有读 `length` / `state`。`entryType` 第一条两边都是 navigation（长度 10）。标题类别两边都是 `16:74`。这三项没有差，没有改。布局上，第一条 896×68 的矩形 top 都是 304，left 本地是 512、有头是 192。只把宽 896 或 960 且 left 大于 400 的值减 320，探针 `lf` 是 5。第二次解码首字节仍是 73，`forms` 仍是 0。getter 已撤回。随后只把 `DOMRect.width` 从 1920 改成 1280，探针 `wd` 是 3。第二次解码首字节仍是 73，没有证书 document POST。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留。有头表单前 `window.top` 和 `window.self` 的返回对象是同一个，`frameElement` 是 null。本地也是 `top === self === window === parent`，`frameElement` 是 null。同一窗口没有差，没有改 getter，没有新开挑战。`location` 的 hostname、pathname、search、hash、href 类别与有头一致，`referrer` 和 `document.cookie` 都是空，`cookieEnabled` 为真，`visibilityState` 为 visible。证书 document POST 仍没有。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留，请求头长度 80。有头表单前第一条 `PerformanceEntry.name` 是长度 41、首字符 `h`。本地导航条目的名字是长度 8、首字符 `d`，而 `location.href` 已是长度 41、首字符 `h`。只在导航条目的名字短于 12 或首字符不是 `h` 时，把它改成当前 `location.href`。探针 `2:41:104`。外层仍是 3792，解码链仍是 3792→2844→2132，第一次解码首字节是 152，第二次仍是 73。`forms` 仍是 0，没有证书 document POST。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留，请求头长度 80。有头表单前第一次 `requestStart` 是 331.4，本地导航条目是 0。只在 `entryType===navigation` 且值小于 200 时返回 331.4。探针 `rq` 是 1。外层仍是 3792，解码链仍是 3792→2844→2132，第一次解码首字节是 160，第二次仍是 73。`forms` 仍是 0，没有证书 document POST。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留，请求头长度 80。有头在 clearance 之前把 `document.readyState` 读成 interactive（长度 11）。本地快照是 complete（长度 8）。只在原生值为 complete 时改回 interactive。探针 `rdy` 是 2。外层仍是 3792，解码链仍是 3792→2844→2132，第一次解码首字节是 160，第二次仍是 73。`forms` 仍是 0，没有证书 document POST。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留，请求头长度 80。只把小于 200 的导航 `responseEnd` 托到 408。探针 `1:408`，页面读到了这个下限。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节仍是 73。`forms` 仍是 0，没有证书 document POST。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留，请求头长度 80。有头 `responseEnd` 采样都在 408 以上。本地导航条目原生是 0。只在 `entryType===navigation` 且值小于 200 时，把它换成当时已经结束的资源 `responseEnd`，没有就用 `performance.now()`。页面只读了一次，替换值是 57，探针 `1:57:1`。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节仍是 73。`forms` 仍是 0，没有证书 document POST。getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留，请求头长度 80。桥上没有 duration、responseStart、encodedBodySize、transferSize 或 candidate 改写。新挑战外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节是 73，不是早先的 141，也不是有头成功路径的 85。`forms` 仍是 0，慢验证模板还在，没有证书 document POST。站点分区仍是 `cf_clearance` 这个名字。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留，请求头长度 80。只把非 `.local` 的 host candidate 地址改成一次性 mDNS 样子。计数是 host 60、srflx 4、relay 0，改写 30 次。外层仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节仍是 73。`forms` 仍是 0，没有证书 document POST。getter 已撤回。duration、responseStart、地址改写这三刀各自单独生效时，第二次首字节都是 73，不能单独归因给其中一刀。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留，请求头长度 80。导航 `responseStart` 原生是 0，getter 只在这一项上把它换成同条 `responseEnd`（采样 `2:57`）。外层仍是 3792，解码链仍是 3792→2844→2132。第一次解码首字节是 100，第二次仍是 73。`forms` 仍是 0，没有证书 document POST。这个 getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留，请求头长度 80。导航 `duration` 原生是 0，getter 只在这一项上把它换成同条 `responseEnd`（采样 `1:57`）。外层仍是 3792，解码链仍是 3792→2844→2132。第一次解码首字节是 157，第二次从 141 变成 73，仍不是 85。`forms` 仍是 0，没有证书 document POST。duration getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留，请求头长度 80。只把 `encodedBodySize` 在原生值为 0 或等于 `transferSize` 时改成 `transferSize-300`。结束采样的编码尺寸是 `0,28040,2234,81033,0,2901`，对应传输尺寸 `0,28340,2534,81333,0,3201`，favicon 的 2234 与有头一致。外层响应仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节仍是 141。`forms` 仍是 0，没有证书 document POST。这个 getter 已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent` 保留，请求头长度 80。只补回文档 `transferSize` 3683 和 orchestrate `transferSize` 83242。结束采样是 `3683,28282,2534,81355,0,3201,83242`。外层响应仍是 3792，解码链仍是 3792→2844→2132，第二次解码首字节仍是 141。`forms` 仍是 0，没有证书 document POST。这两项已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：发行版 `User-Agent`（请求头长度 80）保留。在这份载荷上把视口高度改成有头页读到的 939。探针 `vh` 是 939，外层响应仍是 3792，解码链仍是 3792→2844→2132。第一层首字节从 182 变成 131，第二次解码首字节仍是 141，不是 85。`forms` 仍是 0，慢验证模板还在，没有证书 document POST。高度已改回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：有头第二次 `atob` 返回到 `Map.size` 之间只有 `String.charCodeAt(0)`。其后到 `createElement("form")` 之前只有 `window` / `document` 读取。本地 xpcshell 的 `User-Agent` 长度是 75，产品标记是 alpha；有头包长度是 80。把 `general.useragent.override` 设成发行版长度 80 后，请求头长度是 80，外层响应从 3488 变成 3792，解码链变成 3792→2844→2132，与有头长度一致。第二次解码首字节仍是 141，不是 85。`forms` 仍是 0，慢验证模板还在，没有证书 document POST。这刀已撤回。同一轮先试过 `intl.accept_languages=en-US, en`：线上请求的语言头与有头包一致，外层仍是 3488，首字节仍是 141，也已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：只把文档 `transferSize` 补成 3683、把 orchestrate 脚本 `transferSize` 补成 83242。新挑战的结束采样里这两项都在（`3683,...,83242`）。`forms` 仍是 0，第二次解码首字节仍是 141，外层响应仍是 3488 字节，慢验证模板还在，站点分区仍只有 `cf_clearance` 这个名字。没有证书 document POST。这刀已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：两刀都已撤回，证书 document POST 仍没有。真实文档导航不写快照 HTML 时，文档响应是 403、`cf-mitigated=challenge`，约 9 秒后进程以原生断点退出，orchestrate 请求没有出现。不装页面钩子的最短导航同样退出。另一刀把 `layout.css.prefers-color-scheme.content-override` 设为 light：`matchMedia("(prefers-color-scheme: dark)")` 变为 false，与有头事实一致；第二次解码首字节从 226 变为 141，外层 `cf-chl-out` 仍是 3488 字节，`forms` 仍是 0，慢验证模板还在，站点分区仍只有 `cf_clearance` 这个名字。偏好已撤回。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：有头轨迹在第二次 `atob` 成功之后、`createElement("form")` 之前，宿主调用只有 `charCodeAt(0)=85`、`Map.size=2`、然后 `Map.set` 整段载荷。本地第二次解码的首字节是 226，不会走进这三步。撤掉 `Map.prototype.set` 包装后再跑一份新挑战，`forms` 仍是 0，clearance 仍是 `text/html` 并写入 `cf_clearance` 这个名字，慢验证模板还在。包装已恢复。证书 document POST 仍没有。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：两刀都已撤回，证书 document POST 仍没有。有头页在 clearance POST 之前把 `innerHeight` 读成 939，本地默认视口是 1080。把窗口高度改成 939 之后，探针里的 `vh` 是 939，`forms` 仍是 0，慢验证模板还在，站点分区仍只有 `cf_clearance` 这个名字。高度已改回。另一刀让 orchestrate 走真实 script 请求：clearance POST 仍是 200、`text/html`、请求长度约 8791，并写入 `cf_clearance` 这个名字；随后出现证书路径的 document GET（`sec-fetch-dest=document`、`mode=navigate`、`site=same-origin`），响应 403、`text/html`，没有新的 Set-Cookie 名。进程在这次导航后退出，摘要没有打印。这不是有头事实里的 form POST。脚本替换已恢复。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：clearance 之后的证书 document POST 仍没有。页面自己的 `atob` 会解开 3488 字节的 `cf-chl-out`（得到 2616）并再解一次（得到 1960），两次都成功，正文仍是 64 字符表。随后没有 `createElement("form")`，`Map.set` 的键长最大约 38，不是浏览器事实里那次对整段载荷的写入。同一响应上 `sec-fetch-dest/mode/site` 已是 `empty/cors/same-origin`，与浏览器包一致，不是缺口。令牌大约 3.1s 到达，内层解码大约 3.3s；大约 14s 才画出固定的「验证变慢」模板（文本形状 39/6、89/15、16/4、93/14、84/11、145/21），那是脚本自带文案，不是载荷里的明文字符串，也不是证书表单。`cf_clearance` 这个名字、两次页面 `/fo/` 200、widget 正文和 `window.KP` 未定义保持不变。`{SCRATCH}/bridge-1.json` 与 `bridge-2.json` 没有写。这不是 serverAccepted。
- 2026-09-29：widget 正文取消点已经闭合。`tools/ruyidom/run.ps1` 在进程启动前同时设置 `MOZ_FORCE_DISABLE_E10S=1` 和 `MOZ_FORCE_DISABLE_FISSION=1`，子文档留在进程内。widget 通道约 250KB，结束状态 `0`，`200500` 不再出现。无头窗口被分成 interactive：父页收到 `interactiveBegin` 后没有 `complete`。对窗口文档（含 closed shadow）里有尺寸的 iframe，用 `Window.synthesizeMouseEvent` 点左侧中部之后，成功回调为 1，`msgHit` 含 `interactiveEnd,complete`，站点分区出现 `cf_clearance` 这个名字，页面第二次 `/fo/` 为 200、`text/html`、约 3488 字节、头名含 `cf-chl-out`。回调参数是长度约 688–709 的 string。`window.KP` 仍未定义。证书 path 的 document POST 仍然没有，业务回读没有发生。`form.submit`、`location`、`document.write` 都没有在 clearance 之后增加。`innerHTML` 最大长度 157。`document.notifyUserGestureActivation` 能把 `userActivation.hasBeenActive` 打成真，但不能引出证书 POST，这刀已撤回。关掉 form/location/write 的原型包装也不能引出证书 POST，包装已恢复。Referer 改写和把 widget COOP 改成 `unsafe-none` 此前已证伪并撤回。这不是 serverAccepted。
- Case status 仍是 `patching`。没有写 serverAccepted，没有新 capture，没有 safe AST / opcode，没有定义 `window.KP`。同会话实验使用启动器的 `-AllowNetwork`。纯离线不是这轮的目标。
- 通道仍是锁定 Gecko CLI `tools/ruyidom/run.ps1`（本会话没有 `ruyidom_run`）。Doctor 二进制 hash 与 `mcp/ruyidom-mcp/README.md` 一致；`lib/ruyidom.js` sha256 `9f21705d909f5e5c…`。本轮 doctor `ok=false` 只因临时目录残留，不是 hash 漂移。
- 页面 HTML 进文档。orchestrate 只按页面 script URL 本地应答（sha256/16 `aa2b09a484f556d1`，238694 bytes，flow `h/b`）。Turnstile `api.js` 按捕获到的 script URL 本地应答；同 URL 的惰性标签留在文档里，`HTMLScriptElement.src` 在原生值为空时读回 `data-ruyidom-src`。`history.replaceState` 与这个 getter 的 `toString` 在页面 realm 里是 native-like。
- 离线两次 exit 0 一致：orchestrate=1，fo=3，eb=0，jsd=0，页面错误空。`window.KP` 仍不存在。`window.turnstile` 是 object，匹配 Turnstile 正则的 script 标签 2 个，`src` getter toString 含 native code。`xdiN1` 在 Window 上是 function。Turnstile onload 被调用 2 次。同步回合能走完。
- `/fo/` 已由页面自己的 XHR 发出，没有提交到站点。不回放时三次都是 POST，路径模板 `/cdn-cgi/challenge-platform/h/b/fo/{id}:{id}:{id}/{id}/{id}`，header 名只有 `cf-chl` 和 `cf-chl-ra`，body 各 2306 字节，sha256 每次不同。这不是 serverAccepted。证据：`agent-notes/20260928-ruyidom-bridge.md`。
- 用另一次有头捕获的第一条 `/fo/` 200（106880 字节，加上 `cf-chl-gen`）回放两次，结果一致：只发出 1 次 POST，响应 served=true，随后 `InvalidCharacterError: String contains an invalid character`（eval line 1 column 287）。没有第二次 `/fo/`。异会话响应体不能当本轮答案。默认输入已关掉回放。证据：`agent-notes/20260928-fo-response.md`。
- 真实同会话（`-AllowNetwork`，每次新的 403 挑战页，脚本 200 后在本地带上原型镜像执行，`/fo/` 不拦截）：两次 POST 都有真实响应。第一次 200，约 106864–106876 字节，`text/plain`，Set-Cookie 名 `__cf_bm`，响应头名含 `cf-chl-gen`。第二次 200，3488 字节，`text/html`，响应头名含 `cf-chl-out` 和 `cf-chl-out-s`，Set-Cookie 名 `cf_clearance`。没有 `InvalidCharacterError`。`cf_clearance` 带 `Partitioned`，落在站点分区罐里，未分区罐只有 `__cf_bm`。跑完时 principal、currentURI、location 都是证书页路径。about:blank 三条安全错误都在 `fo=0`。有头对照：clearance 之后 24ms 就是证书 path 的 document POST（`agent-notes/20260928-post-clearance.md`）。本地仍然没有这次 POST。`media.navigator.permission.disabled=true` 让 `createOffer` 和 `setLocalDescription` 都兑现（`1/1/0`，ICE 35–36），SDP 改写没有拒绝 promise。取消 `/g/chains/` 已撤回，仍无 POST。顶层和 iframe 的 form/location 导航计数都是 0。有头 fo 正文是编码载荷。`turnstile.render` 进入 1 次，成功回调是 0，`error-callback` 短码 `200500`。widget 子文档 HTTP 200（policy 7），嵌入方主体已是证书页，不是 `about:blank`。响应头没有 `frame-ancestors`，父文档 CSP 策略数是 0。COEP 是 `require-corp`，CORP 是 `cross-origin`，COOP 是 `same-origin`。关掉 CSP、清掉响应 CSP、清掉 COEP+COOP 都不能让文档提交，这三刀都已撤回。widget 通道自己的结束码是 `80004005`（`NS_ERROR_FAILURE`），`requestBlockingReason` 是 0。`onStartRequest` 成功且当时状态是 0，随后正文 0 字节。`api.js` 同样是 brotli 且已执行。把 widget 子文档改成 gzip，以及关掉 COOP/COEP 远程进程偏好，正文都仍是 0 字节；这两刀已撤回。文档 stop `805e0006` 不是这条通道的结束码。没有 widget 自己的 `/fo/`，没有证书 document POST。这不是 serverAccepted。证据：`agent-notes/20260928-live-fo.md`。
- 同一轮探针：Worker 1、iframe 1、blob URL 1、`crypto.randomUUID` 1、`performance.getEntries` 1、`RTCPeerConnection` 1、`createOffer` 1 次且在 15s pump 内没有 settle、ICE candidate 0、honk 消息 0。`_cf_chl_opt` 36 键。`SessionStoreFunctions.sys.mjs` 仍是引擎文件缺口，没有补。
- 有头复看 `rt_20260928075623_d3a207a25f`：mode 是 `interactive`，不是 headless。UA 为 Firefox，配置里没有 headless/marionette/webdriver。没有 click。页面仍是先 `GET` cert 403 `cf-mitigated: challenge`（标题 Just a moment），再 orchestrate、Turnstile、四次 `/fo/` POST 200，最后一次响应带 `cf_clearance` 这个 cookie 名，随后 `POST` 同一 cert 200，标题是证书页。没有 `eb`。早一轮 `rt_20260928061614_ee71af43b2` 的文档状态序列相同。无感通过是 managed challenge 自己走完，不是无头把挑战跳过。这不是本地补环境的 `serverAccepted`。

### 2026-09-02 隔离 trace 复核

- Mac 同一 Sticky route 的受控请求先前可复现 `403 + cf-mitigated: challenge`，证明 Cliproxy、sidecar 与 managed challenge 输入链可达；本轮两次受控复跑分别直接返回真实 PSA 业务页 `HTTP 200`，最多 12 次 admission 请求未再次触发 managed challenge，故 Node solver 本轮没有可消费的 fresh orchestrate 材料。
- RuyiTrace `rt_20260902054213_014bc111c5` 使用 hash-locked 3.1.0 Firefox 155 runtime 完成 60 秒 `interactive/challenge-fast` 采集：19,607 records、181 artifacts，runtime/index/receipt 三门均 pass。
- 本轮浏览器事实命中 Cloudflare `jsd/oneshot` POST 200；精确索引中 `jsd/oneshot=4`，`orchestrate=0`、`/h/g/fo/=0`、`eb/managed=0`、`cf_clearance=0`。这证明 Cloudflare 检测链处于活动状态，但没有进入 managed challenge 求解链。
- 当前结论保持 `production-integration-pending`：`psa-solve-v16-20260902` 不切生产。下一次必须在 fresh managed challenge 窗口复用同 SID/Cookie/tunnel，验收 `fo/eb -> cf_clearance -> 约 5 秒后真实业务 readback 200`；未触发 challenge 不能计为 solve 成功或失败。
- `web_case.py run` 登记被现有 `web-case.json` 合同漂移拒绝：case 顶层被错误标为 completed，但 local/parity/protocol stages 仍 pending/triage-only。该治理缺陷不影响本轮 receipt 已落盘，但需单独修正合同后再登记，禁止为通过校验伪造 stage 完成状态。

### 2026-08-16 clearance 会话绑定与生产链路实验（demo2-demo6 全记录，定论见 findings F6/F7）

#### 一、机制定性（官方文档 + 四源搜索求证）

- PSA 的 429 + `cf-mitigated: challenge` 来自 **rate limiting 规则 + managed challenge 动作**（throttling 模式，Free/Pro/Business 计划强制）；403 是 WAF/security 类规则 block 的状态码——Firefox 指纹通道当前只见 429（curl/Node TLS 通道才会 403）。
- challenge 状态按 fixed action 语义持续：**触发后 ~20-30s 内所有请求被拦**（与 clearance 无关）。
- 官方模型：pass challenge -> request counter 归零；cf_clearance tied to visitor/device（实测为 IP+UA+TLS 级）。

#### 二、实验时间线（同日，同 IP、同 sn 序列、firefox 指纹）

| 时间 | 实验 | 形态 | 结果 |
|------|------|------|------|
| 16:29 | demo2 串行求解组 | 同 session + 独立提交 clearance | 续航 [13,16,9,14] |
| 16:34 | demo2 no-solve 对照 | 等 25s 不求解 | 稳态续航 [6,8] |
| 17:28 | demo3 run2 | 新会话 B 带 clearance / C 裸 | B=1 / C=5 |
| 17:33 | demo4 AB 交替 | 触发后 20s 开始 | B、C 全被拦（窗口内） |
| 17:43 | demo5 同 session bridge | 冷却仅 2s | A 续航 5 |
| 17:47 | demo5 同 session bridge | 冷却 5s | A 续航 15，B 对照 0 |
| 18:52 | demo5 bridge | 求解提速后固定冷却撞窗 | A=0、B=0（恢复期仅 17s） |
| 18:54 | demo5 | 恢复期 30s | **反转：A=1、B=15** |
| 19:08 | demo5 subject=c | 单变量裸会话 | C=2 |
| 20:02 | demo5 subject=b | 单变量 clearance | **B=15（复现）** |
| 20:09 | demo5 subject=a | 单变量原会话 jar | **A=0（jar 污染）** |
| 20:32 | demo6 生产首跑 | 异步 bridge + 会话分离 | 段 [15,16,6*,15]，669 页/h，1 次连接挂起 |
| 22:18 | demo6 优化复跑 | 404 微间隔 + 挂起快判 + 重试 | 段 [17,8,8,9,9]，788 页/h，重试自愈 1 次 |

（* 6 为连接异常截断段）

#### 三、定论（横比三轮 + 生产复跑支撑）

1. **clearance 跨 session 有效**（IP+UA+TLS 级绑定）：裸 C=2 vs 带 clearance B=15（两轮复现），增益约 7 倍。官方「tied to visitor/device」在本场景不含会话级绑定。
2. **bridge 同 session 形态有 jar 污染副作用**：fo 响应 set-cookie 回灌进采集会话 jar，挑战链中间态 cookie 与 clearance 混带 -> 立即重新挑战（A=0 甚至低于裸 C=2）。demo2 旧形态（fo 走独立 cr.post）无此问题。
3. **求解通过 = 计数器归零**：B 从 0 打到阈值（15）才再触发，与 Phase 1 触发位置一致。
4. **恢复等待必须按距触发绝对时间 >= 30s**：求解提速（27s -> 12s）后固定冷却会撞衰减窗口。
5. **rate limit 阈值动态衰减（F7，medium 置信）**：同 IP 当日 20+ 轮实验后，段通过数从 15-16 降到 8-9（20:32 run 15/16/15 -> 22:18 run 17/8/8/9/9）。求解成功率保持 100%，触发频率上升是 CF 侧收紧。单 IP 吞吐上限随之从 ~1000 降到 ~750-800 页/小时。

#### 四、生产形态（demo6，已两轮实测）

```
干净 AsyncSession 采集（显式 ck，404 微间隔，gap 间隔）
  -> 429 触发（挑战页 body 直接到手）
  -> 触发会话即用即弃 capture-only bridge 异步求解
     （asyncio subprocess + AsyncSession 发 fo + FO_CONTINUE/FO_ACCEPTED 分类 + stdin 回灌）
  -> 恢复等待（距触发 >= 30s）
  -> 新干净 AsyncSession + 显式 ck 继续
异常处置：挂起 10s 快判 -> 重建会话重试一次 -> 仍失败 45s 冷却；
重试撞挑战页直接转入求解。
```

吞吐模型（单 IP）：`段请求数(阈值) × RTT + 求解 ~13s + 恢复 ~17s` 为一个周期。
- 阈值 15 时：~50s 周期 -> ~1000 页/h 理论上限
- 阈值 9 时（当前 IP 状态）：~43s 周期 -> ~750-800 页/h（实测 788 已贴合）

#### 五、边界与下一步

- 单 IP 继续优化的代码空间已尽；提速路径：IP 冷却数小时（阈值大概率回 15）、换出口、或多 IP sticky 池轮换（每 IP 一个 demo6 worker，proxy-usage 提取 + 注入，吞吐线性扩展——高并发采集的正确姿势）。
- F7 为 medium 置信：需不同 IP/时段对照确认阈值衰减是「当日行为累积」还是「长期趋势」。
- demo6 的 solve_bridge_async 与主循环是采集主链的移植单元；旧 bypass_solve（demo2/3/4/5 共用形态）已被 bridge 形态取代。

## Browser / Local / Purecalc Boundary

- Browser fact role: `verified`（rt_20260815060651_eb196ed770，index/receipt integrity pass，rootSha256 399daaf7dc35e4b7489aed07db3c60cf0c69d80bdfb0e0da5f78fedfadc8df7e；receipt pointer sha256 自引用不一致为 MCP 侧 bug，已在 web-case.json limitations 记录）
- V8 local fact / first divergence: 未启动（引擎执行层优先）
- Environment patch scope: `external-host-only`; VM/opcode/bytecode/WASM internal patch: `forbidden`
- Success baseline (`code.js` / `runtime/*.code.js`) and `.base.js` hash: 未建立
- Purecalc ledger: `纯算提取进展清单.md`
- Purecalc candidate (`code.pure.js` / `runtime/*.pure.js`) and stable entry: 未建立
- `localReproduced` / `transportAdmission` / `serverAccepted`: 均未达
- Vanilla client business readback evidence: 无
- Browser automation in final collector: `forbidden`

## Stable Baseline

- Browser run / evidence pointer: rt_20260815060651_eb196ed770（psa_solve）
- Local run / profile: RuyiDOM gecko-xpcshell（Firefox 135 base），runtime hash 校验 pass
- Canonical input hash: 挑战页 cH/cN/cRay 每次访问刷新；runner 输入 `ruyidom-input-v1.json`
- Resource epoch and relevant content hashes: orchestrate `chl-page-orchestrate.js`（228910 bytes，ray a2b5fd7dff701b46 版本）
- RequestShape / target endpoint: `POST /cdn-cgi/challenge-platform/h/{flow}/{eb}/{payload}/{...}/{...}`；flow 段当前为字面 "undefined"（缺口）
- Verified wire route / decoy or wrapper route: 提交为 challenge-platform 相对路径 POST
- Dynamic state and Cookie writer / refresh / outbound egress evidence: `__cf_bm` 两段刷新（挑战前/求解后），`cf_clearance` 求解后下发（浏览器事实）
- Response decode pipeline and fixed-sample proof: 未建立
- Route-local transport admission matrix: 未建立

## Parameter And State Ledger

| Field or state | Source -> transform -> consumer | Current verification | Evidence pointer |
| --- | --- | --- | --- | --- |
| `_cf_chl_opt` | 403 页 init script 注入 -> orchestrate 读取 | 33 字段初始化 verified（引擎） | runner pageState.cfChlOptKeys |
| 提交 URL flow 段 | orchestrate 内部构造 | 3 段字面 "undefined"（缺口） | runner wire xhr url |
| `cH`/`cN`/`cRay` | 403 页每次刷新 | 时间敏感已排除（fresh 页同缺口） | challenge-page-fresh.html |

## First Divergence Or Blocker

- Observation: 引擎执行 orchestrate 后抛 `TypeError: can't access property "call", iw is undefined`（混淆局部变量，经 eval 抛出，window.onerror 不捕获）；提交 XHR URL 含三个字面 "undefined" 段。真实浏览器同版本 orchestrate 无此错误（求解 1.1s 完成）。
- Classification: `execution-boundary`（orchestrate 混淆内部执行路径差异），宿主 API 面板健全已排除常见缺口；meta CSP 与 history.replaceState 两缺口已修复且有证据。
- Evidence pointer: runner 输出 errorShapes.stackHead（observe@ruyidom.js:1267 链）
- Why alternative explanations do not currently fit: fresh 挑战页重跑结果一致（材料过期排除）；hostPanel 16 项宿主 API 全 function/object（宿主缺失排除）。

### 2026-08-15 v8trace 定位收敛（源码级）

- v8trace（challenge-fast，1415 records）Node 崩溃：`TypeError: T[rv(...)][rv(...)] is not a function`；RuyiDOM 引擎同位置 `IG is undefined`——两环境同根。
- 崩溃链（v8trace throw_context + 源码解码）：
  1. J 表构建（RfXVH/JSyym/UoZbM/Toloz/UMkbs/BUgft 6 函数 + SzTgJ="…challenge-platform/h/" + bXxEG="navigation" + yQYB9 数组）完成（源码 50136 附近）
  2. 主逻辑调用 `T[1381](base64$base64)`（日志队列函数，源码 28525 定义：内部 `T[1020][1761](Z)` push 日志）
  3. 崩溃：`T[1020][1761]` 不是函数——T[1020]=[] 的赋值（源码 28496）与 T[1381] 同序列、位于 switch 语句 break 后——**该赋值序列被条件跳过**（引擎环境未走进对应 switch 分支）
- 关键编码解码：wn.Ie=1381、wn.Ip=2099（条件检查键）；dG={Z:1020,J:870,IV:958,Ip:1020,Ii:1761}（T[1020]=队列数组、T[958]=30、[870]=length、[1761]=push 语义）。
- 遗留定位工作：真实浏览器执行路径对照（该 switch 分支在浏览器是否执行、依赖哪个环境条件）——CDP 断点 orchestrate 源码 28496 可一步验证。

### 2026-08-15 三环境对照（Node/iv8/RuyiDOM）与缺口阶梯

- iv8（离线 V8 + DOM 仿真，probe-4 domPanel）：`document.createElement`=function 但
  **`document.createElementNS`=undefined**——orchestrate 在 Pv（源码 106287）调用
  `C[XJ(...)](2参数)`=createElementNS(ns,tag) 创建 CF 指纹 SVG 元素（`cx`,`15` setAttribute）。
- iv8 + createElementNS 桩后：无错误但 0 POST、静默退出（下一缺口不抛错）。
- Node（v8trace v8-20260815075849）：补 createElementNS 桩后崩溃点后移 3 行
  （index.jsonl:1396 vs 1393），同类型 T[rv()][rv()] 崩溃——Node DOM 缺口面过大，
  逐桩补齐不现实（SKILL.md 判据：DOM 缺口面大 = 补环境不可行场景）。
- RuyiDOM（真实 Gecko，最完整）：**createElementNS ×3**（lastTag="path"，SVG path）
  + createElement ×41 执行成功，之后崩于 `IG.call`（IG undefined）——比 iv8/Node
  走得更远。错误经 eval 抛出无列号（onerror/addEventListener('error') 均不携带
  message/colno）。
- 结论：公共缺口=createElementNS（有证据）；RuyiDOM 的 IG.call 是下一缺口
  （orchestrate 内部，混淆变量名，定位需 VM 级分析或引擎列号支持）。

### 2026-08-15 IG.call 定位收敛（Pv → IF 函数边界）

- Pv 函数完整解码（源码 106287 后）：`document.createElementNS` 创建 SVG 图标
  指纹元素（setAttribute cx/cy/r=15 + path d=CF 图标路径数据 + appendChild 组装），
  **RuyiDOM 已完整执行**（createElementNS×3 计数吻合：circle/icon/path 三元素）。
- 崩溃点 = **下一个函数 IF 的首行**（源码 138575 附近）：
  `IV = T[ZZ(1753)][ZZ(1134)]()`，随后 `for(Ip=0; Ip<IV[ZZ(870)]; ...)` 遍历——
  语义是"获取元素集合并遍历"。`IG.call` 崩溃 = T[1753键][1134键] 非函数。
- T[1753] 非 document（RuyiDOM 的 document 方法原生齐全且 querySelectorAll 类
  可用）——需字符串表解码 1753/1134/870 三键确认宿主对象。
- 三环境统一叙事：Pv 之前的缺口（createElementNS 等）→ 修后到达 IF 的
  T[1753][1134] 集合调用——真实浏览器该调用成功（元素集合非空）。



### 2026-08-15 IG.call 最终定位（ID 状态机 case '5'）

- IF 链路全健康（RuyiDOM 插桩实测）：`performance.getEntries` ✓、
  `PerformanceObserver`（new T[1910键]）✓、ID 回调是 function ✓。
- 崩溃点 = ID 状态机（源码 180073 函数）case '5'：
  `T['_cf_chl_opt']['yQYB9']?.['call'](IG)`（插桩解码：_cf_chl_opt,yQYB9）。
- RuyiDOM 里 `typeof _cf_chl_opt.yQYB9` = **object**（非函数）；真实浏览器
  挑战求解期 yQYB9 应为函数（挑战完成后 _cf_chl_opt 整体清除——CDP 实测
  hasChl=false，求解期临时状态）。
- 语义：yQYB9 是 orchestrate 求解流程注册到 _cf_chl_opt 的回调函数；
  RuyiDOM 引擎里注册步骤未执行（被更早的环境分支跳过），yQYB9 停留在
  对象形态（33 字段初始化的字段形态）。
- 三环境缺口阶梯定稿：
  Node（createElementNS 等 DOM 缺口面大）< iv8（修 createElementNS 后
  静默退出）< RuyiDOM（走最远，卡在 yQYB9 回调注册链）。

### 2026-08-15 Phase 1 结果：yQYB9 假设修正

- 赋值历史捕获（_cf_chl_opt setter 观测）：403 页 init 整体赋值 16 字段；
  yQYB9 **仅一次赋值、类型 object、Array.isArray=true**——**yQYB9 是数组**
  （收集 performance entries 的队列），"应为函数"假设被推翻。
- case '5' 真实操作（三键解码）：`_cf_chl_opt.yQYB9.push(entry)`——
  数组 push，引擎里健全。
- 崩溃点在更深处：caseNow=2（ID 状态机 case '2'）——case '2' 变量面板
  健全（Ic=object/PX=function/PI=object/IV[IU]=function）——崩溃链
  ID case '2' → PX（源码 37470）→ PJ（源码 125005，entry 属性 JSON 解码：
  `decodeURIComponent(JSON.parse(...))`）。
- PJ 的 J 参数（entry 属性字符串）在引擎环境可能为 undefined 或格式差异
  ——下一缺口定位目标。
- 嵌套回调链：ID case '2' → PX → PJ（每层 2-3 工具调用下钻，还有若干层）。

### 2026-08-15 Reqable 真实浏览器对照（决定性新事实）

- 当前 PSA 无感挑战 = **Turnstile non-interactive 自动通过**（用户无点击）。
  提交 URL 模板 `/cdn-cgi/challenge-platform/h/g/fo/{id}:{ts}:{hash}/{ray}/{token}`
  （psacard.com 侧 + challenges.cloudflare.com 侧各一次 fo POST，最后
  POST /cert 带求解结果拿 200 页面）。
- 新版 orchestrate（229681 bytes）内 eb 模板：`/eb/{id}/{ray}/{token}`，
  id 为硬编码字面量。引擎旧材料拼出的 `/h/undefined/eb/{id}/undefined/undefined`
  缺 ray/token 段。
- 新 orchestrate + 新 403 页重跑引擎：错误从 `iw` 变 `IG`（同模式
  `.call` 崩溃）——缺口跨版本稳定，是引擎环境差异而非材料问题。

## Current Single-Variable Experiment

- Baseline: offline 注入 + orchestrate 本地映射 + history/storage 桩（v1 runner）
- Changed variable: 移除 meta CSP（v4）→ history.replaceState 包装（v5）→ storage 原型包装（v6）→ fresh 挑战页（v7）
- Expected discriminating result: 提交 URL 完整、无 orchestrate 内部异常
- Result: SecurityError 已消除；`iw is undefined` 与三个 undefined 字段稳定存在
- Evidence pointer: psa_solve/ruyidom_cf_shield_v1.js 迭代记录

## Rejected Or Inapplicable Routes

| Route | Evidence that rejected it | Re-open condition |
| --- | --- | --- |
| RuyiDOM 真实导航（v2） | 导航后 document 空（location 仍 about:blank） | 引擎真实导航模式修复 |
| gated trace 抓挑战段 | GATE_TIMEOUT / BROWSER_OWNERSHIP_PROBE_FAILED 两次失败 | MCP 侧修复 |

## Minimal Verifiable Facts

- 403 页 managed challenge（cType managed / cTplV 5 / cvId 3），CF 边缘 NRT。
- 浏览器求解 ~1.1s 且 managed 无交互自动通过；Turnstile 只在预热 profile 连续访问时触发（本 case 目标规避）。
- 引擎能初始化 `_cf_chl_opt` 33 字段并发出提交 XHR（URL 不完整）。
- 提交 URL 前缀 `/cdn-cgi/challenge-platform/h/`，三个 "undefined" 段为 orchestrate 主动拼接的字面量（缺口字段名待定位）。

### 2026-08-15 环境缺口定稿：UpvLO0 + ZHfDS6（VM 程序验证链）

- VM 程序（IY 状态机 case '13' runProgram，44 opcode 主程序 + 子程序）语义已完整解码：
  - yQ=常量物化（字符串/数字/NaN/数组）、yD=双寄存器常量、yX=寄存器移动、yA=对象创建、yj=对象字段写、y7=属性获取、ye/yR=按名调用 opcode（`obj[prop].call(obj,args)` 族）
  - 程序数据：10 个字符串（window/prototype/ANTT9/UpvLO0/querySelectorAll/querySelector/Element/Document/style/eval）+ native 函数 + 常量 4521/NaN/1755
  - 第一个调用：`window["UpvLO0"].call(window, "1v01dl/...==$NtkGhkT...==(base64$base64 16+16字节)")` — 引擎里 window.UpvLO0 undefined 崩溃（yR opcode Io=1 分支，方法键 "call"）
  - 第二个调用：`window["ZHfDS6"].call(window, "function jcLw7(s){return function(k){for(var o=new Uint8Array(k.length),i=0;i<k.length;i++)o[i]=k[i]^s.charCodeAt(i%s.length);return o}}")` — ZHfDS6 接收程序重建的**完整函数源码**（XOR 流解密器）
- 程序自身从字节码重建函数源码（"function"+" "+"jcLw7"+"(s){...}" 片段拼接）→ 交给 ZHfDS6 → 随后程序调用 window["jcLw7"] —— 语义：ZHfDS6 = 函数注册/求值助手（真实浏览器中由 orchestrate 定义，被引擎环境分支跳过）
- 诊断桩（功能性）：window.UpvLO0=记录桩；window.ZHfDS6=(0,eval)(src) —— 补桩后 errors=0，程序完整运行：
  - 到达「Verification successful. Waiting for {placeholder.com} to respond」（PJ 解码 mtsjj1 文案）
  - 构建隐藏 iframe（sandbox=allow-same-origin + visibility hidden 等 8 项样式）
  - UpvLO0 后续调用载荷：13V7mVH...$QnwcCJ...、bY4JPwin...$o1+qY2T...
  - 性能指纹基准循环：1337331 空格字符串（~1.3MB）+ Date.now 时间戳反复构建 —— 循环等待提交层响应不闭合
- 剩余缺口：提交/响应异步层（Worker「honk」消息协议 / blob URL / iframe 脚本）在 RuyiDOM 引擎未把消息回传页面，程序永远轮询。RuyiDOM Worker/iframe 异步支持待验证（hostPanel wk=function 存在但消息回传未证实）。
- 关键证据文件：workspace/psa_solve/ruyidom_cf_shield_v1.js（插桩 runner + 级联桩）、challenge-material/orchestrate-served.js（served 代码，列号映射用）

### 2026-08-15 提交链路实证（第二里程碑）

- Worker/blob postMessage 往返 smoke 通过（pong:ping）——RuyiDOM Worker 层不是执行边界。
- **window.ZHfDS6 = window.eval（原生别名）**——程序检查 `ZHfDS6.toString() === eval.toString()`（对比值 false 时循环）；1.3MB 空白字符串是 eval 性能指纹基准（长度 1337359 ≈ 程序常量 1337331）。此前 eval 桩/worker 转发桩均错。
- UpvLO0 = XOR 流解密器（按 jcLw7 语义实现，payload base64$base64 拆分 XOR）——已产出 16 字节解密值（e02433f0...、95096791...、ced1a35c...、8d5e4d41... 等，MD5 级 128 位哈希形态）。
- 修复 `String.replace` 的 `$'` 特殊模式 bug（wrapper 中 `split('$')` 被替换串解释，整个页面被插入）——改用 replacer 函数。
- 修复 setTimeout/setInterval 包装 receiver（固定 window，程序用对象作 this 调用时原生会抛）。
- resources.handler 改为 blockUnmapped:false + challenge-platform 的 xhr/document 放行真实网络（net-pass 记录）。
- **提交实证**：`POST /cdn-cgi/challenge-platform/h/g/eb/478345907:1786773913:H-v1Ic.../a2b6539108bf25c6/managed`，body = 完整 $ 分隔指纹载荷；页面设置 cf_chl_rc_ni=1；_cf_chl_opt 新增 CqJg7/cseK1/jWOLY8 字段；流程深入 Angular testability 探测（whenStable/getTestability/get）。
- 剩余缺口：P7 轮询器（提交验证 + 重试）内 `J["DCkwl7"]`（ZZ(1011)）读取 J undefined——J = P7 第二参数，来自 Iw 的 `setTimeout(P7,100,Ig,IG)` 传参（IG undefined，上游状态缺口）。P7 尾：`J[ZZ(519)]=...` + `Ie.send(x(J))`，x(J) 为载荷变换函数。

### 2026-08-15 cf_clearance 持续采集验证（生产可行性）

- 实验（test_clearance_collection.py）：sticky 出口（196.170.94.23，全程一致）拿 clearance → 同出口同 Firefox 指纹连续请求 20 个页面。
- 结果：17×200 + 3×404（序列号不存在的业务空结果）+ **0×403**——有效页面实质 100% 通过。
- 采集四契约（实验确认）：① sticky 出口绑定（sid+t-30，clearance 与出口 IP 绑定）；② TLS 指纹一致（Firefox impersonate）；③ __cf_bm+cf_clearance 会话延续（跟随响应轮换）；④ 0.3s 间隔 20 连发无触发。
- 生产闭环：403 → Node 求解（14s）→ curl_cffi 提交 → clearance → 同会话持续采集；clearance 过期重走 --fresh。

### 2026-08-15 Cliproxy 机房 IP 链路验证

- 链路（记忆 cliproxy-windows-chain-lessons 复用）：本机 → `ssh -D 127.0.0.1:18081 oracle-newapi-primary`（SOCKS 隧道）→ Cliproxy gateway `us.arxlabs.io:3010`（Rand 账号，机房出口 223.196.193.34/102.157.229.183 等）→ 目标。Windows Clash TUN 对 gateway 3010 明文 CONNECT 系统性挂起——必须走 SSH 隧道（历史已知坑）。
- demo 新增 `--cliproxy-rand`：材料抓取（curl_cffi 非 impersonate 经级联触发 403）+ 提交/验证（curl_cffi Firefox 指纹经级联）全链路机房 IP。
- 实测（23:38）：材料 403 → Node 求解 errors=0 → fo 提交 200 → cf_clearance → 验证 200 + 159,484 字节 + "Cert Verification 143963534" = **serverAccepted TRUE**。
- 观察：机房 IP + Firefox TLS 指纹直通 200（无挑战）；机房 IP + 非浏览器 TLS（curl 原生）触发 403——TLS 指纹仍是首要变量，IP 类型是次要变量。
- 遗留清理：测试 SSH 隧道（18080/18081）已清理。

### 2026-08-15 TLS 指纹根因定稿（重新 trace 结论）

- **重新 RuyiTrace capture（2.5.6 runtime，fresh profile）**：真实浏览器指纹（Firefox 155 TLS）**直通 200**（无挑战）——同一 IP、同一时间窗口。
- **curl_cffi 0.16.0（impersonate=firefox）实测直通 200 + 159KB 真实页面**——与浏览器一致。
- **根因定稿**：TLS 指纹是决定性变量——Node 20 TLS 在 CF 侧被标记为非浏览器客户端（触发挑战 + 求解后验证被拒）；Firefox 指纹放行。此前「IP 风控升级」归因被修正：真正变量是客户端指纹层，IP 变化只是改变了触发条件。
- **修复链路**：求解仍在 vanilla Node（orchestrate 执行 + 载荷产出）；**提交与验证改用 curl_cffi Firefox 指纹**（demo.py IMPERSONATE="firefox"）。实测：fo 提交 200 + cf_clearance 签发 → 验证 200 + 159,618 字节 + title "Cert Verification 143963534"（真实页面）。
- demo.py 无参数一键运行稳定复现 serverAccepted（23:19 验证）。Node 求解侧无改动——载荷自始至终被 CF 接受，唯一变量是发送载荷的 TLS 指纹。
- 修正历史局限记录：curl/Python urllib 重放被拒的原因同为 TLS 指纹（非「不同源」）；curl_cffi Firefox 指纹是唯一验证可用的 Python 侧 client。

### 2026-08-15 eb 触发定位与无痕对照

- eb 提交代码结构已定位：`new XHR → open("POST", ebUrl) → timeout=5e3 → setRequestHeader → send(gi(gN))`，整段在 try/catch（异常静默吞）。Node 中该段未执行（无 open 记录）——**上层触发条件不满足**，非 send 失败。
- 同进程内联验证（求解+验证同一 Node 进程/TLS）仍 403——**TLS 会话绑定假设排除**。
- **无痕浏览器对照（用户实测）**：无痕可直接进入（managed 挑战自动求解通过）——IP 未风控。Node 求解被拒而真实浏览器通过——差异收敛到：① eb 提交缺失（浏览器必发）；② 行为指纹质量（Node 的性能基准/时间戳字段与真实浏览器分布不同，CF 风控模型学习后收紧）。
- 排除项汇总：TLS 会话绑定（同进程仍 403）、IP 风控（无痕浏览器正常）、cookie 组合（jar 语义已修）、XHR 响应头（已修）。
- 剩余主嫌疑：eb 提交（触发条件上层链待定位）+ 行为指纹字段真实性（补环境边界——1.3MB eval 基准、时间戳等为 Node 真实值而非浏览器值）。

### 2026-08-15 分支链路对比（Node vs RuyiDOM 同材料）

- 同材料（223831）对比：RuyiDOM 提交 = fo ×1 + **eb/managed ×1**；Node = fo ×2——**Node 缺 eb 提交分支**。
- 已修复相关缺口：XHR `getResponseHeader/getAllResponseHeaders`（原返回 null——P7 读响应头判断）、document.cookie 增量 jar 语义（原覆盖语义丢失 cf_clearance）、XHR 标准字段（responseType/responseURL/withCredentials/timeout/upload/on* 事件属性）。
- eb 提交仍未触发：fo 响应 body 为加密 blob（非 JSON），P7 的解密-判断链未闭环（解密函数/key 来源待定位）。
- **关键对照**：22:26 的 Node serverAccepted 成功时同样无 eb 提交——**eb 非 clearance 生效的必要条件**（至少风控宽松窗口如此）。当前连续 403 主因判断仍为 IP 风控升级（高频求解），eb 缺口列为结构差异待完善项。
- 载荷字段数对比（同材料）：Node 29 字段 vs RuyiDOM 20 字段——结构差异存在，但字段值为随机加密无法直接对比内容。

### 2026-08-15 IP 风控升级证据（验证波动归因）

- 时间线：21:40-21:47 vanilla Node 补环境 serverAccepted 多次成功（HTTP 200/159KB）；21:48 起连续 6+ 次全 403（demo 与 verify 脚本同败）。
- 求解链稳定：cf_clearance 每次均签发（Node fo 提交响应），失败仅在「clearance 页面验证」环节。
- 排除项：TLS 一致性（Node TLS 验证同 403）、cookie 组合（原材料 bm / 轮换 bm 双组合）、代码差异（demo 与 verify 脚本同败）。
- 归因（风控判定纪律-多维）：AWS 数据中心 IP（43.199.43.75）高频求解（半小时 20+ 次 fo 提交）触发 CF 会话风控升级——clearance 形式签发但页面二次验证（jsd 行为证据层）拒绝。求解链能力不变，验证成功率受 IP 信誉窗口约束。
- 复验路径：换 IP 冷却后重跑 demo.py --fresh（求解链无需改动）。
- **复验结果（用户实测）**：换 IP 后 demo.py --fresh 通过——serverAccepted 复验成功。归因闭环：IP 风控升级是唯一变量；vanilla Node 补环境求解链稳定可用。

### 2026-08-15 vanilla Node 补环境 serverAccepted（最终里程碑）

- **纯 Node（无 RuyiDOM/浏览器）求解 → Node XHR 提交 → cf_clearance → 页面 200/159KB = serverAccepted TRUE**（2026-08-15 21:41，demo.py 一键复现）。
- 关键修复链（Node 版 eb/clearance 闭环）：
  1. XHR shim 相对 URL 需 base（`new URL("/cdn-cgi/...")` 失败静默 return——提交从未发出）
  2. XHR 同源自动附 Cookie（浏览器行为；此前提交无凭证被 CF 拒）
  3. 响应 Set-Cookie 应用（字符串/数组双形态）+ demo 从 responses 提取 cf_clearance 与轮换 __cf_bm
- 验证证据：Node 的 fo 提交响应 `cf_clearance=I.5OxTVQlN...` + 轮换 __cf_bm 组合请求页面 → HTTP 200、159,394 字节真实页面；Python/curl 重放同载荷被 cf-chl-out 拒（TLS 指纹）——**Node 20 TLS 被 CF 接受**。
- 提交形态：fo ×2（bodyLen 2178 首轮 + 4599 完整轮）；clearance 由第二轮响应签发。

### 2026-08-15 vanilla Node 补环境形态（模块化重构）

- 用户纠正：补环境运行时依赖应为 Node（RuyiDOM 是诊断执行层，SKILL 主线：vanilla Node/Python client 最终验收）。demo 用 Python（非 PS）。
- 产出：`runtime/code.js`（vanilla Node 浏览器面 shim + 定位缺口补丁）+ `runtime/run.js`（vm 执行 + 提交捕获）+ `scripts/demo.py`（无参数一键 demo）。
- Node 补环境缺口链（本轮定位）：classList 元素面 → location 定义顺序（document.location undefined）→ window 别名/类构造函数（Element/Document/RTCPeerConnection 等）→ 按名全局（ANTT9/qOeu1/PnHD6）→ VM `new Proxy` null target（垫底）。
- 当前 Node 版状态：errors=0、fo 提交产出（bodyLen ~2188）、Python urllib 发送得 HTTP 200（无 cf-chl-out，形式接受）；**eb 提交未产出、clearance 未签发**——Proxy 垫底改变 VM 探测分支。如实记录：serverAccepted 证据仍属 RuyiDOM 诊断层。

### 2026-08-15 提交链路完整闭环（第三里程碑）

- **根因（最终）**：我的 setTimeout/setInterval 诊断包装器丢弃了原生变长参数——`setTimeout(P7,100,Ii,Ic)` 的第 3/4 参数被吞，P7 收到 (undefined,undefined,undefined) → `open("POST","undefined")` + `J["DCkwl7"]` 崩溃。修复为 arguments 全量透传后 errors=0。
- IY 嵌套机（IQ 回调）程序串 `0,3,2,4,1`：case 4 构建数据映射 Ic（cpza4/kwYu6/Cplz9/zcNj0/bACR4/gAMzq7/NWUB3/WpIu5/yRMqb7/jRwR8/yTXuH8/NGYVs4/yCCo2/ucBTZ7/InHf7/riWe2/YIjU8/qOeu1/PnHD6/IfWx3/RGOD3/QnRk5 21 字段）→ case 1 调度 setTimeout(P7,100,Ii,Ic)（此时 Ii=string /fo/ URL、Ic=object）。
- IY case 11 构建 /fo/ 提交 URL：`J[ZZ(1847)](J[ZZ(1962)](J[ZZ(1352)],_cf_chl_opt[ZZ(1408)])+'/fo/478345907:1786773913:H-v1Ic.../'+_cf_chl_opt[ZZ(1755)],'/')+_cf_chl_opt[ZZ(759)]`。
- **提交实证**：3 次 POST `/cdn-cgi/challenge-platform/h/g/fo/478345907:1786773913:H-v1Ic.../a2b6539108bf25c6/{cH-token}`（与 Reqable fo 模板一致）+ eb/managed POST；body = 完整 $ 分隔指纹载荷；P7 轮询器 4 次带参调用（Z=string,J=object,IV=number）。
- 已知未决：字符串表 ZZ 偏移并非全局 475（_cf_chl_opt 实际在 entry 1371→键 1846，DCkwl7 在 536→1011）——静态解码需按函数族分别确认；运行时解码已全部验证。

## Next Minimal Action

- Action: ① 在纯 Node 中实现独立 iframe `vm.Context`、`parent/postMessage`、动态 script/iframe loader；② 接入同一 fresh session 的 XHR response callback，观察 FO response 是否生成动态上下文；③ 只有自然出现 form/document POST 后才做 parity 与 business readback。
- Required fresh evidence: 同一 fresh challenge 的 iframe HTML/script hash、请求/响应顺序和脱敏 response shape；禁止回放历史 FO body/cookie/token。
- Stop condition: `PQak3` 出现真实 define/闭包 return 并越过 eY，且 request boundary 对齐；否则保持 `serverAccepted=false`、`requestBoundaryAligned=false`。
### 2026-10-03 Turnstile iframe realm / PQak3

- RuyiTrace `000010_GET_200...` iframe HTML 的 inline script 为 238636 bytes，包含 `PQak3`、`xdiN1`、`runProgram`；`turnstile-api.js` 仅 86732 bytes，不含这些 producer 事实。
- Node frame canary `v8-20261003152520-xgv5ln` 执行该 script 后 `frameEval=ok`、`_cf_chl_opt` 21→37，并真实读取 `PQak3`；但 `framePqOwn=false`，没有 define、FO 或 response boundary。
- `runProgram` 的动态源码是 59 字符 VM wrapper，`xdiN1` 是队列写入函数，`BGgf6/SSvM5/HxNX2` 是 identity/trusted-types helper；其 function `toString` 均不含 `PQak3`。
- 结论：Node 目前缺的是 iframe 独立 realm、DOM/parent message、XHR response callback 与 FO response 驱动上下文；不把 `PQak3` 硬编码为 Window API，不回放 opaque FO body。

## 2026-10-03 生产 runtime iframe realm

- 第 1 刀：`runtime/lib/iframe-realm.js` + `node run.js frame`。父子各自 `vm.Context`，子 `parent/top` 指向父窗口代理；`postMessage` 只计数，XHR 离线只记 method/path 类别。脚本 238636 bytes，SHA-256 `05102bb5158cd0ba9a41329021f124cad8778a9a556db9a0e802b11c07115262`。
- 结果：`frameEval=ok`，`chlOptKeys=37`，`framePqType=undefined`，`framePqOwn=false`，`throwName=TypeError`（`h[bb(...)] is not a constructor`），`sendCount=0`，`boundary=boundary-unchanged`。
- `PQak3` 没有真实 define。抛错名与 own/type 相对 canary 未变，停止相邻字段；未投递 MessageEvent，未补假 DOM，未回放 FO。
- 下一刀阻塞：需要新的 constructor/response 事实才能动宿主面。在那之前不要做 postMessage 投递或 querySelector 枚举。gate 保持 not-ready / false。
- 证据：`agent-notes/20261003-node-iframe-realm.md`。
