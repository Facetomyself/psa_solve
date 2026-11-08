# Turnstile iframe / PQak3 事实（2026-10-03）

## 结论

`turnstile-api.js` 不是完整 Turnstile 执行面。RuyiTrace 的 `000010_GET_200...` iframe HTML 内有一段 238636 bytes 的 inline script；该脚本包含 `PQak3`、`xdiN1` 与 `runProgram`，而 API resource（86732 bytes）不包含这三个 producer 事实。

## Node 对照

- canary：`v8-20261003151936-i5rosl`、`v8-20261003152132-h2taqe`、`v8-20261003152520-xgv5ln`。
- 只在独立副本中加载同一 browser artifact 的 iframe inline script，未改基线 runner、未联网、未回放 FO body/cookie。
- frame script 成功进入执行：`frameEval=ok`，`frameScriptLength=238636`；`_cf_chl_opt` 字段从 21 增到 37，说明资源确实不是空跑。
- parent/postMessage 与 DOM `innerText/querySelector` stub 逐层补齐后，仍为 `framePqType=undefined`、`framePqOwn=false`；trace 可见 frame 对 `PQak3` 的真实读取，随后因 DOM/状态分支报 TypeError。
- 同一 frame script 在真实 RuyiTrace 中跑在独立 execution contexts，并伴随 blob/eval 子 realm；Node 当前把它压在单一 global，不能把 frame 的 free identifier 当普通 host getter。

## 资源事实

- iframe HTML：约 258062 bytes，inline script 238636 bytes；`PQak3` 仅 1 次，未见 `var/let/const/function/window.PQak3` 声明。
- iframe script 的开头注册 `window.BGgf6/SSvM5/HxNX2` trusted-types helper；这解释了 Node API canary 中出现的同名 mirror，但不产生 `PQak3`。
- browser FO response 为 opaque text（例如 frame-side FO body 798300 bytes，未落入生产输入）；本轮不读取/回放 response 内容，只记录长度/hash/边界。

## 判定

当前缺口从“API resource 未执行”收敛为：`iframe HTML -> 独立 realm -> DOM/worker/message -> FO response -> callback` 没有迁移到 Node。`PQak3` 仍不是可证的 `window.PQak3` 常量，不能硬编码。

证据：`evidence/web/v8trace/v8-20261003152520-xgv5ln/`、`evidence/web/ruyitrace/rt_20260929103550_341b734038/raw/http_packet/000010_GET_200_challenges.cloudflare.com_cdn-cgi_challenge-platform_h_b_turnstile_f_av0_rch_4crrq_0x4AA_56a09332_pid30840_400000016.http_packet.json`。
