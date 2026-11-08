# 2026-09-28 方向资料：/fo/ 轮次角色与回放边界

Case: `psa-cf-5s-shield-20260815`  
范围：只读资料与本地笔记对照。不改求解代码，不开 RuyiDOM/trace，不提交目标站。  
**这不是 serverAccepted。web-case 仍应是 `patching`。**

不写 cookie/token/ray/header/body 原值，不写可用请求模板。

## 问题对照（四条）

| # | 方向问题 | 结论摘要 |
|---|---|---|
| 1 | `/fo/` 多轮各自交换什么 | 早期多为继续材料（脚本/探针载荷，`text/plain`）；中段可交错 Turnstile 子链材料；末轮偏通过面（`text/html` + clearance 名）。不能按「全局第 N 次」固定角色。 |
| 2 | 响应是否与当次请求绑定 | 文献与官方：通过面/令牌与求解上下文（会话、IP、客户端信号）绑定。头名 `cf-chl-gen` 多见继续轮响应；`cf-chl-out` / `cf-chl-out-s` 多见后段/接受面。公开文档不给这些头的密码学公式。 |
| 3 | 异会话 body 解码失败是否支持「不能回放」 | 支持。仓库文章明确禁止用旧 trace body 顶 live；本地异会话回放首包即 `InvalidCharacterError` 并截断链。 |
| 4 | 下一刀：继续补宿主 vs 承认响应面不可伪造 | **更应承认响应面不是宿主 patch 能伪造的**；下一刀应对齐「同会话真实应答回灌」，而不是优先补 createOffer settle。宿主仍要能消费合法回灌，但不能发明边缘响应。 |

## 来源条目

每条：标题、定位、它支持的那一句结论。

1. **Cloudflare 5s v2：/fo 与 form.submit 补环境**  
   - 定位：`article/web-reverse/cloudflare-5s-v2-fo-pipeline.md`  
   - 支持：`/fo` 分类为继续材料（大 `text/plain`、无 clearance）vs 主站接受面（`text/html` + clearance 名 + `cf-chl-out-s`）vs Turnstile 子链材料；回灌须带完整 envelope（含 `cf-chl-out` / `cf-chl-out-s`）；**不用旧 trace body 顶 live body**；Python 真实发送 + 回灌，Node 只自然出 body 并消费响应。

2. **INDEX 命中（仅指针，非全文）**  
   - 定位：`article/INDEX.md` → `cloudflare-5s-v2-fo-pipeline.md` / `products/cloudflare-5s-challenge.md`  
   - 支持：知识库把主站与 Turnstile 子 `/fo` 分计；`cf_clearance` 与 reload 都不是业务完成门。

3. **2026-09-28 /fo/ 有头浏览器顺序**  
   - 定位：`workspace/psa_solve/agent-notes/20260928-fo-browser.md`  
   - 支持：有头约 4 次 `/fo/` 皆 200、无 `eb`；末轮 set-cookie 名含 clearance 后回证书页；本地能发 `/fo/` 但 `served=false` 时链停在响应缺失；createOffer 未 settle 仍能发 `/fo/`。

4. **fo response extract / Replay**  
   - 定位：`workspace/psa_solve/agent-notes/20260928-fo-response.md`  
   - 支持：四轮响应体量级与头名角色（前段含 `cf-chl-gen`，后段含 `cf-chl-out` / `cf-chl-out-s`，末轮 clearance 名）；异会话回放第 1 条后 `InvalidCharacterError`，链停在 1 次 POST；**明确不是 serverAccepted，web-case 仍是 patching**。

5. **2026-09-28 /fo/ 本地边界判断**  
   - 定位：`workspace/psa_solve/agent-notes/20260928-fo-local.md`  
   - 支持：主假说是「没有可消费的 `/fo/` 响应」而非「发不出 `/fo/`」；createOffer settle 是次级观察；取消通道 ≠ 解题响应。

6. **How Challenges work（Cloudflare 官方）**  
   - 定位：`https://developers.cloudflare.com/cloudflare-challenges/concepts/how-challenges-work/`  
   - 支持：Managed Challenge 是多步客户端检查；**求解请求与签发挑战的 IP 不一致则求解无效**（上下文绑定，不是可随意异机回放的令牌）。

7. **Turnstile 概述 / 客户端渲染（官方）**  
   - 定位：`https://developers.cloudflare.com/turnstile` 、`.../turnstile/get-started/client-side-rendering/`  
   - 支持：Turnstile 与 Challenge Platform 同源；先跑一系列非交互 JS 探针再可能升交互；产出是一次性校验令牌（站点侧 siteverify），不是可跨会话复用的 opaque blob。

8. **Integrating Turnstile with the Cloudflare WAF（官方博客）**  
   - 定位：`https://blog.cloudflare.com/integrating-turnstile-with-the-cloudflare-waf-to-challenge-fetch-requests`  
   - 支持：通过后发 `cf_clearance` 类通过凭证；挑战在浏览器执行，fetch-only 路径拿不到同等通过面——侧面说明通过面依赖真实挑战会话，不是本地拼装。

9. **cdn-cgi / Challenges 产品说明（官方）**  
   - 定位：`https://developers.cloudflare.com/fundamentals/reference/cdn-cgi-endpoint/` 、`https://developers.cloudflare.com/cloudflare-challenges`  
   - 支持：`/cdn-cgi/challenge-platform/` 由边缘处理；挑战评估客户端信号。不公开 `/fo/` 载荷规格。

10. **GitLab 排障：HAR 与 `cf-chl-out`**  
    - 定位：`https://support.gitlab.com/hc/en-us/articles/20436860213020-Troubleshooting-Verify-you-are-human-redirect-loop`  
    - 支持：排障材料保留 `cf-chl-out` 头名（角色：挑战输出/排障相关响应头），不解释算法。

11. **公开观测：头名出现频率 / 流量扫描**  
    - 定位：gist「Most frequent HTTP headers」；urlscan / urlquery 对 `challenges.cloudflare.com` 的头名统计与样例摘要  
    - 支持：`cf-chl-gen`、`cf-chl-out`、`cf-chl-out-s`、请求侧 `cf-chl` / `cf-chl-ra` 是真实流量里的稳定**名字**；继续轮响应常伴 `cf-chl-gen`。不把任何样例值当规范。

12. **第三方 flow 笔记（scaredos/cfresearch 转述）**  
    - 定位：`https://github.com/scaredos/cfresearch`（及镜像摘要）  
    - 支持：旧 `flow/ov1` 路径上也出现 `cf-chl-out` / `cf-chl-out-s` 类输出头——说明「挑战输出头」跨路径族存在；**版本与字段布局会变，不能当当前 `/h/b/fo/` 字节级规格**。

13. **CF 请求链地图（本仓）**  
    - 定位：`workspace/psa_solve/agent-notes/20260928-cf-request-map.md`  
    - 支持：fo 响应体是加密/不透明 blob；成功口径是业务回读而非单次 HTTP 200；本地缺的是可消费应答映射，不是先猜响应明文。

## 文献 ↔ 本地证据对应（第 4 问展开）

| 主张 | 文献依据 | 本地证据 |
|---|---|---|
| 多轮：继续材料 →（可选子链）→ 通过面 | 文章 FO_CONTINUE / 子链 / FO_ACCEPTED；官方「一系列检查」 | 有头 4×200；体量级 大/更大/小/更小；头名从 `cf-chl-gen` 迁到 `cf-chl-out*`；末轮 clearance 名 |
| 响应与当次会话绑定 | 官方 IP/求解上下文；文章禁止旧 body 顶 live；Turnstile 令牌一次性 | 异会话回放 → `InvalidCharacterError`；当次本地 body sha256 每轮不同 |
| 宿主 patch 伪造不了边缘响应 | 文章：Python 真实发送 + 完整 envelope 回灌；Node 不直连、不硬拼 clearance | `served=false` 链停；取消通道 ≠ 解题响应；硬灌异会话包反而截断 |
| createOffer settle 不是当前闸 | （公开文献几乎不谈 RTC 与 `/fo/` 顺序） | 浏览器 fo 前已 settle；本地未 settle 仍 fo×3 |

**因此下一刀优先级：** 同会话、可消费的 `/fo/` 应答回灌（传输/材料面），而不是继续堆「缺失浏览器宿主」去伪造通过面。宿主缺口只在「回灌之后链仍停、且观测证明页面已读到合法 status/body」时再单面切开。

## 资料不足（显式）

- Cloudflare **未公开** `/fo/` 请求/响应的编解码、`cf-chl-gen` 与 body 的精确绑定公式、各轮语义的正式状态机。
- 第三方 teardown（crawlex、cfresearch）描述的是观测/旧路径，**不能**当作当前 `h/b` 字节协议。
- 公开文很少对比「补环境宿主」与「边缘响应」的分工；本结论主要靠仓库文章 + 本地回放失败 + 官方会话/IP 绑定旁证。
- 未在本切片验证：同会话 live 回灌后，页面是否必定进入第 2 次 `/fo/`（文章主张会，本地尚未用当次材料闭环证明）。

## 搜索预算备忘

- 已用：本地 20260928 笔记；`article/INDEX` 命中单篇精读；search-layer deep×3 子查询；client web_search×2。`gh` 本机不可用。未 WebFetch。未扫 `article/` 全库。
