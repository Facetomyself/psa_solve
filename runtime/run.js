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

// 5. 执行 orchestrate（求解主流程）
try {
  vm.runInContext(orchJs, ctx, { filename: "orchestrate.js", timeout: 60000 });
} catch (e) {
  errors.push({ stage: "orchestrate", message: String(e && e.message || e).slice(0, 200) });
}

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
function pollSolve() {
  const responses = global.__patchResponses || [];
  const hasClearance = responses.some((r) => /cf_clearance/.test(String(r.setCookie || "")));
  const submits = (global.__patchXhr || []).filter((r) => r.u && r.u.includes("challenge-platform"));
  const lastSubmitAt = global.__lastSubmitAt || 0;
  if (hasClearance || global.__captureHasClearance) return finishOutput();
  // capture 模式不用"提交静默 3s"早退：FO 轮间静默属正常（PoW/定时器驱动），
  // 且 submits 计数含 orchestrate GET，非完成信号。交由 clearance / deadline 收口。
  if (!captureOnly && submits.length >= 2 && Date.now() - lastSubmitAt > 3000) return finishOutput();
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
