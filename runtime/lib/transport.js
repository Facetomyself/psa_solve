/*
 * lib/transport.js — XHR shim（真实网络 + 记录 + cookie/响应头浏览器语义）
 *
 * 职责：
 *  - XHR 经 Node https 真实发请求（相对 URL 用目标 origin 解析）
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
    const mod = parsed.protocol === "https:" ? https : http;
    const data = body == null ? undefined : Buffer.from(String(body));

    // 浏览器行为：默认 UA/Referer + 同源自动携带 document.cookie
    const headers = Object.assign({
      "User-Agent": cfg.CF_USER_AGENT,
      "Referer": cfg.CF_REFERER,
    }, self._headers);
    const cookie = String(g.document.cookie || "");
    if (cookie && !headers["Cookie"] && !headers["cookie"]) {
      headers["Cookie"] = cookie;
    }

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
