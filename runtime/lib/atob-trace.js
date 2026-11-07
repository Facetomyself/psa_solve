/*
 * lib/atob-trace.js — Node 侧 atob/btoa I/O 记录器（对拍 driver 用）
 *
 * 门控：CF_ATOB_TRACE=1 时启用；CF_ATOB_TRACE_FILE 指定落盘路径。
 * 语义：wrap globalThis.atob 与 globalThis.btoa（先记录后委托，异常输入记
 * `!` 标记后重抛），不改编解码行为；记录 {n, dir, in, out|!} 到内存数组，
 * 进程 exit 时落盘 JSONL。记录为对拍 ground truth：与 ruyijs 引擎内同位
 * hook（capture_atob_values.py v5 expose sink）产出的 (input,output) 对
 * 逐位 diff，定位键控流第一分歧。btoa 方向（2026-11-07 第三轮加）：第二层
 * 输入溯源需要编码方向证据（XOR 解密后的再编码点）。
 * 上限 20000 对（与 ruyijs 侧 SINK_LIMIT 一致），溢出只计数。
 */
"use strict";

function install(g) {
  if (process.env.CF_ATOB_TRACE !== "1") return;
  const LIMIT = 20000;
  const records = [];
  let overflow = 0;
  let seq = 0;

  function wrap(name, dir) {
    const orig = g[name];
    if (typeof orig !== "function") return;
    const wrapped = function (input) {
      const s = String(input);
      let out;
      try {
        out = orig.call(g, s);
      } catch (e) {
        if (records.length < LIMIT) {
          records.push({ n: seq++, dir, i: s, o: "!" + String(e && e.name || e) });
        } else {
          overflow++;
        }
        throw e;
      }
      if (records.length < LIMIT) {
        records.push({ n: seq++, dir, i: s, o: String(out) });
      } else {
        overflow++;
      }
      return out;
    };
    g[name] = wrapped;
  }
  wrap("atob", "d"); // decode
  wrap("btoa", "e"); // encode

  const file = process.env.CF_ATOB_TRACE_FILE ||
    "atob-trace-" + Date.now() + ".jsonl";
  // 周期增量落盘：Node 被外部 kill（timeout/驱动收尾）时不触发 exit handler，
  // 只靠 exit 落盘会丢全部记录（2026-11-07 replay 实测 NO-TRACE）。
  // 每 2s 全量重写；exit handler 兜底最后一次。
  function flush() {
    try {
      const fs = require("fs");
      const lines = [];
      for (const r of records) {
        lines.push(JSON.stringify({ n: r.n, dir: r.dir, i: r.i, o: r.o }));
      }
      lines.push(JSON.stringify({
        __summary: true, count: records.length, overflow,
      }));
      fs.writeFileSync(file, lines.join("\n") + "\n", "utf8");
    } catch (e) { /* 落盘失败不影响主流程 */ }
  }
  const timer = setInterval(flush, 2000);
  if (timer.unref) timer.unref();
  process.on("exit", flush);
}

module.exports = { install };
