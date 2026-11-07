/*
 * lib/atob-trace.js — Node 侧 atob I/O 记录器（对拍 driver 用）
 *
 * 门控：CF_ATOB_TRACE=1 时启用；CF_ATOB_TRACE_FILE 指定落盘路径。
 * 语义：wrap globalThis.atob（先记录后委托，异常输入记 `!` 标记后重抛），
 * 不改解码行为；记录 {n, in, out|!} 到内存数组，进程 exit 时落盘 JSONL。
 * 记录为对拍 ground truth：与 ruyijs 引擎内同位 hook（capture_atob_values.py
 * v5 expose sink）产出的 (input,output) 对逐位 diff，定位键控流第一分歧。
 * 上限 20000 对（与 ruyijs 侧 SINK_LIMIT 一致），溢出只计数。
 */
"use strict";

function install(g) {
  if (process.env.CF_ATOB_TRACE !== "1") return;
  if (typeof g.atob !== "function") return;
  const LIMIT = 20000;
  const records = [];
  let overflow = 0;
  const orig = g.atob;
  const wrapped = function (input) {
    const s = String(input);
    let out;
    try {
      out = orig.call(g, s);
    } catch (e) {
      if (records.length < LIMIT) {
        records.push({ n: records.length, i: s, o: "!" + String(e && e.name || e) });
      } else {
        overflow++;
      }
      throw e;
    }
    if (records.length < LIMIT) {
      records.push({ n: records.length, i: s, o: String(out) });
    } else {
      overflow++;
    }
    return out;
  };
  // 保持 toString 面不变化意义不大（Node 侧无需伪装），但不覆盖 length/name
  g.atob = wrapped;
  const file = process.env.CF_ATOB_TRACE_FILE ||
    "atob-trace-" + Date.now() + ".jsonl";
  process.on("exit", () => {
    try {
      const fs = require("fs");
      const lines = [];
      for (const r of records) {
        lines.push(JSON.stringify({ n: r.n, i: r.i, o: r.o }));
      }
      lines.push(JSON.stringify({
        __summary: true, count: records.length, overflow,
      }));
      fs.writeFileSync(file, lines.join("\n") + "\n", "utf8");
    } catch (e) { /* 落盘失败不影响主流程 */ }
  });
}

module.exports = { install };
