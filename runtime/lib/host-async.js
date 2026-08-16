/*
 * lib/host-async.js — Worker / 观察者 / 定时器 / URL / Blob
 *
 * 职责：异步宿主面（观察者 no-op、Worker 完整事件接口、定时器透传）。
 */
"use strict";

function install(g) {
  // ---- 观察者（orchestrate 仅存在性/创建用途） ----
  class NoopObserver {
    constructor(cb) { this.cb = cb; }
    observe() {}
    disconnect() {}
    takeRecords() { return []; }
  }
  g.MutationObserver = NoopObserver;
  g.IntersectionObserver = NoopObserver;
  g.PerformanceObserver = NoopObserver;
  g.ResizeObserver = NoopObserver;

  // ---- 定时器（原生透传；orchestrate 用 setTimeout(fn, delay, ...args) 传上下文） ----
  {
    const origST = g.setTimeout;
    g.setTimeout = function (...args) { return origST(...args); };
    const origSI = g.setInterval;
    g.setInterval = function (...args) { return origSI(...args); };
  }
  g.requestAnimationFrame = (cb) => setTimeout(() => cb(performance.now()), 16);
  g.cancelAnimationFrame = clearTimeout;
  g.requestIdleCallback = (cb) => setTimeout(() => cb({ didTimeout: false }), 50);
  g.queueMicrotask = (f) => Promise.resolve().then(f);

  // ---- Worker（完整事件接口；orchestrate 当前仅指纹用途，消息无依赖） ----
  g.Worker = class {
    constructor(url) {
      this.url = url;
      this.onmessage = null;
      this.onerror = null;
      this.onmessageerror = null;
    }
    postMessage() {}
    addEventListener() {}
    removeEventListener() {}
    dispatchEvent() { return true; }
    terminate() {}
  };

  // ---- Blob / URL ----
  g.Blob = class Blob {
    constructor(parts, opts) { this._parts = parts; this.type = (opts && opts.type) || ""; }
  };
  g.URL = g.URL || {};
  g.URL.createObjectURL = () => "blob:node/" + Math.random().toString(36).slice(2);
  g.URL.revokeObjectURL = () => {};
  g.URLSearchParams = globalThis.URLSearchParams;

  // ---- atob/btoa 兜底（Node 20 自带） ----
  if (typeof g.atob !== "function") {
    g.atob = (s) => Buffer.from(s, "base64").toString("binary");
    g.btoa = (s) => Buffer.from(s, "binary").toString("base64");
  }
}

module.exports = { install };
