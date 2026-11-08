/*
 * lib/transport.js — XHR shim（真实网络 + capture 桥接 + cookie/响应头浏览器语义）
 *
 * 职责：
 *  - 默认：XHR 经 Node https 真实发请求（相对 URL 用目标 origin 解析）
 *  - CF_CAPTURE_ONLY=1：XHR 不建真实连接，request record 经 stdout JSONL 输出，
 *    由上层（Python）真实发送并回灌 response envelope（stdin）触发 XHR 事件链
 *    —— Python 是唯一外网请求层（对齐 5s v2 bridge 协议）
 *  - 浏览器行为：同源自动附 Cookie；响应 Set-Cookie 应用（cookie jar 增量）
 *  - 完整 XHR 接口面（status/responseText/responseType/responseURL/on* 事件等）
 *  - 观测：__patchXhr（请求记录）/ __patchResponses（响应记录）供 run.js 输出
 */
"use strict";

const fs = require("fs");
const https = require("https");
const http = require("http");
const { URL: URLImpl } = require("url");

// CF_WATCHDOG=1：XHR 回调同步打点（fd2 直写）——定位响应驱动代码的同步挂死。
const WATCHDOG = process.env.CF_WATCHDOG === "1";
let wdSeq = 0;
function wdRun(label, fn) {
  if (!WATCHDOG) return fn();
  const seq = ++wdSeq;
  fs.writeSync(2, "[wd] enter " + seq + " " + label + "\n");
  const t0 = Date.now();
  try { return fn(); }
  finally { fs.writeSync(2, "[wd] exit " + seq + " " + label + " " + (Date.now() - t0) + "ms\n"); }
}

function install(g, cfg) {
  g.__patchXhr = [];
  g.__patchResponses = [];
  g.__capturePending = {};

  // 上层回灌 response envelope：{type, request_id, status, headers, set_cookies, body}
  g.__deliverCapturedResponse = function (message) {
    const cb = g.__capturePending[message.request_id];
    if (!cb) {
      g.__patchResponses.push({
        url: message.request_id, error: "no pending capture for request_id" });
      return;
    }
    delete g.__capturePending[message.request_id];
    cb(message);
  };

  function hasHeader(headers, name) {
    const want = String(name).toLowerCase();
    return Object.keys(headers || {}).some((key) => String(key).toLowerCase() === want);
  }

  function documentOrigin() {
    if (g.location && g.location.origin) return String(g.location.origin);
    return String((cfg.TARGET && cfg.TARGET.origin) || "");
  }

  function siteLabel(hostname) {
    const parts = String(hostname || "").toLowerCase().split(".").filter(Boolean);
    if (parts.length <= 2) return parts.join(".");
    return parts.slice(-2).join(".");
  }

  function fetchSite(parsed) {
    let doc;
    try { doc = new URLImpl(documentOrigin()); }
    catch (e) { return "cross-site"; }
    if (doc.origin === parsed.origin) return "same-origin";
    if (doc.protocol === parsed.protocol && siteLabel(doc.hostname) && siteLabel(doc.hostname) === siteLabel(parsed.hostname)) {
      return "same-site";
    }
    return "cross-site";
  }

  function acceptLanguageValue() {
    const nav = g.navigator || {};
    const listed = Array.isArray(nav.languages)
      ? nav.languages.map((item) => String(item || "").trim()).filter(Boolean)
      : [];
    const primary = listed[0] || (nav.language ? String(nav.language).trim() : "");
    if (!primary) return "";
    const parts = listed.length ? listed.slice() : [primary];
    const base = primary.split("-")[0];
    const hasBase = parts.some((item) => item.split(";")[0].toLowerCase() === base.toLowerCase()
      && item.split(";")[0].toLowerCase() !== primary.toLowerCase());
    if (base && !hasBase && base.toLowerCase() !== primary.toLowerCase()) parts.push(base + ";q=0.9");
    return parts.join(",");
  }

  function applyAutomaticRequestHeaders(self, parsed) {
    const headers = self._headers;
    const origin = documentOrigin();
    if (origin && !hasHeader(headers, "origin")) headers.Origin = origin;
    if (!hasHeader(headers, "sec-fetch-dest")) headers["Sec-Fetch-Dest"] = "empty";
    if (!hasHeader(headers, "sec-fetch-mode")) headers["Sec-Fetch-Mode"] = "cors";
    if (!hasHeader(headers, "sec-fetch-site")) headers["Sec-Fetch-Site"] = fetchSite(parsed);
    // XHR sets Accept to */* when the caller did not.
    if (!hasHeader(headers, "accept")) headers.Accept = "*/*";
    // Firefox sends this from navigator.language when the caller did not.
    const lang = acceptLanguageValue();
    if (lang && !hasHeader(headers, "accept-language")) headers["Accept-Language"] = lang;
  }

  function xhrSend(self, body) {
    const u = self._url;
    if (!u) return;
    let parsed;
    try {
      parsed = new URLImpl(u, u.startsWith("http") ? undefined
        : (g.location && g.location.origin) || cfg.TARGET.origin);
    } catch (e) {
      g.__patchResponses.push({ url: u, error: "URL parse: " + String(e.message || e) });
      return;
    }

    // 资源时序条目（2026-11-07 补环境缺口）：真实 Firefox / ruyijs 对每次 XHR
    // 生成 performance resource 条目（initiatorType=xmlhttprequest，script 加载
    // 为 script）。挑战代码在 FO 响应回调里读条目时序/名字参与键控解码；缺条目
    // → 键控流错位（修复前表现 vm-default 崩溃，补条目表后表现为长解码不收敛）。
    const perfT0 = g.performance && typeof g.performance.now === "function"
      ? g.performance.now() : Date.now();
    const perfInitiator = self.__perfInitiator || "xmlhttprequest";
    function perfRecordResource() {
      // 预登记条目去重：run.js step 4.5 已按 ruyijs 真值登记 orchestrate 脚本的
      // resource 条目；页面 loader 触发的真实脚本加载若再记一条，getEntries 遍历
      // 会多出条目 → 挑战代码编码进 FO 载荷的条目数错位。
      if (self.__psaSkipPerfRecord) return;
      if (typeof g.__perfRecord !== "function") return;
      try {
        const t1 = g.performance && typeof g.performance.now === "function"
          ? g.performance.now() : Date.now();
        g.__perfRecord("resource", {
          name: parsed.href,
          entryType: "resource",
          startTime: perfT0,
          duration: t1 - perfT0,
          initiatorType: perfInitiator,
          fetchStart: perfT0,
          requestStart: perfT0,
          responseStart: t1,
          responseEnd: t1,
          transferSize: 0,
          encodedBodySize: 0,
          decodedBodySize: 0,
        });
      } catch (e) {}
    }

    applyAutomaticRequestHeaders(self, parsed);

    // 浏览器行为：默认 UA/Referer + 同源自动携带 document.cookie
    const headers = Object.assign({
      "User-Agent": cfg.CF_USER_AGENT,
      "Referer": cfg.CF_REFERER,
    }, self._headers);
    const cookie = String(g.document.cookie || "");
    if (cookie && !headers["Cookie"] && !headers["cookie"]) {
      headers["Cookie"] = cookie;
    }

    if (cfg.CF_CAPTURE_ONLY) {
      // capture 桥接：request record 输出 stdout，挂起等待回灌
      // url 输出解析后的绝对地址（与真实分支语义一致：相对 URL 按 target origin 解析）
      const reqId = "fo-" + (g.__captureRequestId = (g.__captureRequestId || 0) + 1);
      g.__patchResponses.push({ url: parsed.href, capture: reqId, status: "pending" });
      process.stdout.write(JSON.stringify({
        type: "runtime_request",
        request_id: reqId,
        method: self._method,
        url: parsed.href,
        headers,
        body: body == null ? "" : String(body),
      }) + "\n");
      g.__capturePending[reqId] = (envelope) => {
        self.status = envelope.status || 0;
        self.statusText = String(envelope.status || "");
        // 无损搬运：driver 发 body_b64（latin1 字符串化），兼容旧 body 字段。
        // 证据：utf-8/replace 桥接把非 UTF-8 字节变 U+FFFD，VM opcode 流被毁
        //（ruyijs 走真实字节流无此问题）。XHR responseText 按 latin1 还原字节。
        if (typeof envelope.body_b64 === "string") {
          const buf = Buffer.from(envelope.body_b64, "base64");
          self.responseText = buf.toString("latin1");
        } else {
          self.responseText = envelope.body || "";
        }
        self.response = self.responseText;
        self.responseURL = u;
        self.readyState = 4;
        self._respHeaders = envelope.headers || {};
        // 浏览器行为：响应 Set-Cookie 应用（cookie jar 增量语义）
        const scArr = Array.isArray(envelope.set_cookies) ? envelope.set_cookies : [];
        if (g.document.__cookieSet) {
          scArr.forEach((c) => { g.document.__cookieSet(c); });
        }
        const scStr = scArr.join(",");
        if (/cf_clearance=/.test(scStr)) g.__captureHasClearance = true;
        // 回灌后 __patchResponses 的 pending 占位换成真实响应
        for (let i = g.__patchResponses.length - 1; i >= 0; i--) {
          if (g.__patchResponses[i].capture === envelope.request_id) {
            g.__patchResponses[i] = {
              url: u,
              status: envelope.status,
              setCookie: scStr,
              bodyHead: (envelope.body || "").slice(0, 300),
            };
            break;
          }
        }
        perfRecordResource();
        try { self.onreadystatechange && self.onreadystatechange(); }
        catch (e) {
          if (cfg.CF_DIAGNOSTICS) process.stderr.write(
            "[diag] xhr onreadystatechange threw: " + String(e && e.name || "") + ": " +
            String(e && e.message || "") + " | " + String(e && e.stack || e).slice(0, 1200) + "\n");
        }
        try { self.onload && self.onload(); }
        catch (e) {
          if (cfg.CF_DIAGNOSTICS) process.stderr.write(
            "[diag] xhr onload threw: " + String(e && e.stack || e).slice(0, 1200) + "\n");
        }
      };
      return;
    }

    const mod = parsed.protocol === "https:" ? https : http;
    const data = body == null ? undefined : Buffer.from(String(body));

    const req = mod.request(parsed, { method: self._method, headers }, (res) => {
      const buf = [];
      res.on("data", (c) => buf.push(c));
      res.on("end", () => {
        const text = Buffer.concat(buf).toString("utf8");
        self.status = res.statusCode || 0;
        self.statusText = String(res.statusCode || "");
        self.responseText = text;
        self.response = text;
        self.responseURL = u;
        self.readyState = 4;
        self._respHeaders = res.headers || {};
        // 浏览器行为：响应 Set-Cookie 应用（cookie jar 增量语义）
        const sc = res.headers["set-cookie"];
        const scArr = Array.isArray(sc) ? sc : (sc ? [String(sc)] : []);
        if (g.document.__cookieSet) {
          scArr.forEach((c) => { g.document.__cookieSet(c); });
        }
        g.__patchResponses.push({
          url: u,
          status: res.statusCode,
          bodyLength: text.length,
          setCookie: String(sc || ""),
          bodyHead: text.slice(0, 300),
        });
        // FO 请求/响应原始字节落盘（诊断域，CF_DUMP_FO_DIR 指定）：供离线回放
        // 与 ruyijs 真值对比。响应按原始 Buffer 写，避免 UTF-8 解码损伤字节流。
        if (process.env.CF_DUMP_FO_DIR && /\/fo\//.test(String(u))) {
          try {
            fs.mkdirSync(process.env.CF_DUMP_FO_DIR, { recursive: true });
            const seq = (g.__foDumpSeq = (g.__foDumpSeq || 0) + 1);
            const dir = process.env.CF_DUMP_FO_DIR;
            fs.writeFileSync(dir + "/fo-req-" + seq + ".bin",
              Buffer.concat([Buffer.from(String(self._method) + " " + u + "\n", "utf8"),
                Buffer.from(String(body == null ? "" : body), "utf8")]));
            fs.writeFileSync(dir + "/fo-resp-" + seq + "-" + (res.statusCode || 0) + ".bin",
              Buffer.concat(buf));
            fs.writeFileSync(dir + "/fo-resp-" + seq + ".json",
              JSON.stringify({ url: u, status: res.statusCode, headers: res.headers }));
          } catch (e) {}
        }
        // 与 capture 分支对齐：真实分支的异常不再静默（CF_DIAGNOSTICS 时落 stderr）
        perfRecordResource();
        const labelBase = self._method + " " + String(parsed.href).slice(0, 120);
        try {
          wdRun(labelBase + " onreadystatechange",
            () => { self.onreadystatechange && self.onreadystatechange(); });
        } catch (e) {
          if (cfg.CF_DIAGNOSTICS) process.stderr.write(
            "[diag] xhr onreadystatechange threw: " + String(e && e.name || "") + ": " +
            String(e && e.message || "") + " | " + String(e && e.stack || e).slice(0, 1200) + "\n");
        }
        try {
          wdRun(labelBase + " onload", () => { self.onload && self.onload(); });
        } catch (e) {
          if (cfg.CF_DIAGNOSTICS) process.stderr.write(
            "[diag] xhr onload threw: " + String(e && e.name || "") + ": " +
            String(e && e.message || "") + " | " + String(e && e.stack || e).slice(0, 1200) + "\n");
        }
      });
    });
    req.on("error", (e) => {
      self.status = 0;
      self.responseText = "";
      self.readyState = 4;
      g.__patchResponses.push({ url: u, error: String(e.message || e) });
      try { self.onreadystatechange && self.onreadystatechange(); } catch (err) {}
      try { self.onerror && self.onerror(e); } catch (err) {}
    });
    if (data) req.write(data);
    req.end();
  }

  g.XMLHttpRequest = class {
    constructor() {
      this.readyState = 0;
      this.status = 0;
      this.responseText = "";
      this.response = "";
      this.responseType = "";
      this.responseURL = "";
      this.responseXML = null;
      this.withCredentials = false;
      this.timeout = 0;
      this.upload = { addEventListener: () => {} };
      this.onreadystatechange = null;
      this.onload = null;
      this.onerror = null;
      this.onabort = null;
      this.ontimeout = null;
      this._method = "GET";
      this._url = null;
      this._headers = {};
      this._respHeaders = {};
    }
    open(m, u) {
      this._method = String(m).toUpperCase();
      this._url = String(u);
      this.readyState = 1;
      g.__patchXhr.push({ m: this._method, u: this._url, body: null });
    }
    setRequestHeader(k, v) { this._headers[k] = String(v); }
    getResponseHeader(k) {
      const h = this._respHeaders || {};
      const v = h[k] ?? h[String(k).toLowerCase()];
      return v == null ? null : (Array.isArray(v) ? v.join(", ") : String(v));
    }
    getAllResponseHeaders() {
      const h = this._respHeaders || {};
      return Object.entries(h)
        .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`)
        .join("\r\n");
    }
    send(b) {
      if (g.__patchXhr.length) g.__patchXhr[g.__patchXhr.length - 1].body = String(b || "");
      g.__lastSubmitAt = Date.now();
      // XHR send(USVString) sets this when the caller did not.
      if (typeof b === "string" && !hasHeader(this._headers, "content-type")) {
        this._headers["Content-Type"] = "text/plain;charset=UTF-8";
      }
      xhrSend(this, b);
    }
    abort() {}
  };
}

module.exports = { install };
