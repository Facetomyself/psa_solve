/*
 * v8trace Node runner：执行 orchestrate（challenge-fast profile）。
 * 最小 DOM/BOM 桩 + _cf_chl_opt 注入；envcall 事实由 patched Node 吐出。
 * 目的：本地缺口清单（对照 RuyiDOM 引擎的 IG 缺口定位）。
 */
"use strict";
const fs = require("fs");
const path = require("path");

const ROOT = "D:\\reverse_ENV\\workspace\\psa_solve\\challenge-material";
const challengeHtml = fs.readFileSync(path.join(ROOT, "challenge-page-fresh.html"), "utf8");
const orchestrateJs = fs.readFileSync(path.join(ROOT, "chl-page-orchestrate-fresh.js"), "utf8");

// 从 403 页提取 _cf_chl_opt 字面量
function extractChlOpt(html) {
  const m = html.match(/window\._cf_chl_opt\s*=\s*(\{[\s\S]*?\});/);
  if (!m) throw new Error("no _cf_chl_opt in challenge html");
  return m[1];
}

// 最小 DOM/BOM 桩（仅结构，方法空实现；envcall 会记录真实调用点）
const emptyFn = function () { return undefined; };
const noop = function () {};
function makeElement() {
  return {
    tagName: "SCRIPT", style: {}, dataset: {}, children: [],
    setAttribute: noop, getAttribute: function () { return null; },
    appendChild: function (c) { return c; },
    removeChild: noop, addEventListener: noop, removeEventListener: noop,
    dispatchEvent: noop, click: noop,
    submit: function () { global.__ruyiFormSubmit = true; },
    innerHTML: "", textContent: "", className: "",
  };
}
const documentStub = {
  createElement: function (t) { return makeElement(); },
  createElementNS: function (ns, t) { return makeElement(); },
  getElementsByTagName: function () { return []; },
  getElementById: function () { return null; },
  querySelector: function () { return null; },
  querySelectorAll: function () { return []; },
  head: makeElement(), body: makeElement(),
  documentElement: makeElement(),
  cookie: "",
  title: "",
  location: { href: "https://www.psacard.com/cert/143963534/psa", hostname: "www.psacard.com" },
  referrer: "",
  readyState: "complete",
  addEventListener: noop,
  createEvent: function () { return { initEvent: noop }; },
};
const navigatorStub = {
  userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0",
  language: "en-US", languages: ["en-US"], platform: "Win32",
  hardwareConcurrency: 16, maxTouchPoints: 0,
  sendBeacon: function () { return false; },
  cookieEnabled: true, onLine: true,
  vendor: "Google Inc.",
};
global.window = global;
global.self = global;
global.document = documentStub;
global.navigator = navigatorStub;
global.location = documentStub.location;
global.history = { replaceState: noop, pushState: noop, length: 1 };
global.localStorage = { getItem: function () { return null; }, setItem: noop, removeItem: noop, clear: noop };
global.sessionStorage = { getItem: function () { return null; }, setItem: noop, removeItem: noop, clear: noop };
global.XMLHttpRequest = function () {
  this.open = function (m, u) { global.__ruyiXhr = global.__ruyiXhr || []; global.__ruyiXhr.push({ m: String(m), u: String(u), body: null }); };
  this.send = function (b) { var r = global.__ruyiXhr[global.__ruyiXhr.length - 1]; if (r) r.body = String(b || ""); };
  this.setRequestHeader = noop; this.addEventListener = noop;
  this.abort = noop;
};
global.fetch = function () { return Promise.resolve({ ok: true, status: 200, json: function () { return Promise.resolve({}); }, text: function () { return Promise.resolve(""); } }); };
global.performance = { now: function () { return Date.now(); }, timing: { navigationStart: Date.now() - 100 } };
global.screen = { width: 1920, height: 1080, availWidth: 1920, availHeight: 1040, colorDepth: 24, pixelDepth: 24 };
global.requestAnimationFrame = function (cb) { return 0; };
global.cancelAnimationFrame = noop;
global.setInterval = setInterval;
global.clearInterval = clearInterval;
global.addEventListener = noop;
global.getComputedStyle = function () { return { getPropertyValue: function () { return ""; } }; };
global.MutationObserver = function () { this.observe = noop; this.disconnect = noop; };
global.IntersectionObserver = function () { this.observe = noop; };
global.ResizeObserver = function () { this.observe = noop; };
global.matchMedia = function () { return { matches: false, addListener: noop, addEventListener: noop }; };
global.URLSearchParams = URLSearchParams;
global.atob = atob; global.btoa = btoa;
global.Worker = function () { throw new Error("Worker unsupported"); };
global.Blob = Blob; global.FileReader = function () {};

// 注入 _cf_chl_opt 并执行 orchestrate
(function main() {
  try {
    const optLiteral = extractChlOpt(challengeHtml);
    // 通过 eval 执行 init（设置 _cf_chl_opt）
    eval("window._cf_chl_opt = " + optLiteral + ";");
    // 执行 orchestrate
    eval(orchestrateJs);
    const xhr = global.__ruyiXhr || [];
    const keys = Object.keys(global._cf_chl_opt || {});
    console.log(JSON.stringify({
      ok: true,
      chlOptKeys: keys.length,
      xhrCount: xhr.length,
      xhrUrls: xhr.slice(0, 5).map(function (r) { return String(r.u).slice(0, 200); }),
    }));
  } catch (error) {
    console.log(JSON.stringify({
      ok: false,
      error: String(error && error.message || error).slice(0, 300),
      stack: String(error && error.stack || "").split("\n").slice(0, 6).join(" | ").slice(0, 800),
    }));
  }
})();
