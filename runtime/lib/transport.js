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

const https = require("https");
const http = require("http");
const { URL: URLImpl } = require("url");

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
      const reqId = "fo-" + (g.__captureRequestId = (g.__captureRequestId || 0) + 1);
      g.__patchResponses.push({ url: u, capture: reqId, status: "pending" });
      process.stdout.write(JSON.stringify({
        type: "runtime_request",
        request_id: reqId,
        method: self._method,
        url: u,
        headers,
        body: body == null ? "" : String(body),
      }) + "\n");
      g.__capturePending[reqId] = (envelope) => {
        self.status = envelope.status || 0;
        self.statusText = String(envelope.status || "");
        self.responseText = envelope.body || "";
        self.response = envelope.body || "";
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
        try { self.onreadystatechange && self.onreadystatechange(); } catch (e) {}
        try { self.onload && self.onload(); } catch (e) {}
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
          setCookie: String(sc || ""),
          bodyHead: text.slice(0, 300),
        });
        try { self.onreadystatechange && self.onreadystatechange(); } catch (e) {}
        try { self.onload && self.onload(); } catch (e) {}
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
      xhrSend(this, b);
    }
    abort() {}
  };
}

module.exports = { install };
