/*
 * lib/host-globals.js — window 别名 / 屏幕 / navigator / performance / 事件全局
 *
 * 职责：补齐 Node 缺失的浏览器全局对象面（值面），不含行为逻辑。
 */
"use strict";

function install(g, cfg) {
  // ---- window 别名与基础属性 ----
  g.window = g;
  g.self = g;
  g.top = g;
  g.parent = g;
  g.frames = g;
  g.content = g;
  g.globalThis = g;
  g.origin = cfg.TARGET.origin;
  g.isSecureContext = true;
  g.crossOriginIsolated = false;
  g.closed = false;
  g.opener = null;
  g.status = "";
  g.name = "";
  g.scrollX = 0;
  g.scrollY = 0;
  g.pageXOffset = 0;
  g.pageYOffset = 0;

  // ---- 屏幕/视口 ----
  g.innerWidth = 1920;
  g.innerHeight = 939;  // 对齐 RuyiTrace rt_20260929103550_341b734038 浏览器事实
  g.outerWidth = 1920;
  g.outerHeight = 1080;
  g.devicePixelRatio = 1;
  g.screen = { width: 1920, height: 1080, availWidth: 1920, availHeight: 1040, colorDepth: 24 };

  // ---- window 方法（no-op 面） ----
  g.scroll = () => {};
  g.scrollTo = () => {};
  g.scrollBy = () => {};
  g.focus = () => {};
  g.blur = () => {};
  g.close = () => {};
  g.open = () => null;
  g.alert = () => {};
  g.confirm = () => false;
  g.prompt = () => null;
  g.getSelection = () => null;
  g.stop = () => {};
  g.print = () => {};
  g.getComputedStyle = () => ({});
  g.matchMedia = () => ({ matches: false, addListener: () => {} });

  // ---- location（从目标 URL 派生） ----
  g.location = {
    href: cfg.CF_TARGET_URL,
    origin: cfg.TARGET.origin,
    protocol: cfg.TARGET.protocol,
    host: cfg.TARGET.host,
    hostname: cfg.TARGET.hostname,
    port: cfg.TARGET.port,
    pathname: cfg.TARGET.pathname,
    search: cfg.TARGET.search,
    hash: cfg.TARGET.hash,
    assign: () => {},
    replace: () => {},
    reload: () => {},
  };

  // ---- history ----
  g.history = { replaceState: () => {}, pushState: () => {}, go: () => {}, back: () => {} };

  // ---- navigator ----
  function gpuLimits() {
    return {
      maxTextureDimension1D: 8192,
      maxTextureDimension2D: 8192,
      maxTextureDimension3D: 2048,
      maxBindGroups: 4,
      maxBindingsPerBindGroup: 1000,
      maxBufferSize: 268435456,
      maxComputeWorkgroupSizeX: 256,
      maxComputeWorkgroupSizeY: 256,
      maxComputeWorkgroupSizeZ: 64,
      maxComputeInvocationsPerWorkgroup: 256,
    };
  }
  function gpuDevice() {
    return {
      features: new Set(["texture-compression-bc"]),
      limits: gpuLimits(),
      queue: {
        submit() {},
        writeBuffer() {},
        onSubmittedWorkDone() { return Promise.resolve(); },
      },
      createBuffer() {
        return {
          destroy() {},
          getMappedRange() { return new ArrayBuffer(0); },
          mapAsync() { return Promise.resolve(); },
          unmap() {},
        };
      },
      createShaderModule() { return {}; },
      createCommandEncoder() {
        return {
          finish() { return {}; },
          beginComputePass() {
            return { setPipeline() {}, dispatchWorkgroups() {}, end() {} };
          },
          beginRenderPass() { return { end() {} }; },
        };
      },
      createComputePipeline() { return {}; },
      createRenderPipeline() { return {}; },
      createBindGroup() { return {}; },
      createBindGroupLayout() { return {}; },
      createPipelineLayout() { return {}; },
      destroy() {},
    };
  }
  g.navigator = {
    userAgent: cfg.CF_USER_AGENT,
    language: "en-US",
    languages: ["en-US"],
    platform: "Win32",
    webdriver: false,
    sendBeacon: () => true,
    hardwareConcurrency: 8,
    cookieEnabled: true,
    maxTouchPoints: 0,
    doNotTrack: null,
    gpu: {
      requestAdapter() {
        return Promise.resolve({
          features: new Set(["texture-compression-bc"]),
          limits: gpuLimits(),
          isFallbackAdapter: false,
          requestDevice() { return Promise.resolve(gpuDevice()); },
        });
      },
      getPreferredCanvasFormat() { return "bgra8unorm"; },
    },
  };

  // ---- atob/btoa（对齐 ruyijs 引擎的宽容语义）----
  // 证据链（2026-11-06 bridge diag）：
  // 1) Node 内建 atob 不剥空白 → FO r1 响应处理抛 InvalidCharacterError；
  // 2) 修正后链推进（FO 响应即下一阶段 orchestrate，被注入执行），但其解码器
  //    喂给 atob 的字符超出 WHATWG 字母表（含 URL-safe 变体），说明 ruyijs 引擎
  //    atob 为宽容型（非法字符丢弃后解码）。Node 补环境按宽容语义对齐。
  g.atob = function (input) {
    const s = String(input).replace(/[^A-Za-z0-9+/\-_]/g, "");
    return Buffer.from(s, "base64").toString("latin1");
  };
  g.btoa = function (input) {
    const s = String(input);
    for (let i = 0; i < s.length; i++) {
      if (s.charCodeAt(i) > 0xff) {
        const err = typeof DOMException === "function"
          ? new DOMException("Out of range", "InvalidCharacterError")
          : Object.assign(new Error("Out of range"), { name: "InvalidCharacterError" });
        throw err;
      }
    }
    return Buffer.from(s, "latin1").toString("base64");
  };

  // ---- performance ----
  const perfNow = () => {
    const [s, ns] = process.hrtime();
    return s * 1000 + ns / 1e6;
  };
  // ruyijs ApiMonitor 证据（2026-11-07）：挑战脚本调用 mark×5 / clearMarks×4 /
  // getEntriesByType×3 / getEntries×2 —— mark 必须有状态可读回，clearMarks
  // 必须存在（缺失即 TypeError 断链）。语义对齐浏览器：mark 入条目表，
  // clearMarks(name?) 按名删或全删，getEntries* 从条目表读。
  //
  // 2026-11-07 消变体对拍定站（n=759 分叉根因）：orchestrate 遍历
  // performance.getEntries() 逐条调用处理函数（读 entryType/name/
  // requestStart/responseStart 等并编码进 FO 载荷），随后注册
  // PerformanceObserver({entryTypes:['resource','navigation']})。
  // ruyijs 引擎为 load_page 生成 navigation + 6 条 resource 条目；
  // Node 侧原实现 getEntries 只有 mark 表 → 返回 [] → 条目处理电路
  // 整段跳过 → atob 调用序列错位。故补 navigation/resource 条目表：
  // 条目由 run.js 在页面/脚本加载与 XHR 完成时经 __perfRecord 打点产生，
  // 数值取真实时钟（挑战接受真实浏览器级时序范围，不硬编码）。
  const perfMarks = [];
  const perfNav = [];
  const perfResources = [];
  const perfObservers = [];
  const PERF_TYPES = { mark: perfMarks, navigation: perfNav, resource: perfResources };
  function perfEntry(type, init) {
    const e = Object.assign({
      name: "",
      entryType: type,
      startTime: perfNow(),
      duration: 0,
    }, init || {});
    const bucket = PERF_TYPES[type] || perfMarks;
    bucket.push(e);
    // observer 投递（异步，对齐浏览器队列语义；observe 时已存在的条目不投递，
    // 除非 buffered:true —— 挑战代码的 wS 走的是主动 getEntries 遍历，不依赖此路）
    for (const ob of perfObservers) {
      if (!ob._types || ob._types.indexOf(type) === -1) continue;
      const cb = ob._cb;
      setTimeout(() => {
        try { cb.call(ob, [{ getEntries: () => [e] }], ob); } catch (err) {}
      }, 0);
    }
    return e;
  }
  g.__perfRecord = perfEntry;
  function allPerfEntries() {
    return perfNav.concat(perfResources, perfMarks)
      .sort((a, b) => a.startTime - b.startTime);
  }
  g.performance = {
    now: perfNow,
    timeOrigin: 0,
    getEntries: () => allPerfEntries(),
    getEntriesByType: (t) => {
      const type = String(t);
      const bucket = PERF_TYPES[type];
      return bucket ? bucket.slice() : [];
    },
    getEntriesByName: (n, t) => {
      const name = String(n);
      const pool = t != null && PERF_TYPES[String(t)] ? PERF_TYPES[String(t)] : allPerfEntries();
      return pool.filter((e) => e.name === name);
    },
    mark: (name) => {
      perfEntry("mark", {
        name: String(name == null ? "" : name),
        startTime: perfNow(),
        duration: 0,
      });
    },
    clearMarks: (name) => {
      if (name == null) {
        perfMarks.length = 0;
        return;
      }
      const target = String(name);
      for (let i = perfMarks.length - 1; i >= 0; i--) {
        if (perfMarks[i].name === target) perfMarks.splice(i, 1);
      }
    },
    measure: () => {},
    clearMeasures: () => {},
  };
  g.PerformanceObserver = class PerformanceObserver {
    constructor(cb) {
      this._cb = typeof cb === "function" ? cb : function () {};
      this._types = null;
      this._observed = false;
    }
    observe(opts) {
      const o = opts && typeof opts === "object" ? opts : {};
      if (Array.isArray(o.entryTypes)) {
        this._types = o.entryTypes.map(String);
      } else if (o.type != null) {
        this._types = [String(o.type)];
      }
      if (!this._observed) {
        perfObservers.push(this);
        this._observed = true;
      }
    }
    disconnect() {
      const i = perfObservers.indexOf(this);
      if (i !== -1) perfObservers.splice(i, 1);
      this._observed = false;
    }
    takeRecords() { return []; }
  };
  g.PerformanceEntry = function PerformanceEntry() {};
  g.PerformanceNavigationTiming = function PerformanceNavigationTiming() {};
  g.PerformanceResourceTiming = function PerformanceResourceTiming() {};

  // ---- 事件全局（window / document 共用同一组方法，按 this 分桶） ----
  g.addEventListener = addEventListener;
  g.removeEventListener = removeEventListener;
  g.dispatchEvent = dispatchEvent;
  g.postMessage = () => {};

  // ---- DOM 类构造函数（instanceof/原型检查面） ----
  const domClasses = [
    "HTMLElement", "HTMLDocument", "HTMLHtmlElement", "HTMLHeadElement",
    "HTMLBodyElement", "HTMLDivElement", "HTMLAnchorElement", "HTMLSpanElement",
    "HTMLScriptElement", "HTMLStyleElement", "HTMLLinkElement", "HTMLInputElement",
    "HTMLFormElement",
    "HTMLCanvasElement", "HTMLIFrameElement", "HTMLImageElement", "Image",
    "Document", "DocumentFragment", "CharacterData", "Text", "Comment", "Attr",
    "CSSStyleDeclaration", "EventTarget", "Element", "Node", "Event",
    "MouseEvent", "ErrorEvent", "MessageEvent", "SVGElement", "SVGSVGElement",
    // FO 下一阶段脚本（swc 编译）实扫描面：2026-11-06 diag 实测
    // ReferenceError: HTMLCollection is not defined → 补集合/遍历一族
    "HTMLCollection", "NodeList", "NamedNodeMap", "DOMTokenList",
    "HTMLAllCollection", "HTMLFormControlsCollection", "HTMLOptionsCollection",
    "DOMStringMap", "DOMStringList", "RadioNodeList",
    "RTCPeerConnection", "webkitRTCPeerConnection", "RTCSessionDescription",
    "RTCIceCandidate", "MediaStream", "MediaStreamTrack",
  ];
  for (const name of domClasses) {
    if (typeof g[name] === "undefined") g[name] = function () {};
  }
  // ruyijs ApiMonitor 证据（2026-11-07）：挑战脚本读 Event.isTrusted×8。
  // Firefox 语义：脚本构造（new Event）的事件 isTrusted===false，仅 UA 生成
  // 的事件为 true（host-async.js 的 parentEvent 已按 true 给消息事件）。
  // 空构造器缺 type/isTrusted → 读出 undefined 即分歧。
  g.Event = function (type, init) {
    const opts = init && typeof init === "object" ? init : {};
    this.type = String(type == null ? "" : type);
    this.bubbles = !!opts.bubbles;
    this.cancelable = !!opts.cancelable;
    this.isTrusted = false;
    this.target = null;
    this.currentTarget = null;
    this.defaultPrevented = false;
    this.eventPhase = 0;
    this.timeStamp = perfNow();
  };
  g.Event.prototype.preventDefault = function () {};
  g.Event.prototype.stopPropagation = function () {};
  g.Event.prototype.stopImmediatePropagation = function () {};
  g.AudioContext = undefined;
  g.OfflineAudioContext = undefined;
  g.SharedWorker = undefined;
  g.MessageChannel = class {
    constructor() { this.port1 = { postMessage: () => {} }; this.port2 = this.port1; }
  };

  // ---- 按名 window 全局占位（orchestrate 自身定义被环境分支跳过；语义待运行时揭示） ----
  // 与 UpvLO0/ZHfDS6 同族（见 patches.js）
  g.ANTT9 = function () {};
  g.qOeu1 = function () {};
  g.PnHD6 = function () {};
}

const listenerBuckets = new WeakMap();

function eventReceiver(target) {
  if (target === null || (typeof target !== "object" && typeof target !== "function")) return globalThis;
  return target;
}

function bucketsFor(target) {
  const key = eventReceiver(target);
  let buckets = listenerBuckets.get(key);
  if (!buckets) {
    buckets = new Map();
    listenerBuckets.set(key, buckets);
  }
  return buckets;
}

function addEventListener(type, listener) {
  if (typeof listener !== "function" && !(listener && typeof listener.handleEvent === "function")) return;
  const key = String(type);
  const buckets = bucketsFor(this);
  let list = buckets.get(key);
  if (!list) {
    list = [];
    buckets.set(key, list);
  }
  if (list.indexOf(listener) !== -1) return;
  list.push(listener);
}

function removeEventListener(type, listener) {
  const buckets = listenerBuckets.get(eventReceiver(this));
  if (!buckets) return;
  const list = buckets.get(String(type));
  if (!list) return;
  const index = list.indexOf(listener);
  if (index >= 0) list.splice(index, 1);
}

function dispatchEvent(event) {
  const receiver = eventReceiver(this);
  const buckets = listenerBuckets.get(receiver);
  if (!buckets) return true;
  const type = event && event.type != null ? String(event.type) : "";
  const list = buckets.get(type);
  if (!list || !list.length) return true;
  for (const listener of list.slice()) {
    if (typeof listener === "function") listener.call(receiver, event);
    else listener.handleEvent(event);
  }
  return true;
}

module.exports = { install };
