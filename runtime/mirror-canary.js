/*
 * v8trace Node runner：执行 orchestrate（challenge-fast profile）。
 * 最小 DOM/BOM 桩 + _cf_chl_opt 注入；envcall 事实由 patched Node 吐出。
 * 目的：本地缺口清单（对照 RuyiDOM 引擎的 IG 缺口定位）。
 */
"use strict";
const fs = require("fs");
const path = require("path");

const ROOT = "D:\\reverse_ENV\\workspace\\psa_solve\\challenge-material\\rt_20260928061614_ee71af43b2";
const FRAME_PACKET = "D:\\reverse_ENV\\workspace\\psa_solve\\evidence\\web\\ruyitrace\\rt_20260929103550_341b734038\\raw\\http_packet\\000010_GET_200_challenges.cloudflare.com_cdn-cgi_challenge-platform_h_b_turnstile_f_av0_rch_4crrq_0x4AA_56a09332_pid30840_400000016.http_packet.json";
const challengeHtml = fs.readFileSync(path.join(ROOT, "challenge-page.html"), "utf8");
let orchestrateJs = fs.readFileSync(path.join(ROOT, "chl-page-orchestrate.js"), "utf8");
console.log(JSON.stringify({sourceGateNames:["iU","iq","iR"], sourceHasIu:orchestrateJs.includes("function iU(")}));
// Diagnostic-only wrapper: record known gate entry/return without changing values.
for (const name of ["iU","iq","iR"]) { const marker="function " + name + "("; const pos=orchestrateJs.indexOf(marker);  if(pos>=0){ const brace=orchestrateJs.indexOf("{",pos); orchestrateJs=orchestrateJs.slice(0,brace+1)+"global.__gateTrace.push({name:\""+name+"\",phase:\"enter\"});"+orchestrateJs.slice(brace+1); } }
const turnstileJs = fs.readFileSync(path.join(ROOT, "turnstile-api.js"), "utf8");
const framePacket = JSON.parse(fs.readFileSync(FRAME_PACKET, "utf8"));
const frameHtml = String(framePacket.responseBody && framePacket.responseBody.text || "");
const frameScriptMatch = frameHtml.match(/<script[^>]*>([\s\S]*?)<\/script>/i);
const frameScript = frameScriptMatch ? frameScriptMatch[1] : "";
global.__stateWrites = []; global.__mirrorDebug = { timers: [], ops: [] };
const __origWindow = global.window;
global.__xdiCalls = []; global.__evalEvents = []; global.__defNames = [];
const __xdiN1Wrap = function(fn){ return function(){ global.__xdiCalls.push({argc:arguments.length,args:Array.prototype.slice.call(arguments,0,3).map(function(x){return {type:typeof x,ctor:x&&x.constructor&&x.constructor.name||"",keys:x&&typeof x==="object"?Object.keys(x).slice(0,8):[]};})}); return fn.apply(this,arguments); }; };
const originalEval = global.eval; global.eval = function(src){ var text=String(src); global.__evalEvents.push({kind:"eval",len:text.length}); var out=originalEval(src); var ev=global.__evalEvents[global.__evalEvents.length-1]; ev.returnType=typeof out; ev.returnCtor=out&&out.constructor&&out.constructor.name||""; ev.returnKeys=out&&typeof out==="object"?Object.keys(out).slice(0,20):[]; return out; }; const originalDefineProperty = Object.defineProperty; Object.defineProperty = function(target, prop, desc) { if (target===global || target===global.window || target===global._cf_chl_opt) global.__stateWrites.push({prop:String(prop),hasValue:Object.prototype.hasOwnProperty.call(desc,"value"),valueType:typeof desc.value,receiver:String(target===global?"global":target===global.window?"window":"opt")}); if (typeof desc.value==="function" && typeof prop==="string") global.__defNames.push(String(prop)); if (String(prop)==="xdiN1" && typeof desc.value==="function") desc.value=__xdiN1Wrap(desc.value); return originalDefineProperty(target,prop,desc); };
const FRAME_HASH = require("crypto").createHash("sha256").update(frameScript).digest("hex");
global.__gateTrace = []; global.__stateTrace = []; global.__callbackTrace = []; global.__itArgs = []; global.__stateWrites = []; global.__proxyReads = []; global.__xdiCalls = []; global.__evalEvents = []; global.__defNames = [];
const RESPONSE_STATES = [{status:200,state:"headers",bytes:798300},{status:200,state:"loading",bytes:117964},{status:200,state:"complete",bytes:6776,cfChlOut:true}];
const OPAQUE_FO = { bytes: 798300, sha256: "47d704c3b9ff5249e83bb784aa04ed275ee84bb2cc6c61e6d76aa1c6a53c265a", followup: { bytes: 117964, sha256: "unrecorded", final: { bytes: 6776, sha256: "unrecorded", hasCfChlOut: true } } };
const FRAME_DEBUG = process.env.FRAME_DEBUG === "1";
const frameUrl = String(framePacket.url || "https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/b/turnstile/frame");

// 从 403 页提取 _cf_chl_opt 字面量
function extractChlOpt(html) {
  const m = html.match(/window\._cf_chl_opt\s*=\s*(\{[\s\S]*?\});/);
  if (!m) throw new Error("no _cf_chl_opt in challenge html");
  return m[1];
}

// 最小 DOM/BOM 桩（仅结构，方法空实现；envcall 会记录真实调用点）
const emptyFn = function () { return undefined; };
const noop = function () {};
function HTMLScriptElement() {}
function makeElement(tagName, className) {
  const el = {
    tagName: String(tagName || "SCRIPT").toUpperCase(), style: {}, dataset: {}, children: [],
    setAttribute: noop, getAttribute: function () { return null; },
    appendChild: function (c) { return c; },
    insertBefore: function (c) { return c; },
    querySelector: function (selector) { return findClassElement(selector) || makeElement("DIV"); },
    querySelectorAll: function (selector) { const found = findClassElements(selector); return found.length ? found : [makeElement("DIV")]; },
    removeChild: noop, addEventListener: noop, removeEventListener: noop,
    dispatchEvent: noop, click: noop,
    submit: function () { global.__ruyiFormSubmit = true; },
    innerHTML: "", textContent: "", innerText: "", className: String(className || ""),
    firstElementChild: null,
    parentNode: { insertBefore: function (child) { return child; } },
  };
  if (el.tagName === "SCRIPT") Object.setPrototypeOf(el, HTMLScriptElement.prototype);
  const classes = new Set(el.className.split(/\s+/).filter(Boolean));
  el.classList = {
    contains: function (token) { return classes.has(String(token)); },
    add: function (token) {
      const value = String(token);
      if (value) classes.add(value);
      el.className = Array.from(classes).join(" ");
    },
    remove: function (token) {
      classes.delete(String(token));
      el.className = Array.from(classes).join(" ");
    },
  };
  return el;
}
function findClassElement(selector) {
  const match = /^\.([A-Za-z0-9_-]+)$/.exec(String(selector || ""));
  if (!match) return null;
  const wanted = match[1];
  const tagPattern = /<([A-Za-z][A-Za-z0-9:-]*)\b[^>]*\bclass=(["'])(.*?)\2[^>]*>/gi;
  let found;
  while ((found = tagPattern.exec(challengeHtml))) {
    const classes = found[3].split(/\s+/).filter(Boolean);
    if (classes.includes(wanted)) return makeElement(found[1], found[3]);
  }
  return null;
}
function findClassElements(selector) {
  const match = /^\.([A-Za-z0-9_-]+)$/.exec(String(selector || ""));
  if (!match) return [];
  const wanted = match[1];
  const out = [];
  const tagPattern = /<([A-Za-z][A-Za-z0-9:-]*)\b[^>]*\bclass=(["'])(.*?)\2[^>]*>/gi;
  let found;
  while ((found = tagPattern.exec(challengeHtml))) {
    const classes = found[3].split(/\s+/).filter(Boolean);
    if (classes.includes(wanted)) {
      const el = makeElement(found[1], found[3]);
      el.parentNode = { insertBefore: function (child) { return child; } };
      out.push(el);
    }
  }
  if (out.length === 0 && (wanted === "DywTL2" || wanted === "pFfL9" || wanted === "FWHsC3")) {
    const count = wanted === "DywTL2" ? 8 : 2;
    for (let i = 0; i < count; i += 1) {
      const el = makeElement("A", wanted);
      el.parentNode = { insertBefore: function (child) { return child; } };
      out.push(el);
    }
  }
  return out;
}
const documentStub = {
  createElement: function (t) { return makeElement(); },
  createElementNS: function (ns, t) { return makeElement(); },
  getElementsByTagName: function () { return []; },
  getElementById: function () { return makeElement("DIV"); },
  querySelector: function (selector) { return findClassElement(selector) || makeElement("DIV"); },
  querySelectorAll: function (selector) { const found = findClassElements(selector); return found.length ? found : [makeElement("DIV")]; },
  insertBefore: function (c) { return c; },
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
const turnstileCurrentScript = makeElement("SCRIPT");
turnstileCurrentScript.src = "https://challenges.cloudflare.com/turnstile/v0/b/d76008a69eab/api.js?onload=zaERg6&render=explicit";
turnstileCurrentScript.getAttribute = function (name) {
  return String(name).toLowerCase() === "src" ? turnstileCurrentScript.src : null;
};
documentStub.currentScript = turnstileCurrentScript;
const navigatorStub = {
  userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0",
  language: "en-US", languages: ["en-US"], platform: "Win32",
  hardwareConcurrency: 16, maxTouchPoints: 0,
  sendBeacon: function () { return false; },
  cookieEnabled: true, onLine: true,
  vendor: "Google Inc.",
};
global.window = new Proxy(global,{get:function(t,p,r){if(["_cf_chl_opt","location","navigator","document"].includes(String(p)))global.__proxyReads.push(String(p));return Reflect.get(t,p,r);},set:function(t,p,v,r){if(["_cf_chl_opt","location"].includes(String(p)))global.__stateWrites.push({prop:String(p),valueType:typeof v});return Reflect.set(t,p,v,r);}});
global.self = global;
global.top = global.window;
global.HTMLScriptElement = HTMLScriptElement;
global.document = documentStub;
global.navigator = navigatorStub;
global.location = documentStub.location;
global.history = { replaceState: noop, pushState: noop, length: 1 };
global.localStorage = { getItem: function () { return null; }, setItem: noop, removeItem: noop, clear: noop };
global.sessionStorage = { getItem: function () { return null; }, setItem: noop, removeItem: noop, clear: noop };
global.__baseTimeout = global.setTimeout;
global.__mirrorDebug.timers.push({delay:-1,fn:"base-installed"});
global.setTimeout = (function(orig){ return function(fn, delay){ global.__stateTrace.push({kind:"timer",delay:Number(delay)||0,fn:String(fn).slice(0,180)}); global.__mirrorDebug.timers.push({delay:Number(delay)||0, fn:String(fn).slice(0,100), scheduled:true}); var wrapped=function(){ global.__callbackTrace.push({fn:String(fn).slice(0,180),delay:Number(delay)||0,args:Array.prototype.slice.call(arguments).map(function(x){return {type:typeof x,ctor:x&&x.constructor&&x.constructor.name||"",keys:x&&typeof x==="object"?Object.keys(x).slice(0,16):[]};})}); global.__mirrorDebug.timers.push({delay:Number(delay)||0, fn:String(fn).slice(0,100), fired:true}); try { return fn.apply(this, arguments); } catch(e) { global.__mirrorDebug.lastError={message:String(e&&e.message||e),stack:String(e&&e.stack||"").split("\\n").slice(0,4)}; throw e; } }; return orig(wrapped, delay); }; })(global.setTimeout);
 global.__ruyiXhr = []; global.__deliveryEvents = [];
global.XMLHttpRequest = function () {
  this.readyState=0; this.status=0; this.responseText=""; this.response=""; this.responseURL=""; this.onreadystatechange=null; this.onload=null; this.onerror=null;
  this.open=function(m,u){global.__deliveryEvents.push({kind:"xhr",state:"request",method:String(m),url:String(u)});global.__ruyiXhr=global.__ruyiXhr||[];this._method=String(m);this._url=String(u);global.__ruyiXhr.push({m:this._method,u:this._url,body:null,responseState:"opened"});this.readyState=1;};
  this.send=function(b){var r=global.__ruyiXhr[global.__ruyiXhr.length-1];if(r){r.body=String(b||"");r.responseState="sent";}};
  this.__deliver=function(shape){ global.__deliveryEvents.push({state:shape.state||"headers",status:shape.status||200});this.status=shape.status||200;this.readyState=2;this.responseState=shape.state||"headers";if(this.onreadystatechange)this.onreadystatechange();this.readyState=3;this.responseText=shape.text||"";this.response=this.responseText;if(this.onreadystatechange)this.onreadystatechange();this.readyState=4;if(this.onreadystatechange)this.onreadystatechange();if(this.onload)this.onload();};
  this.setRequestHeader=noop; this.addEventListener=function(n,fn){this["on"+String(n)]=fn;}; this.abort=noop;
  this.getResponseHeader=function(){return null;}; this.getAllResponseHeaders=function(){return "";};
};global.fetch = function (url, options) { global.__deliveryEvents.push({kind:"fetch",url:String(url),state:"request"}); return Promise.resolve({ ok:true,status:200,headers:{get:function(){return null;}}, json:function(){return Promise.resolve({});}, text:function(){return Promise.resolve("");} }); };
const performanceEntries = [];
global.__performanceGetEntriesCalls = 0;
global.performance = {
  now: function () { return Date.now(); },
  timing: { navigationStart: Date.now() - 100 },
  getEntries: function getEntries() {
    global.__performanceGetEntriesCalls += 1;
    return performanceEntries.slice();
  },
  getEntriesByType: function getEntriesByType() {
    return [];
  },
};
global.screen = { width: 1920, height: 1080, availWidth: 1920, availHeight: 1040, colorDepth: 24, pixelDepth: 24 };
global.requestAnimationFrame = function (cb) { return 0; };
global.cancelAnimationFrame = noop;
global.setInterval = setInterval;
process.on("uncaughtException", function (e) { console.log(JSON.stringify({uncaught: String(e && e.message || e).slice(0,200), stack: String(e && e.stack || "").split("\\n").slice(0,4)})); });
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

// Source-aligned canary: model the bridge's separate Window/global identity.
const windowMirror = {
  window: null, self: null, top: null, document: documentStub,
  navigator: global.navigator, location: global.location, history: global.history,
  performance: global.performance, screen: global.screen,
  setTimeout: global.setTimeout, clearTimeout: global.clearTimeout,
  setInterval: global.setInterval, clearInterval: global.clearInterval,
  addEventListener: global.addEventListener, removeEventListener: noop,
  XMLHttpRequest: global.XMLHttpRequest, fetch: global.fetch,
  MutationObserver: global.MutationObserver, IntersectionObserver: global.IntersectionObserver,
  ResizeObserver: global.ResizeObserver, matchMedia: global.matchMedia,
  URLSearchParams: global.URLSearchParams, atob: global.atob, btoa: global.btoa,
};
windowMirror.window = windowMirror;
windowMirror.self = windowMirror;
windowMirror.top = windowMirror;
windowMirror.parent = windowMirror;
windowMirror.postMessage = noop;
documentStub.defaultView = windowMirror;
global.window = windowMirror;
global.self = windowMirror;
global.top = windowMirror;
const mirrorCode = "(function(){var g=this,win;try{win=document.defaultView;}catch(e){return;}if(!win||g===win)return;var cache=new WeakMap();function wrap(fn){var hit=cache.get(fn);if(hit)return hit;var wrapped=new Proxy(fn,{apply:function(targetFn,thisArg,args){if(thisArg===g)thisArg=win;return Reflect.apply(targetFn,thisArg,args);},construct:function(targetFn,args,newTarget){return Reflect.construct(targetFn,args,newTarget);},get:function(targetFn,prop,rec){if(prop==='toString')return function(){return Function.prototype.toString.call(targetFn);};return Reflect.get(targetFn,prop,rec);}});cache.set(fn,wrapped);return wrapped;}var bridge=new Proxy(win,{get:function(target,prop){var value=Reflect.get(target,prop,target);return typeof value==='function'?wrap(value):value;},set:function(target,prop,value,receiver){try{Object.defineProperty(target,prop,{configurable:true,writable:true,enumerable:true,value:value});}catch(e){}if(receiver&&receiver!==target){try{Object.defineProperty(receiver,prop,{configurable:true,writable:true,enumerable:true,value:value});}catch(e2){}}return true;},getPrototypeOf:function(target){return Reflect.getPrototypeOf(target);}});try{Object.setPrototypeOf(g,bridge);}catch(e3){}})();";

// 注入 _cf_chl_opt 并执行 orchestrate
(function main() {
  try {
    const optLiteral = extractChlOpt(challengeHtml);
    // 通过 eval 执行 init（设置 _cf_chl_opt）
    (0, eval)("window._cf_chl_opt = " + optLiteral + ";");
    (0, eval)(mirrorCode);
    // 执行 orchestrate
    (0, eval)(orchestrateJs);
    let turnstileEval = "ok";
    try {
      (0, eval)(turnstileJs);
    } catch (resourceError) {
      turnstileEval = String(resourceError && resourceError.name || resourceError) + ":" + String(resourceError && resourceError.message || resourceError).slice(0, 160);
    }
    let frameEval = "skipped";
    let frameError = "";
    try {
      const oldHref = windowMirror.location && windowMirror.location.href;
      const oldCurrentScript = documentStub.currentScript;
      const frameCurrentScript = makeElement("SCRIPT");
      frameCurrentScript.src = frameUrl;
      documentStub.currentScript = frameCurrentScript;
      if (windowMirror.location) windowMirror.location.href = frameUrl;
      (0, eval)(frameScript);
      frameEval = "ok";
      if (windowMirror.location) windowMirror.location.href = oldHref;
      documentStub.currentScript = oldCurrentScript;
    } catch (error) {
      frameEval = "error";
      frameError = String(error && error.name || error) + ":" + String(error && error.message || error).slice(0, 180);
    }
    const xhr = global.__ruyiXhr || [];
    const responseStateContract = RESPONSE_STATES;
    if (global.__ruyiXhr.length) { const last=global.__ruyiXhr[global.__ruyiXhr.length-1]; last.responseStateContract=RESPONSE_STATES; }
    global.__mirrorDebug.timers.push({fn:"report", fired:true});
    console.log(JSON.stringify({debug: global.__mirrorDebug, timerNames: global.__mirrorDebug.timers.map(x=>x.fn)}));
    if (global.__mirrorDebug) console.log(JSON.stringify(global.__mirrorDebug));
    console.log(JSON.stringify({gateTrace:global.__gateTrace,stateTrace:global.__stateTrace,callbackTrace:global.__callbackTrace,stateWrites:global.__stateWrites,proxyReads:global.__proxyReads,xdiCalls:global.__xdiCalls,evalEvents:global.__evalEvents,defNames:global.__defNames,stateWrites:global.__stateWrites,proxyReads:global.__proxyReads,xdiCalls:global.__xdiCalls,evalEvents:global.__evalEvents,defNames:global.__defNames}));
    const keys = Object.keys(global._cf_chl_opt || {});
    console.log(JSON.stringify({
      ok: true,
      chlOptKeys: keys.length,
      xhrCount: xhr.length,
      performanceGetEntriesCalls: global.__performanceGetEntriesCalls,
      turnstileEval: turnstileEval,
      frameEval: frameEval,
      frameError: frameError,
      frameScriptLength: frameScript.length,
      frameSha256: FRAME_HASH,
      opaqueFo: OPAQUE_FO,
      responseStateContract: responseStateContract,
      deliveryEvents: global.__deliveryEvents,
      framePqType: typeof windowMirror.PQak3,
      framePqOwn: Object.prototype.hasOwnProperty.call(windowMirror, "PQak3"),
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

// Canary only: stop after a short async window once the boundary facts are emitted.
global.__baseTimeout(function () { global.__reportDone=true; console.log(JSON.stringify({finalCallbackTrace:global.__callbackTrace,finalGateTrace:global.__gateTrace,finalStateTrace:global.__stateTrace})); process.exit(0); }, 5000);
