#!/usr/bin/env node
// make_instrumented.js — 独立生成 loopguard/hotp 插桩版 orchestrate。
// 插桩算法原样复制自 runtime/run.js（CF_LOOPGUARD / CF_HOT_SNAPSHOT 段），
// 保证 ruyijs 侧与 Node 侧对同一份 orchestrate 字节产生相同的循环 id 与
// __lc / __hotp 语义，供同字节 trace 对齐。
// 用法: node make_instrumented.js <in.js> <out.js> [limit]
//   环境: CF_HOT_SNAPSHOT=1 注入 __hotp 快照

"use strict";
const fs = require("fs");

const srcPath = process.argv[2];
const outPath = process.argv[3];
const limit = Number(process.argv[4] || process.env.CF_LOOPGUARD || 5000000);
const hot = process.env.CF_HOT_SNAPSHOT === "1";
const opTrace = new Set((process.env.CF_OP_TRACE || "").split(",")
  .map((s) => s.trim()).filter(Boolean).map(Number));
const opTargets = [];
if (!srcPath || !outPath) {
  console.error("usage: node make_instrumented.js <in.js> <out.js> [limit]");
  process.exit(2);
}

let orchJs = fs.readFileSync(srcPath, "utf8");
const before = orchJs;
let loopId = 0;
orchJs = orchJs.replace(/for\s*\(\s*;\s*;\s*\)/g, () => {
  loopId += 1;
  const v = "__lg" + loopId;
  return "for(var " + v + "=0;;)if(++" + v + ">" + limit +
    ")throw new Error('loopguard#" + loopId + " iter='+" + v + ");else ";
});

const loopMeta = [];
{
  let out = "";
  let i = 0;
  const n = orchJs.length;
  while (i < n) {
    const idx = orchJs.indexOf("for", i);
    if (idx < 0) { out += orchJs.slice(i); break; }
    const prev = idx > 0 ? orchJs[idx - 1] : "";
    const after = orchJs.slice(idx + 3, idx + 40);
    if (/[A-Za-z0-9_$]/.test(prev) || !/^\s*\(/.test(after)) {
      out += orchJs.slice(i, idx + 3);
      i = idx + 3;
      continue;
    }
    let j = idx + 3;
    while (j < n && /\s/.test(orchJs[j])) j++;
    if (orchJs[j] !== "(") { out += orchJs.slice(i, idx + 3); i = idx + 3; continue; }
    let depth = 0, k = j, inStr = null, esc = false;
    for (; k < n; k++) {
      const ch = orchJs[k];
      if (inStr) {
        if (esc) { esc = false; continue; }
        if (ch === "\\") { esc = true; continue; }
        if (ch === inStr) inStr = null;
        continue;
      }
      if (ch === "'" || ch === '"' || ch === "`") { inStr = ch; continue; }
      if (ch === "(") depth++;
      else if (ch === ")") { depth--; if (depth === 0) break; }
    }
    if (depth !== 0) { out += orchJs.slice(i, k + 1); i = k + 1; continue; }
    const header = orchJs.slice(j + 1, k);
    const parts = [];
    let cur = "";
    depth = 0; inStr = null; esc = false;
    for (let q = 0; q < header.length; q++) {
      const ch = header[q];
      if (inStr) {
        cur += ch;
        if (esc) esc = false;
        else if (ch === "\\") esc = true;
        else if (ch === inStr) inStr = null;
        continue;
      }
      if (ch === "'" || ch === '"' || ch === "`") { inStr = ch; cur += ch; continue; }
      if ("([{".includes(ch)) depth++;
      if (")]}".includes(ch)) depth--;
      if (ch === ";" && depth === 0) { parts.push(cur); cur = ""; continue; }
      cur += ch;
    }
    parts.push(cur);
    if (parts.length !== 3) { out += orchJs.slice(i, k + 1); i = k + 1; continue; }
    const cond = parts[1].trim();
    if (cond === "true" || cond === "!0") {
      const id = loopMeta.length;
      const bodyHead = orchJs.slice(k + 1, k + 600);
      const hm = bodyHead.match(
        /switch\s*\(\s*(.+?)\[\s*([A-Za-z_$][\w$]*(?:\[[^\[\]]*\])?)\s*\+\+\s*\]\s*\)/);
      let hotExpr = "";
      if (hot && hm) {
        const tbl = hm[1].trim();
        const ptr = hm[2];
        hotExpr = ",((globalThis.__lc[" + id + "]&65535)===1&&(function(){try{" +
          "globalThis.__hotp=[" + id + "," + ptr + ",(" + tbl + "||[]).length];" +
          "}catch(e){}}).call(this))";
      }
      if (hm && opTrace.has(id)) {
        opTargets.push({ id: id, expr: hm[0], table: hm[1].trim(), ptr: hm[2] });
      }
      const wrapped = "((globalThis.__lc=globalThis.__lc||[]),(globalThis.__lc[" + id +
        "]=(globalThis.__lc[" + id + "]||0)+1)" + hotExpr + ",(" + cond + "))";
      loopMeta.push({ id: id, at: j, head: "for(" + header.slice(0, 70) });
      out += orchJs.slice(i, j + 1) + parts[0] + ";" + wrapped + ";" + parts[2] + ")";
      i = k + 1;
      continue;
    }
    out += orchJs.slice(i, k + 1);
    i = k + 1;
  }
  orchJs = out;
}

// 第二遍：对 CF_OP_TRACE 指定的循环，把 switch(TABLE[PTR++]) 改写为
// switch((__opTmp=TABLE[PTR++], __op<id>.push(__opTmp), __opTmp))
// ——保留原求值与自增副作用，并把每条被执行指令值全量记入 globalThis.__op<id>。
let opApplied = 0;
for (const target of opTargets) {
  const count = orchJs.split(target.expr).length - 1;
  if (count !== 1) continue;
  const rec = "switch((globalThis.__opTmp=" + target.table + "[" + target.ptr + "++]," +
    "(globalThis.__op" + target.id + "=globalThis.__op" + target.id +
    "||[]).push(globalThis.__opTmp),globalThis.__opTmp))";
  orchJs = orchJs.replace(target.expr, rec);
  opApplied += 1;
}

fs.writeFileSync(outPath, orchJs);
fs.writeFileSync(outPath + ".meta.json", JSON.stringify({
  limit, hot, applied: orchJs !== before, forEver: loopId, loops: loopMeta,
  opTrace: { requested: Array.from(opTrace), applied: opApplied, targets: opTargets },
}, null, 1));
process.stderr.write("[make_instrumented] changed=" + (orchJs !== before) +
  " forEver=" + loopId + " loops=" + loopMeta.length +
  " limit=" + limit + " hot=" + hot +
  " opTrace=" + Array.from(opTrace).join(",") + " opApplied=" + opApplied + "\n");
