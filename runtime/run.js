/*
 * run.js — PSA CF 5s 盾 vanilla Node 补环境求解入口
 *
 * 用法：node run.js <challenge-page.html> <orchestrate.js> [__cf_bm]
 *   node run.js <page> <orch>                    求解并输出提交（不发真实提交）
 *   node run.js <page> <orch> <cookie>           求解并真实发送提交 + 报告响应
 *
 * 输出：stdout 单行 JSON {ok, submits, responses, errors, pageState}
 */
"use strict";
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const mode = process.argv[2];

// frame 模式：离线 iframe vm.Context。不加载 code.js，不发网络。
// node run.js frame
if (mode === "frame") {
  runOfflineFrame();
  return;
}

// verify 模式：用 code.js 的 XHR（Node 真实请求）验证页面，与提交同源
// node run.js verify <url> <cookie>
if (mode === "verify") {
  const verifyUrl = process.argv[3];
  const verifyCookie = process.argv[4] || "";
  if (!verifyUrl) {
    console.error("usage: node run.js verify <url> <cookie>");
    process.exit(2);
  }
  require(path.join(__dirname, "code.js"));
  global.document.cookie = verifyCookie;
  const xhr = new global.XMLHttpRequest();
  xhr.onreadystatechange = function () {
    if (xhr.readyState !== 4) return;
    const text = String(xhr.responseText || "");
    const head = text.slice(0, 4000);
    const titleMatch = head.match(/<title>([^<]*)<\/title>/);
    console.log(JSON.stringify({
      status: xhr.status,
      size: text.length,
      title: titleMatch ? titleMatch[1].trim() : "",
      hasNextData: head.includes("__NEXT_DATA__"),
      bodyHead: head.slice(0, 300),
      responses: global.__patchResponses || [],
    }));
    process.exit(0);
  };
  xhr.open("GET", verifyUrl);
  xhr.send(null);
  setTimeout(() => { console.log(JSON.stringify({ status: 0, size: 0, title: "", timeout: true })); process.exit(1); }, 25000);
  return;
}

const pagePath = process.argv[2];
const orchPath = process.argv[3];
const cookieArg = process.argv[4] || "";
const captureOnly = process.env.CF_CAPTURE_ONLY === "1";

if (!pagePath || !orchPath) {
  console.error("usage: node run.js <challenge-page.html> <orchestrate.js> [__cf_bm] | verify <url> <cookie> | frame");
  process.exit(2);
}

// 分支追踪插桩（--trace 环境变量开启）：
//  状态机 case 标签计数 + VM 调度器 opcode 序列（与 RuyiDOM 诊断期证据对比用）
if (process.env.CF_TRACE === "1") {
  const orchRaw = fs.readFileSync(orchPath, "utf8");
  const orchT = orchRaw
    .replace(/case`(\d+)`:/g, "case`$1`:global.__caseCount[$1]=(global.__caseCount[$1]||0)+1;")
    .replace(/case (\d+):(\w+)\[/g, "case $1:global.__vmSeq.push($1);$2[");
  fs.writeFileSync(orchPath + ".trace.js", orchT);
}

const pageHtml = fs.readFileSync(pagePath, "utf8");
let orchJs = fs.readFileSync(orchPath, "utf8");

// VM 调度器 default 抛空 Error 的诊断插桩：把 switch(km) 的 km 值带进异常消息。
// 证据（2026-11-06）：FO r1 响应驱动下一阶段 VM 程序在 default:throw Error() 崩溃，
// 空消息无法区分"opcode 未实现"还是"查表输入漂移"。CF_DIAGNOSTICS=1 时改写。
if (process.env.CF_DIAGNOSTICS === "1") {
  orchJs = orchJs.replace(/default:throw Error\(\)\}/g,
    "default:throw new Error('vm-default opcode='+(typeof km!=='undefined'?km:'?')+' hex='+(typeof km==='number'?(km>>>0).toString(16):'-'))}");
}

// 同步死循环看门狗（CF_LOOPGUARD=<迭代上限>）：挑战代码的 VM 程序执行器用
// `for(;;)` 调度（orchestrate 中常见唯一/少量 for(;;)；变量名每变体不同，不能
// 用定点锚）。FO r1 响应驱动的挑战代码在此挂死 >150s（2026-11-07 在线探测，
// CF_WATCHDOG 定位到 FO onreadystatechange 后不返回）。通用改写：
//   for(;;)<body>  →  for(var __lgN=0;;)if(++__lgN>limit)throw;else <body>
// 超限抛错 → transport/全局兜底记录 → 拿到挂死栈而非静默挂起。
if (process.env.CF_LOOPGUARD) {
  const limit = Number(process.env.CF_LOOPGUARD) || 5000000;
  // CF_OP_TRACE：逐 opcode 落盘（与 make_instrumented.js 相同的第二遍改写）。
  // "*" 记录所有匹配 switch(TABLE[PTR++]) 的循环；逗号分隔记录指定 id。
  // 每条序列限长 CF_OP_TRACE_LIMIT（默认 20000），防止热循环 12M 条爆内存。
  const opTraceAll = process.env.CF_OP_TRACE === "*";
  const opTraceIds = new Set((process.env.CF_OP_TRACE || "").split(",")
    .map((s) => s.trim()).filter((s) => s && s !== "*").map(Number));
  const opTraceLimit = Number(process.env.CF_OP_TRACE_LIMIT) || 20000;
  const opTargets = [];
  let loopId = 0;
  const before = orchJs;
  orchJs = orchJs.replace(/for\s*\(\s*;\s*;\s*\)/g, () => {
    loopId += 1;
    const v = "__lg" + loopId;
    return "for(var " + v + "=0;;)if(++" + v + ">" + limit +
      ")throw new Error('loopguard#" + loopId + " iter='+" + v + ");else ";
  });
  // for(...;true;/!0;) 循环计数（不抛错，仅累计到 globalThis.__lc[id]）：
  // VM 驱动循环常用这种形式，for(;;) 覆盖不到。扫描平衡括号，只改条件段。
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
        // CF_HOT_SNAPSHOT=1：低频（每 65536 次）把该循环的指令指针与指令表长度
        // 写入 globalThis.__hotp，供 inspector 在挂死窗口 evaluate 读取。用于判定
        // "有限推进（指针递增、表长有限）"vs"原地死循环（指针不动/回绕）"。
        // 循环体形如 {switch(TABLE[PTR++])...}，PTR 可能是成员表达式（nJ[1]）。
        const bodyHead = orchJs.slice(k + 1, k + 600);
        const hm = bodyHead.match(
          /switch\s*\(\s*(.+?)\[\s*([A-Za-z_$][\w$]*(?:\[[^\[\]]*\])?)\s*\+\+\s*\]\s*\)/);
        let hotExpr = "";
        if (process.env.CF_HOT_SNAPSHOT === "1" && hm) {
          const tbl = hm[1].trim();
          const ptr = hm[2];
          hotExpr = ",((globalThis.__lc[" + id + "]&65535)===1&&(function(){try{" +
            "globalThis.__hotp=[" + id + "," + ptr + ",(" + tbl + "||[]).length];" +
            "}catch(e){}}).call(this))";
        }
        if (hm && (opTraceAll || opTraceIds.has(id))) {
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
  // CF_OP_TRACE 第二遍：把目标循环的 switch(TABLE[PTR++]) 改写为记录版，
  // 保留原求值与 PTR 自增副作用，限长写入 globalThis.__op<id>。
  let opApplied = 0;
  for (const target of opTargets) {
    if (orchJs.split(target.expr).length - 1 !== 1) continue;
    const rec = "switch((globalThis.__opTmp=" + target.table + "[" + target.ptr + "++]," +
      "(globalThis.__op" + target.id + "=globalThis.__op" + target.id + "||[]).length<" +
      opTraceLimit + "&&globalThis.__op" + target.id +
      ".push(globalThis.__opTmp),globalThis.__opTmp))";
    orchJs = orchJs.replace(target.expr, rec);
    opApplied += 1;
  }
  if (opTargets.length) {
    process.stderr.write("[diag] opTrace requested=" +
      (opTraceAll ? "*" : Array.from(opTraceIds).join(",")) +
      " applied=" + opApplied + " limit=" + opTraceLimit + "\n");
  }
  process.stderr.write("[diag] loopguard " + (orchJs === before ? "NOT-APPLIED" : "applied x" + loopId) +
    " limit=" + limit + " loopcounters=" + loopMeta.length + "\n" +
    loopMeta.slice(0, 8).map((m) => "  #" + m.id + " at " + m.at + " " + m.head).join("\n") + "\n");
}

// eb 状态机函数调用追踪（诊断）：j[Jx(1853)] 是 eb 提交状态机（case 8 构造 eb URL）
// 记录调用次数与首参（program 串）——判断 Node 里 eb 链路为何未触发
{
  const EB_ANCHOR = "j[Jx(1853)]=function(J,x,O0,xd,gt,gu,gA,gE,gB,gH,gM,gL){";
  if (orchJs.includes(EB_ANCHOR)) {
    orchJs = orchJs.replace(
      EB_ANCHOR,
      "j[Jx(1853)]=function(J,x,O0,xd,gt,gu,gA,gE,gB,gH,gM,gL){global.__ebCall=(global.__ebCall||0)+1;global.__ebProg=(typeof J)+','+String(J).slice(0,120)+',x='+(typeof x)+','+String(x).slice(0,80);"
    );
  }
}

// 1. 加载补环境（code.js）
require(path.join(__dirname, "code.js"));

// 1.5 预执行脚本登记：页面 loader 会 appendChild(<script src=orchestrate>)，host-dom
// 现在会真实发起加载并执行。run.js 在 step 5 已同步执行同一份 orchestrate，登记
// 该 URL 让 host-dom 跳过二次执行（但保留 script.onload 时序——loader 的 onload
// 负责 history.replaceState 恢复原 URL，与浏览器/ruyijs 一致）。
let orchUrlEarly = "";
try {
  const lm = pageHtml.match(/a\.src\s*=\s*['"]([^'"]*orchestrate[^'"]*)['"]/);
  if (lm) orchUrlEarly = new URL(lm[1], "https://www.psacard.com").href;
} catch (e) { /* URL 解析失败则不登记 */ }
global.__psaPreExecutedScripts = new Set(orchUrlEarly ? [orchUrlEarly] : []);

// 2. 会话 cookie
let initialCookie = cookieArg;
if (captureOnly && process.env.CF_COOKIE_FILE) {
  initialCookie = fs.readFileSync(process.env.CF_COOKIE_FILE, "utf8").trim();
}
if (initialCookie) {
  for (const item of initialCookie.split(";")) {
    const cookie = item.trim();
    if (cookie.includes("=")) global.document.cookie = cookie;
  }
}

if (captureOnly) {
  let stdinBuffer = "";
  process.stdin.setEncoding("utf8");
  process.stdin.on("data", (chunk) => {
    stdinBuffer += chunk;
    while (stdinBuffer.includes("\n")) {
      const index = stdinBuffer.indexOf("\n");
      const line = stdinBuffer.slice(0, index).trim();
      stdinBuffer = stdinBuffer.slice(index + 1);
      if (!line) continue;
      try {
        const message = JSON.parse(line);
        if (message.type === "response") global.__deliverCapturedResponse(message);
      } catch (e) {
        errors.push({ stage: "ipc", message: "invalid response envelope" });
      }
    }
  });
}

// 3. 提取 403 页内联 init 脚本
const initMatch = pageHtml.match(/<script[^>]*>([\s\S]*?)<\/script>/);
const initJs = initMatch ? initMatch[1] : "";

// 4. 提取 _cf_chl_opt 预置（init 设置后 orchestrate 依赖）
const errors = [];
const ctx = vm.createContext(global);
try { vm.runInContext(initJs, ctx, { filename: "challenge-init.js" }); }
catch (e) { errors.push({ stage: "init", message: String(e && e.message || e).slice(0, 200) }); }

// Proxy 垫底已移入 code.js（模块化安装时设置，经 vm context 继承）

// 4.5 Performance 条目打点（2026-11-07 消变体对拍定站 n=759 分叉根因）：
// orchestrate 遍历 performance.getEntries() 逐条处理（读 entryType/name/
// requestStart/responseStart 编码进 FO 载荷）。ruyijs 引擎为 load_page 生成
// navigation + resource 条目，Node 侧原 getEntries 只有 mark 表 → 遍历整段
// 跳过 → atob 序列错位。此处按页面自身数据生成同构条目（run.js 无网络栈，
// orchestrate/静态资源由调用方喂入，条目名从 403 页 loader 脚本提取）。
if (typeof global.__perfRecord === "function") {
  try {
    const opt = global._cf_chl_opt || {};
    const zone = String(opt.cZone || "www.psacard.com");
    let path = String(opt.cUPMDTk || "/").split("?")[0];
    if (!path.startsWith("/")) path = "/" + path;
    const pageUrl = "https://" + zone + path;
    global.__perfRecord("navigation", {
      name: pageUrl, entryType: "navigation", startTime: 0,
      duration: 0, initiatorType: "navigation",
      fetchStart: 0, requestStart: 0, responseStart: 0, responseEnd: 0,
      domInteractive: 0, domContentLoadedEventStart: 0,
      domContentLoadedEventEnd: 0, domComplete: 0,
      loadEventStart: 0, loadEventEnd: 0,
      transferSize: 0, encodedBodySize: 0, decodedBodySize: 0,
      type: "navigate", redirectCount: 0, activationStart: 0,
    });
    let orchUrl = "";
    const lm = pageHtml.match(/a\.src\s*=\s*['"]([^'"]*orchestrate[^'"]*)['"]/);
    if (lm) {
      try { orchUrl = new URL(lm[1], pageUrl).href; } catch (e) {}
    }
    if (orchUrl) {
      const t = global.performance && typeof global.performance.now === "function"
        ? global.performance.now() : 0;
      global.__perfRecord("resource", {
        name: orchUrl, entryType: "resource",
        startTime: t, duration: 0, initiatorType: "script",
        fetchStart: t, requestStart: t, responseStart: t, responseEnd: t,
        transferSize: 0, encodedBodySize: orchJs.length,
        decodedBodySize: orchJs.length,
      });
    }
  } catch (e) { /* 打点失败不阻断求解 */ }
}

// 5. 执行 orchestrate（求解主流程）
//    document.currentScript：浏览器/ruyijs 里 orchestrate 由页面 loader 的
//    <script src=...ray=...> 元素加载执行，执行期 currentScript 指向该元素
//    （含 src/nonce）。run.js 直接 vm 执行等效脚本，需合成同构元素；否则挑战
//    读 currentScript 得到 null（api_log 证据：Document.currentScript 47 次，
//    解码窗口 45 次），键控流与环境期望不一致。
let orchCurrentScript = null;
try {
  if (global.document && typeof global.document.createElement === "function") {
    orchCurrentScript = global.document.createElement("script");
    const lm2 = pageHtml.match(/a\.src\s*=\s*['"]([^'"]*orchestrate[^'"]*)['"]/);
    if (lm2) {
      try { orchCurrentScript.setAttribute("src", new URL(lm2[1], "https://www.psacard.com").href); }
      catch (e) { orchCurrentScript.setAttribute("src", lm2[1]); }
    }
    const nm = pageHtml.match(/a\.nonce\s*=\s*['"]([^'"]+)['"]/);
    if (nm) orchCurrentScript.nonce = nm[1];
    global.document.currentScript = orchCurrentScript;
  }
} catch (e) { /* 合成失败不阻断 */ }
try {
  vm.runInContext(orchJs, ctx, { filename: "orchestrate.js", timeout: 60000 });
} catch (e) {
  errors.push({ stage: "orchestrate", message: String(e && e.message || e).slice(0, 200) });
} finally {
  try {
    if (orchCurrentScript && global.document) global.document.currentScript = null;
  } catch (e) {}
}

// 5.5 文档生命周期（2026-11-07 消变体对拍实测撤回）：ruyijs 引擎
// load_page 返回时 readyState 已为 'complete'（页面脚本与 load 事件在
// load_page 内同步完成），orchestrate 执行时 DOMContentLoaded/load 均已
// 派发过。此处若补派发反而制造引擎侧不存在的事件；挑战代码的
// 'loading' 分支两侧均不进入。故不派发，保持 readyState='complete'。

// 6. 全局错误兜底（异步回调里的异常不退出进程）
process.on("uncaughtException", (e) => {
  errors.push({
    stage: "async",
    message: String(e && e.message || e).slice(0, 200),
    stackHead: String(e && e.stack || "").split("\n").slice(0, 4).join(" | ").slice(0, 400),
  });
});
process.on("unhandledRejection", (e) => {
  errors.push({ stage: "rejection", message: String(e && e.message || e).slice(0, 200) });
});


// 7. 动态完成检测：clearance 出现或提交稳定后即输出（最长窗口兜底）
//    求解链实际完成时间远小于固定窗口——轮询 500ms 检测提前退出
//    ruyijs 参考链证据（2026-11-06）：FO 轮间隔带 GET/PoW，静默可 >10s；
//    capture 模式 deadline 110s（外层 bridge 120s 之内），非 capture 维持 30s。
const solveDeadline = Date.now() + (captureOnly ? 110000 : 30000);
const startTime = Date.now();

function urlClass(raw) {
  let path = String(raw || "");
  try { path = new URL(path, "https://www.psacard.com").pathname; } catch (e) {}
  if (path.includes("/cdn-cgi/challenge-platform") && path.includes("/fo")) return "challenge-fo";
  if (path.includes("orchestrate")) return "orchestrate-script";
  if (path.startsWith("/cert/")) return "cert-document";
  if (path.includes("favicon")) return "favicon";
  if (path.includes("challenge-platform")) return "challenge-platform";
  return "other";
}

function lengthClass(n) {
  const v = Number(n) || 0;
  if (v === 0) return "0";
  if (v < 1000) return "1-999";
  if (v < 5000) return "1000-4999";
  if (v < 20000) return "5000-19999";
  return "20000+";
}

function requestClasses() {
  return (global.__patchXhr || []).map((r) => ({
    method: r.m,
    urlClass: urlClass(r.u),
    bodyLengthClass: lengthClass(r.body ? String(r.body).length : 0),
  }));
}

function responseClasses() {
  return (global.__patchResponses || []).map((r) => ({
    urlClass: urlClass(r.url),
    status: typeof r.status === "number" ? r.status : null,
    bodyLengthClass: typeof r.bodyLength === "number" ? lengthClass(r.bodyLength) : "absent",
  }));
}

function finishOutput() {
  const submits = (global.__patchXhr || []).filter((r) => r.u && r.u.includes("challenge-platform"));
  const responses = global.__patchResponses || [];

  // 提取 clearance + 轮换 __cf_bm
  let clearance = "";
  let bmNew = "";
  for (const r of responses) {
    const sc = String(r.setCookie || "");
    for (const part of sc.split(",")) {
      const p = part.trim();
      if (p.startsWith("cf_clearance=")) clearance = p.split(";")[0];
      if (p.startsWith("__cf_bm=")) bmNew = p.split(";")[0];
    }
  }

  const out = captureOnly ? {
    type: "result",
    ok: Boolean(global.__captureHasClearance),
    elapsedMs: Date.now() - startTime,
    requestCount: global.__captureRequestId || 0,
    errorCount: errors.length,
    hasClearance: Boolean(global.__captureHasClearance),
    missingGlobals: global.__missingGlobals ? Array.from(global.__missingGlobals).slice(0, 60) : undefined,
    missingHostProps: global.__missingHostProps ? Array.from(global.__missingHostProps).slice(0, 60) : undefined,
  } : {
    ok: true,
    elapsedMs: Date.now() - startTime,
    submits: submits.map((r) => ({
      method: r.m,
      url: String(r.u).slice(0, 300),
      bodyLen: r.body ? r.body.length : 0,
      bodyHead: (r.body || "").slice(0, 120),
      fullBody: r.body || "",
    })),
    responses: responses.slice(0, 6),
    errors,
    pageState: {
      optKeys: Object.keys((global._cf_chl_opt) || {}).length,
      cookie: String(global.document.cookie),
      cfClearance: /cf_clearance/.test(String(global.document.cookie)),
    },
    clearance,
    bmNew,
    ebDiag: { call: global.__ebCall || 0, prog: String(global.__ebProg || "") },
    requestClasses: requestClasses(),
    responseClasses: responseClasses(),
  };
  if (captureOnly) {
    console.log(JSON.stringify(out));
    process.exit(0);
    return;
  }
  setTimeout(() => sameLeaseRead(out), 5000);
}

function sameLeaseRead(out) {
  const https = require("https");
  const cfg = require(path.join(__dirname, "lib", "config.js"));
  let parsed;
  try { parsed = new URL(cfg.CF_TARGET_URL); }
  catch (e) {
    out.readback = { status: 0, titleLen: 0, pageKind: "other", error: "bad-url" };
    console.log(JSON.stringify(out));
    process.exit(0);
    return;
  }
  const headers = {
    "User-Agent": cfg.CF_USER_AGENT,
    Referer: cfg.CF_REFERER,
  };
  const cookie = String((global.document && global.document.cookie) || "");
  if (cookie) headers.Cookie = cookie;
  const req = https.request(parsed, { method: "GET", headers }, (res) => {
    const buf = [];
    res.on("data", (c) => buf.push(c));
    res.on("end", () => {
      const text = Buffer.concat(buf).toString("utf8");
      const title = ((text.match(/<title>([^<]*)<\/title>/i) || [, ""])[1] || "").trim();
      const challenge = /just a moment/i.test(title) || res.statusCode === 403;
      out.readback = {
        status: res.statusCode || 0,
        titleLen: title.length,
        pageKind: challenge ? "challenge" : (res.statusCode === 200 ? "cert" : "other"),
        bodyLengthClass: lengthClass(text.length),
      };
      console.log(JSON.stringify(out));
      process.exit(0);
    });
  });
  req.on("error", () => {
    out.readback = { status: 0, titleLen: 0, pageKind: "other", error: "request-error" };
    console.log(JSON.stringify(out));
    process.exit(0);
  });
  req.setTimeout(20000, () => req.destroy());
  req.end();
}

// 轮询完成检测：500ms 间隔，clearance 出现或提交稳定 3s 即退出，30s 兜底
// CF_STABLE_MS 可覆盖"提交静默"阈值（探测/诊断用）：挑战 FO 轮间有 ~5s 定时器
//（PoW/Ot 回调），3s 静默会把正常的轮间等待误判为完成（2026-11-07 在线探测）。
function pollSolve() {
  const responses = global.__patchResponses || [];
  const hasClearance = responses.some((r) => /cf_clearance/.test(String(r.setCookie || "")));
  const submits = (global.__patchXhr || []).filter((r) => r.u && r.u.includes("challenge-platform"));
  const lastSubmitAt = global.__lastSubmitAt || 0;
  if (hasClearance || global.__captureHasClearance) return finishOutput();
  // capture 模式不用"提交静默 3s"早退：FO 轮间静默属正常（PoW/定时器驱动），
  // 且 submits 计数含 orchestrate GET，非完成信号。交由 clearance / deadline 收口。
  const stableMs = Number(process.env.CF_STABLE_MS || 3000);
  if (!captureOnly && submits.length >= 2 && Date.now() - lastSubmitAt > stableMs) return finishOutput();
  if (Date.now() > solveDeadline) return finishOutput();
  setTimeout(pollSolve, 500);
}
setTimeout(pollSolve, 500);

function classifyFrameBoundary(obs) {
  const message = String(obs.throwMessage || "");
  const domTypeError = obs.throwName === "TypeError" && (
    /innerText|querySelector|postMessage|\bparent\b|cannot read propert|不能读属性/i.test(message)
  );
  if (obs.framePqOwn === false && domTypeError) return "boundary-unchanged";
  if (obs.throwName && obs.throwName !== "TypeError") return "boundary-moved";
  if (obs.framePqOwn === true || (obs.framePqType && obs.framePqType !== "undefined")) return "boundary-moved";
  return "boundary-unchanged";
}

function runOfflineFrame() {
  const crypto = require("crypto");
  const iframeRealm = require(path.join(__dirname, "lib", "iframe-realm.js"));
  const cfg = require(path.join(__dirname, "lib", "config.js"));
  const packetPath = path.join(
    __dirname,
    "..",
    "evidence",
    "web",
    "ruyitrace",
    "rt_20260929103550_341b734038",
    "raw",
    "http_packet",
    "000010_GET_200_challenges.cloudflare.com_cdn-cgi_challenge-platform_h_b_turnstile_f_av0_rch_4crrq_0x4AA_56a09332_pid30840_400000016.http_packet.json"
  );
  const DRAIN_MS = 5000;

  function emit(payload, code) {
    console.log(JSON.stringify(payload));
    process.exit(code);
  }

  let packet;
  try {
    packet = JSON.parse(fs.readFileSync(packetPath, "utf8"));
  } catch (err) {
    emit({
      ok: false,
      mode: "frame",
      scriptBytes: 0,
      scriptSha256: "",
      frameEval: "error",
      chlOptKeys: null,
      framePqType: "undefined",
      framePqOwn: false,
      throwName: "Error",
      sendCount: 0,
      boundary: "blocked",
    }, 1);
    return;
  }

  const html = String(packet.responseBody && packet.responseBody.text || "");
  const scriptMatch = html.match(/<script[^>]*>([\s\S]*?)<\/script>/i);
  const script = scriptMatch ? scriptMatch[1] : "";
  const scriptBytes = Buffer.byteLength(script);
  const scriptSha256 = crypto.createHash("sha256").update(script).digest("hex");
  if (!script) {
    emit({
      ok: false,
      mode: "frame",
      scriptBytes: 0,
      scriptSha256: scriptSha256,
      frameEval: "error",
      chlOptKeys: null,
      framePqType: "undefined",
      framePqOwn: false,
      throwName: "Error",
      sendCount: 0,
      boundary: "blocked",
    }, 1);
    return;
  }

  const session = iframeRealm.createRealms({
    frameHref: String(packet.url || ""),
    frameHtml: html,
    parentHref: cfg.CF_TARGET_URL,
    userAgent: cfg.CF_USER_AGENT,
    timeoutMs: 20000,
  });

  function onHostError(err) {
    session.noteThrow(err instanceof Error ? err : new Error(iframeRealm.sanitizeMessage(err)));
  }
  process.on("uncaughtException", onHostError);
  process.on("unhandledRejection", onHostError);

  try {
    session.runFrameScript(script, "turnstile-iframe.js");
  } catch (err) {
    emit({
      ok: false,
      mode: "frame",
      scriptBytes,
      scriptSha256,
      frameEval: "error",
      chlOptKeys: null,
      framePqType: "undefined",
      framePqOwn: false,
      throwName: err && err.name || "Error",
      sendCount: 0,
      boundary: "blocked",
    }, 1);
    return;
  }

  setTimeout(() => {
    const obs = session.observe();
    session.dispose();
    emit({
      ok: obs.frameEval === "ok" && !obs.throwName,
      mode: "frame",
      scriptBytes,
      scriptSha256,
      frameEval: obs.frameEval,
      chlOptKeys: obs.chlOptKeys,
      framePqType: obs.framePqType,
      framePqOwn: obs.framePqOwn,
      throwName: obs.throwName,
      sendCount: obs.sendCount,
      boundary: classifyFrameBoundary(obs),
      parentPqOwn: obs.parentPqOwn,
      parentPostMessageCount: obs.parentPostMessageCount,
      sends: obs.sends,
      throwMessage: obs.throwMessage,
      constructorCalls: obs.constructorCalls,
      operations: obs.operations,
    }, 0);
  }, DRAIN_MS);
}
