# 20260929 Cloudflare managed challenge 公开资料合成（只读）

检索：search-layer deep / intent=exploratory；中英各一组；client-native web search 补权威页。Grok 源多数 timeout，Exa/Tavily/原生仍可用。未发现需 `gh` 有界核对的高相关 GitHub issue/PR（命中多为 MDN content blob、skills 文档，非卡点讨论）。无会话句柄。

敏感约束：不写 cookie/token/ray/sitekey/证书编号、/fo/ 正文、CSP nonce；不写绕过配方、伪造 clearance、PoC。

---

## 结论（相对本地卡点）

1. **清关名出现 ≠ 挑战页脚本必然建表并 document 导航。**  
   官方模型把 `cf_clearance` 定位为「已通过客户端校验」的边缘侧通行凭证（含 challenge clearance 等级 + precursor 持续评估），用于后续请求是否再发挑战。Interstitial 路径的公开阶段大致是：挑战 HTML → `/cdn-cgi/challenge-platform/` 编排脚本 → flow 类结果提交 → 边缘接受后 Set-Cookie → **整页重载/导航到原目标**。研究笔记把「接受后 reload / document 导航」放在编排验收之后；官方未承诺「同文档内只要 cookie 名已在分区出现，脚本就一定创建 forms 并 POST」。本地「分区已有 cookie 名、forms=0、无证书 document POST、window.KP 未定义」更接近 **编排未走到验收后导航**，而不是「清关已消费完毕」。

2. **Turnstile / Managed 的公开阶段划分（高层面）。**  
   - Managed Challenge：边缘按信号动态选 Non-Interactive / Managed / Interactive；多数访客非交互通过。  
   - Turnstile：嵌入式小部件发一次性 token；可选 pre-clearance 再发同名 clearance cookie。  
   - Clearance 等级：Interactive > Managed > Non-Interactive；高等级覆盖低等级。  
   - Precursor（及更早的 JS Detections）：会话中持续改写 cookie 内状态，可在 Challenge Passage 未到期前削弱/作废有效清关并触发再挑战。  
   因此「cookie 名已下发」只说明边缘曾发出/更新过该名；是否进入「表单创建 + document POST」取决于挑战页脚本是否判定本轮探针/小部件完成，而不是 cookie 名本身。

3. **UA 覆盖成 Firefox 155 发行串后，仍会与真 155 分叉的公开信号（官方/Bugzilla/MDN 优先）。**  
   - **HTTP/3 / QUIC**：155 引入 QUIC v2 兼容协商（Bug 2059947）；Happy Eyeballs v3 曾默认后因 UDP 阻断场景回退问题在 155/156 关闭（Bug 2062892 / 2063452 / 2067488）。协议选择影响 JA4 的 `q…`（QUIC）与 `t…`（TCP）前缀。本地已用 alt-svc 把首包页打成 h3 且 Alt-Used 为真，说明「有 H3」本身不够对齐发行版栈。  
   - **TLS ClientHello / JA4**：UA 字符串不改 NSS/ClientHello。135 起 HTTP/3 默认带 post-quantum `X25519MLKEM768`（Bug 1941041 / 135 release notes），会显著改变 key_share / ClientHello 体积；155 相对 135 的公开差异更偏 QUIC 版本协商与连接竞速，而非再换一套全新 cipher 叙事。扩展顺序随机化、ECH（含 GREASE）属更早版本即有的长期行为。  
   - **Accept-Encoding / 头部顺序**：公开资料仍把默认 `gzip, deflate, br, zstd` 与头部序当作 JA4H 类信号；155 release notes / MDN 未见「默认 AE 序相对 135 大改」的权威条目。壳版本仍是 135.0a1 时，网络栈与发行 155.0.1 不对齐是预期，不是 UA 长度 80 能抹平的。

4. **「清关 cookie 已出现但挑战页仍不提交表单」的公开形态与归因。**  
   社区与第三方笔记常见的是：cookie 已 Set / 分区可见，但随后仍卡在挑战页、循环再挑战、或导航不发生。作者归因（高层面，不抄步骤）集中在：  
   - **TLS / JA3·JA4 与声明 UA 不一致**（官方亦写 clearance 绑定访客/设备，不可跨机复用）；  
   - **HTTP/2 vs HTTP/3 协议指纹**；  
   - **会话中途 precursor / JS Detections 改写同名 cookie**，挑战 clearance 被冲掉或降级；  
   - **挑战编排 JS 未完成**（环境信号不足），边缘虽曾下发 cookie 名，页面侧仍不进入验收后导航。  
   几乎没有权威材料把该形态单独归因成「只差 cookie 名」；版本号、TLS、HTTP 协议三类信号反复出现。这与本地「有头 155 对照能走完证书 document POST，RuyiDOM 壳 135 + UA 覆盖后有 cookie 名但 forms=0」一致：**缺口在编排完成条件 / 客户端网络身份，不在再找一个 clearance 名字。**

5. **对本地事实的边界（不外推）。**  
   - 清关响应长度类 3792→3488、forms=0、无证书 document POST、KP 未定义：公开资料只能解释为「挑战页未进入验收后导航」的观测相容，不能从公开文档反推出站点私有脚本门槛。  
   - 不要把解码首字节当成分数（遵任务约束）。  
   - 官方 troubleshooting 列的是不支持浏览器、CORS 不带 cookie、挑战循环等运维向条目，不是「半清关」专用诊断表。

---

## 来源条目

### 官方：Clearance 概念

- **题名**：Clearance · Cloudflare challenges docs  
- **URL**：https://developers.cloudflare.com/cloudflare-challenges/concepts/clearance/  
- **日期**：文档页（检索日 2026-09-29；无固定文章日）  
- **与本地卡点关系**：定义 challenge clearance 等级、precursor 可持续改写/作废、cookie 绑定访客与设备；解释「有 cookie 名」不等于会话已稳定可导航。  
- **不适用**：不描述挑战页何时 `document.createElement('form')` 或站点证书 path 的 document POST。

### 官方：Interstitial Challenge Pages / How Challenges work

- **题名**：Interstitial Challenge Pages；How Challenges work  
- **URL**：https://developers.cloudflare.com/cloudflare-challenges/challenge-types/challenge-pages/ ；https://developers.cloudflare.com/cloudflare-challenges/concepts/how-challenges-work/  
- **日期**：文档页（2026-09-29）  
- **与本地卡点关系**：Managed 动态选难度；挑战页是完整 HTML interstitial，通过后才服务原内容；阶段上强调「拦截 → 客户端完成 → 再放行」。  
- **不适用**：不保证 partial clearance 下同页建表行为；无 Firefox 壳版本差异说明。

### 官方：Precursor / Challenge Passage / Troubleshooting

- **题名**：Precursor；Challenge Passage；Challenge solve issues / Troubleshooting  
- **URL**：https://developers.cloudflare.com/cloudflare-challenges/precursor/ ；https://developers.cloudflare.com/cloudflare-challenges/challenge-types/challenge-pages/challenge-passage/ ；https://developers.cloudflare.com/cloudflare-challenges/troubleshooting/challenge-solve-issues/  
- **日期**：文档页（2026-09-29）  
- **与本地卡点关系**：Passage 默认约 30 分钟；Precursor 可在到期前再挑战；troubleshooting 覆盖循环与不支持客户端——与「卡在挑战页」表象相容。  
- **不适用**：无「cookie 已下发但 forms=0」的专门病例；无 TLS/JA4 对照表。

### 官方博客：Turnstile 与 WAF / pre-clearance

- **题名**：Integrating Turnstile with the Cloudflare WAF to challenge fetch requests  
- **URL**：https://blog.cloudflare.com/integrating-turnstile-with-the-cloudflare-waf-to-challenge-fetch-requests  
- **日期**：2023-09-28（博客文）  
- **与本地卡点关系**：澄清 interstitial 与嵌入式 Turnstile、pre-clearance 发同名 cookie 供后续 API/页面；阶段上 cookie 服务于「之后的请求」，不是挑战页未完成时的替代终点。  
- **不适用**：场景是站长集成 fetch，不是第三方研究卡点；无 Firefox 135/155 差分。

### 官方：JA3/JA4 fingerprint（Bot）

- **题名**：JA3/JA4 fingerprint · Cloudflare bot solutions docs；Advancing Threat Intelligence: JA4 fingerprints…  
- **URL**：https://developers.cloudflare.com/bots/additional-configurations/ja3-ja4-fingerprint/ ；https://blog.cloudflare.com/ja4-signals  
- **日期**：文档页 / 博客（JA4 signals 文约 2024）  
- **与本地卡点关系**：边缘显式消费 TLS/JA4 与跨请求信号；支撑「仅改 UA 不够」的公开依据。  
- **不适用**：不写挑战页表单创建条件；无「半清关」案例。

### 社区：同名 cookie 冲突

- **题名**：Cf_clearance cookie conflict between turnstile and javascript detections  
- **URL**：https://community.cloudflare.com/t/cf-clearance-cookie-conflict-between-turnstile-and-javascript-detections/827381  
- **日期**：帖内讨论（约 2025；检索见存）  
- **与本地卡点关系**：公开形态「cookie 被后续 JSD/precursor 类逻辑改写，通行预期落空」；归因偏产品共用 cookie / 会话更新，而非伪造步骤。  
- **不适用**：站长配置向；不是「壳 Firefox 版本」专题；勿当作操作手册。

### 研究笔记：cf-chl 编排阶段（第三方）

- **题名**：Inside the Cloudflare challenge platform（cf-chl orchestration 类笔记，crawlex）  
- **URL**：https://blog.crawlex.net/blog/cloudflare-challenge-platform-cf-chl/  
- **日期**：第三方笔记（检索 2026-09-29；以页内为准）  
- **与本地卡点关系**：把公开可观察阶段写成 编排 GET → flow POST → 接受后 reload + clearance；有助于对照本地「无表单/无 document POST」落在验收前。  
- **不适用**：非官方规格；含实现细节，本笔记只取阶段划分，不摘编探测/编解码步骤。

### 第三方综述：cookie 绑定与再挑战循环

- **题名**：Cloudflare cf_clearance: why it expires and how to stop the re-challenge loop（DEV / 转载类）  
- **URL**：https://dev.to/bshahin/cloudflare-cfclearance-why-it-expires-and-how-to-stop-the-re-challenge-loop-do9  
- **日期**：约 2026-06（文内/转载链）  
- **与本地卡点关系**：把「已有 clearance 仍循环」归因到绑定失效、指纹/会话不一致、超时——与「名在、导航无」同族表象。  
- **不适用**：含运维/自动化口吻；本任务不采纳其中任何复现或绕过段落。

### Mozilla：Firefox 135 release / PQ HTTP3

- **题名**：Firefox 135.0 release notes；Bug 1941041（mlkem768x25519 for HTTP/3）  
- **URL**：https://www.firefox.com/en-US/firefox/135.0/releasenotes/ ；https://bugzilla.mozilla.org/show_bug.cgi?id=1941041  
- **日期**：2025-02（135.0）  
- **与本地卡点关系**：壳基线 135.0a1 与「HTTP/3 默认 PQ key exchange」同代；UA 改成 155 不会改这笔 ClientHello 结构是否与发行 155 一致需另证。  
- **不适用**：不直接谈 Cloudflare 表单。

### Mozilla：Firefox 155 / QUIC v2 / Happy Eyeballs

- **题名**：Firefox 155 release notes；MDN Firefox 155；Bug 2059947；Bug 2062892 / 2067488  
- **URL**：https://www.firefox.com/en-US/firefox/155.0/releasenotes ；https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/155 ；https://bugzilla.mozilla.org/show_bug.cgi?id=2059947 ；https://bugzilla.mozilla.org/show_bug.cgi?id=2062892  
- **日期**：2026-09（155.0 / 155.0.1）  
- **与本地卡点关系**：有头对照 155.0.1 相对 135 壳的公开网络差分（QUIC v2 协商、连接竞速策略回退）；解释「同 UA 串、不同栈」为何仍可被边缘区分。  
- **不适用**：release notes 不提 Cloudflare；Happy Eyeballs 问题是加载卡住类，不是 clearance 语义。

### Mozilla：ECH / GREASE；Accept-Encoding

- **题名**：Security/Encrypted Client Hello（MozillaWiki）；MDN Accept-Encoding  
- **URL**：https://wiki.mozilla.org/Security/Encrypted_Client_Hello ；https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Accept-Encoding  
- **日期**：Wiki/MDN 持续页  
- **与本地卡点关系**：ECH（含 GREASE）与 AE 取值是 UA 覆盖后仍可能分叉的长期客户端信号；官方未宣称 155 相对 135 默认 AE 序大改。  
- **不适用**：无「挑战页不建表」因果链。

### 第三方协议指纹综述（仅作归因对照）

- **题名**：HTTP/2 and HTTP/3 Fingerprinting: Protocol-Level Bot Detection（Scrapfly 等综述类）  
- **URL**：https://scrapfly.io/blog/posts/http2-http3-fingerprinting-guide  
- **日期**：检索见存（约 2025–2026）  
- **与本地卡点关系**：公开把 H2/H3、头部序、TLS 列为机器人信号；支撑「Alt-Used=h3 仍可能因栈细节不一致失败」的归因方向。  
- **不适用**：厂商博客且常夹带工具推销；禁止当作操作指南。

---

## 检索备注

- 中英 deep 均已跑；Grok grounded 多次 timeout，不阻塞合成。  
- 无高相关 GitHub issue/PR → 未调用 pavedpath-code / `gh`。  
- 绕过类、求解器营销页仅作「存在该卡点表象」的弱旁证，正文不摘步骤。
