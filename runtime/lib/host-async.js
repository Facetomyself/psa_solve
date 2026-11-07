/*
 * lib/host-async.js — Worker / 观察者 / 定时器 / URL / Blob
 *
 * 职责：异步宿主面（观察者 no-op、Worker 完整事件接口、定时器透传）。
 */
"use strict";

const vm = require("vm");
const blobSources = new Map();
const workerState = new WeakMap();

function blobText(blob) {
  const parts = blob && blob._parts;
  if (!Array.isArray(parts)) return "";
  try { return parts.map((part) => String(part)).join(""); }
  catch (e) { return ""; }
}

function trustedTypesFor() {
  const names = new Set();
  return {
    createPolicy(name, rules) {
      const key = String(name);
      if (names.has(key)) throw new TypeError("policy");
      names.add(key);
      const options = rules && typeof rules === "object" ? rules : {};
      function apply(kind, value) {
        const fn = options[kind];
        return typeof fn === "function" ? fn(value) : String(value);
      }
      return {
        createHTML(value) { return apply("createHTML", value); },
        createScript(value) { return apply("createScript", value); },
        createScriptURL(value) { return apply("createScriptURL", value); },
      };
    },
  };
}

function parentEvent(data) {
  return { data: data, origin: "", source: null, isTrusted: true, type: "message", ports: [] };
}

function stateFor(worker) {
  let state = workerState.get(worker);
  if (!state) {
    state = { onmessage: null, listeners: [], queue: [], inbound: [], scope: null };
    workerState.set(worker, state);
  }
  return state;
}

function emitParent(worker, data) {
  const state = stateFor(worker);
  const event = parentEvent(data);
  let delivered = false;
  if (typeof state.onmessage === "function") {
    delivered = true;
    try { state.onmessage.call(worker, event); } catch (e) {}
  }
  for (const listener of state.listeners) {
    delivered = true;
    try { listener.call(worker, event); } catch (e) {}
  }
  if (!delivered) state.queue.push(data);
}

function flushParent(worker) {
  const state = stateFor(worker);
  if (!state.queue.length) return;
  if (typeof state.onmessage !== "function" && state.listeners.length === 0) return;
  const queued = state.queue.splice(0);
  for (const data of queued) emitParent(worker, data);
}

function workerHandlerReady(state) {
  const scope = state.scope;
  if (!scope) return false;
  if (typeof scope.onmessage === "function") return true;
  return Array.isArray(scope._listeners) && scope._listeners.length > 0;
}

function deliverWorker(worker, data) {
  const state = stateFor(worker);
  const scope = state.scope;
  if (!scope) return;
  if (!workerHandlerReady(state)) {
    state.inbound.push(data);
    return;
  }
  const event = parentEvent(data);
  try {
    if (typeof scope.onmessage === "function") scope.onmessage.call(scope, event);
  } catch (e) {}
  for (const listener of scope._listeners || []) {
    try { listener.call(scope, event); } catch (e) {}
  }
}

function flushWorker(worker) {
  const state = stateFor(worker);
  if (!state.inbound.length || !workerHandlerReady(state)) return;
  const queued = state.inbound.splice(0);
  for (const data of queued) deliverWorker(worker, data);
}

function bootWorker(worker, script, page) {
  const state = stateFor(worker);
  const origin = page && page.location && page.location.origin ? String(page.location.origin) : "";
  const scope = {
    close() {},
    importScripts() {},
    postMessage(data) { emitParent(worker, data); },
    addEventListener(type, fn) {
      if (type === "message" && typeof fn === "function") {
        scope._listeners.push(fn);
        flushWorker(worker);
      }
    },
    removeEventListener() {},
    origin: origin,
    name: "",
    trustedTypes: trustedTypesFor(),
    crypto: page.crypto,
    performance: page.performance,
    atob: page.atob,
    btoa: page.btoa,
    navigator: page.navigator,
    setTimeout: page.setTimeout,
    clearTimeout: page.clearTimeout,
    setInterval: page.setInterval,
    clearInterval: page.clearInterval,
  };
  scope._listeners = [];
  let workerHandler = null;
  Object.defineProperty(scope, "onmessage", {
    configurable: true,
    enumerable: true,
    get() { return workerHandler; },
    set(fn) {
      workerHandler = typeof fn === "function" ? fn : null;
      flushWorker(worker);
    },
  });
  scope.self = scope;
  scope.globalThis = scope;
  scope.location = { href: origin ? origin + "/" : "", origin: origin };
  const ctx = vm.createContext(scope);
  state.scope = scope;
  state.ctx = ctx;
  try {
    vm.runInContext(script, ctx, { filename: "blob-worker.js", timeout: 1000 });
  } catch (e) {}
}

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
  // host-globals.js 已装真实 PerformanceObserver（getEntries 条目 + observe 投递，
  // 2026-11-07 消变体对拍定站 n=759 分叉根因）；仅在其缺席时兜底 Noop。
  if (typeof g.PerformanceObserver === "undefined") g.PerformanceObserver = NoopObserver;
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

  // ---- Worker（blob 脚本在独立 realm 执行；消息 origin 为空） ----
  g.Worker = class {
    constructor(url) {
      const state = stateFor(this);
      Object.defineProperty(this, "onmessage", {
        configurable: true,
        enumerable: true,
        get() { return state.onmessage; },
        set(fn) {
          state.onmessage = typeof fn === "function" ? fn : null;
          flushParent(this);
        },
      });
      this.onerror = null;
      this.onmessageerror = null;
      this.url = url;
      const script = blobSources.get(String(url || ""));
      if (typeof script === "string" && script) bootWorker(this, script, g);
    }
    postMessage(data) {
      deliverWorker(this, data);
    }
    addEventListener(type, fn) {
      if (type !== "message" || typeof fn !== "function") return;
      const state = stateFor(this);
      state.listeners.push(fn);
      flushParent(this);
    }
    removeEventListener(type, fn) {
      if (type !== "message") return;
      const state = stateFor(this);
      state.listeners = state.listeners.filter((listener) => listener !== fn);
    }
    dispatchEvent() { return true; }
    terminate() {
      const state = stateFor(this);
      state.scope = null;
      state.ctx = null;
    }
  };

  // ---- Blob / URL ----
  g.Blob = class Blob {
    constructor(parts, opts) { this._parts = parts; this.type = (opts && opts.type) || ""; }
  };
  g.URL = g.URL || {};
  g.URL.createObjectURL = function (blob) {
    const id = "blob:node/" + Math.random().toString(36).slice(2);
    blobSources.set(id, blobText(blob));
    return id;
  };
  g.URL.revokeObjectURL = (id) => { blobSources.delete(String(id || "")); };
  g.URLSearchParams = globalThis.URLSearchParams;

  // ---- atob/btoa 兜底（Node 20 自带） ----
  if (typeof g.atob !== "function") {
    g.atob = (s) => Buffer.from(s, "base64").toString("binary");
    g.btoa = (s) => Buffer.from(s, "binary").toString("base64");
  }
}

module.exports = { install };
