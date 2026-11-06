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
  g.performance = {
    now: perfNow,
    timeOrigin: 0,
    getEntries: () => [],
    getEntriesByType: () => [],
    getEntriesByName: () => [],
    mark: () => {},
    measure: () => {},
  };

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
