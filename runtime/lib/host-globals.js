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
  g.innerHeight = 1080;
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

  // ---- 事件全局（no-op） ----
  g.addEventListener = () => {};
  g.removeEventListener = () => {};
  g.dispatchEvent = () => true;
  g.postMessage = () => {};

  // ---- DOM 类构造函数（instanceof/原型检查面） ----
  const domClasses = [
    "HTMLElement", "HTMLDocument", "HTMLHtmlElement", "HTMLHeadElement",
    "HTMLBodyElement", "HTMLDivElement", "HTMLAnchorElement", "HTMLSpanElement",
    "HTMLScriptElement", "HTMLStyleElement", "HTMLLinkElement", "HTMLInputElement",
    "HTMLCanvasElement", "HTMLIFrameElement", "HTMLImageElement", "Image",
    "Document", "DocumentFragment", "CharacterData", "Text", "Comment", "Attr",
    "CSSStyleDeclaration", "EventTarget", "Element", "Node", "Event",
    "MouseEvent", "ErrorEvent", "MessageEvent", "SVGElement", "SVGSVGElement",
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

module.exports = { install };
