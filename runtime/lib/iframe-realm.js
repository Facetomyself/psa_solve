/*
 * lib/iframe-realm.js — 父窗口与 Turnstile iframe 各自的 vm.Context
 *
 * 第 1 刀只证明 realm 隔离和 inline script 执行。
 * parent.postMessage 只记次数与 data 的 typeof/constructor，不投递 MessageEvent。
 * XHR/fetch 只记 method 与 path 类别，不回放历史 body，不打开网络。
 * 不定义 PQak3，不把 process/Buffer/require/module/global 放进目标 realm。
 */
"use strict";

const vm = require("vm");
const nodeCrypto = require("crypto");

const NODE_LEAKS = ["process", "Buffer", "require", "module", "global"];
const DOM_CLASS_NAMES = [
  "HTMLElement", "HTMLDocument", "HTMLHtmlElement", "HTMLHeadElement",
  "HTMLBodyElement", "HTMLDivElement", "HTMLAnchorElement", "HTMLSpanElement",
  "HTMLScriptElement", "HTMLStyleElement", "HTMLLinkElement", "HTMLInputElement",
  "HTMLFormElement", "HTMLCanvasElement", "HTMLIFrameElement", "HTMLImageElement",
  "Image", "Document", "DocumentFragment", "CharacterData", "Text", "Comment",
  "Attr", "CSSStyleDeclaration", "EventTarget", "Element", "Node", "Event",
  "MouseEvent", "ErrorEvent", "MessageEvent", "SVGElement", "SVGSVGElement",
];

function pathClass(raw) {
  let path = String(raw || "");
  try {
    if (/^[a-z][a-z0-9+.-]*:/i.test(path)) path = new URL(path).pathname;
  } catch (err) { /* 非绝对 URL 时只切路径 */ }
  const queryAt = path.indexOf("?");
  if (queryAt >= 0) path = path.slice(0, queryAt);
  const hashAt = path.indexOf("#");
  if (hashAt >= 0) path = path.slice(0, hashAt);
  if (path.includes("/fo/")) return "fo";
  const parts = path.split("/").filter(Boolean).filter((part) => {
    if (part.length > 20) return false;
    if (/^[0-9a-f-]{8,}$/i.test(part)) return false;
    if (/^\d{6,}$/.test(part)) return false;
    return /^[a-z0-9._-]+$/i.test(part);
  });
  return parts.slice(0, 4).join("/") || "other";
}

function ctorName(value) {
  if (value === null) return "null";
  if (value === undefined) return "undefined";
  const ctor = value.constructor;
  if (ctor && typeof ctor.name === "string" && ctor.name) return ctor.name;
  return typeof value;
}

function sanitizeMessage(message) {
  return String(message || "")
    .replace(/https?:\/\/\S+/gi, "[url]")
    .replace(/\?[^\s)]*/g, "")
    .slice(0, 180);
}

function decodeEntities(text) {
  return String(text || "")
    .replace(/&hellip;/g, "...")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, "\"")
    .replace(/&#(\d+);/g, (_, n) => String.fromCharCode(Number(n)))
    .replace(/&#x([0-9a-f]+);/gi, (_, n) => String.fromCharCode(parseInt(n, 16)));
}

function parseAttrs(raw) {
  const attrs = {};
  const re = /([^\s=\/]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|(\S+)))?/g;
  let match;
  while ((match = re.exec(String(raw || "")))) {
    attrs[match[1].toLowerCase()] = match[2] || match[3] || match[4] || "";
  }
  return attrs;
}

function parseHtml(html) {
  const src = String(html || "").replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, "");
  const root = { nodeType: 1, tagName: "#ROOT", attrs: {}, children: [] };
  const stack = [root];
  const re = /<!--[\s\S]*?-->|<\/([a-zA-Z][\w:-]*)\s*>|<([a-zA-Z][\w:-]*)\b([^>]*?)(\/?)>|([^<]+)/g;
  let match;
  while ((match = re.exec(src))) {
    if (match[0].startsWith("<!--")) continue;
    if (match[1]) {
      const name = match[1].toUpperCase();
      while (stack.length > 1 && stack[stack.length - 1].tagName !== name) stack.pop();
      if (stack.length > 1) stack.pop();
      continue;
    }
    if (match[2]) {
      const el = {
        nodeType: 1,
        tagName: match[2].toUpperCase(),
        attrs: parseAttrs(match[3] || ""),
        children: [],
      };
      stack[stack.length - 1].children.push(el);
      const voidTag = /^(META|LINK|IMG|BR|HR|INPUT|BASE)$/.test(el.tagName);
      if (!voidTag && match[4] !== "/") stack.push(el);
      continue;
    }
    if (match[5]) {
      const text = decodeEntities(match[5]).replace(/\s+/g, " ").trim();
      if (!text) continue;
      stack[stack.length - 1].children.push({ nodeType: 3, textContent: text, children: [] });
    }
  }
  return root;
}

function findTag(node, tagName) {
  if (!node || node.nodeType !== 1) return null;
  if (node.tagName === tagName) return node;
  for (const child of node.children || []) {
    const found = findTag(child, tagName);
    if (found) return found;
  }
  return null;
}

function collectText(node) {
  if (!node) return "";
  if (node.nodeType === 3) return node.textContent || "";
  if (node.tagName === "SCRIPT" || node.tagName === "STYLE") return "";
  let out = "";
  for (const child of node.children || []) out += collectText(child);
  return out;
}

function createRealms(options) {
  const opts = options || {};
  const frameHref = String(opts.frameHref || "https://challenges.cloudflare.com/");
  const parentHref = String(opts.parentHref || "https://www.psacard.com/");
  const userAgent = String(opts.userAgent || "Mozilla/5.0");
  const frameHtml = String(opts.frameHtml || "");
  const timeoutMs = Number(opts.timeoutMs) > 0 ? Number(opts.timeoutMs) : 20000;

  const parentSandbox = {};
  const childSandbox = {};
  vm.createContext(parentSandbox, { name: "psa-parent-window" });
  vm.createContext(childSandbox, { name: "psa-iframe-window" });

  const state = {
    frameEval: "pending",
    thrown: null,
    sends: [],
    parentPostMessageCount: 0,
    parentPostMessageSamples: [],
    timerIds: new Set(),
    constructorCalls: [],
    operations: [],
  };

  function noteThrow(err) {
    if (state.thrown || !err) return;
    state.thrown = err;
    state.operations.push({op: "throw", name: err.name || "Error", message: sanitizeMessage(err.message)});
  }

  function recordConstructor(name, args) {
    if (state.constructorCalls.length >= 32) return;
    state.constructorCalls.push({
      realmId: "turnstile-frame",
      name: String(name || "anonymous"),
      argCount: args.length,
      args: args.slice(0, 4).map((value) => ({
        type: typeof value,
        ctor: ctorName(value),
        length: value && typeof value.length === "number" ? value.length : null,
      })),
    });
  }

  const links = { childWindow: childSandbox, childDocument: null };

  function recordSend(method, url, body) {
    state.sends.push({
      method: String(method || "").toUpperCase() || "GET",
      pathClass: pathClass(url),
      bodyLength: body == null ? 0 : String(body).length,
    });
  }

  function recordParentPostMessage(data) {
    state.parentPostMessageCount += 1;
    if (state.parentPostMessageSamples.length < 8) {
      state.parentPostMessageSamples.push({
        dataType: typeof data,
        dataCtor: ctorName(data),
      });
    }
  }

  function makeLocation(href) {
    let parsed;
    try { parsed = new URL(href); } catch (err) { parsed = new URL("https://challenges.cloudflare.com/"); }
    return {
      href: parsed.href,
      origin: parsed.origin,
      protocol: parsed.protocol,
      host: parsed.host,
      hostname: parsed.hostname,
      port: parsed.port,
      pathname: parsed.pathname,
      search: parsed.search,
      hash: parsed.hash,
      assign() {},
      replace() {},
      reload() {},
      toString() { return parsed.href; },
    };
  }

  function makeStorage() {
    const map = new Map();
    return {
      getItem: (key) => (map.has(key) ? map.get(key) : null),
      setItem: (key, value) => { map.set(String(key), String(value)); },
      removeItem: (key) => { map.delete(String(key)); },
      clear: () => { map.clear(); },
      key: (index) => Array.from(map.keys())[index] ?? null,
      get length() { return map.size; },
    };
  }

  function makeTimers(sandbox) {
    sandbox.setTimeout = function setTimeout(fn, delay) {
      const args = Array.prototype.slice.call(arguments, 2);
      const id = global.setTimeout(() => {
        state.timerIds.delete(id);
        try {
          if (typeof fn === "function") fn.apply(sandbox, args);
        } catch (err) {
          noteThrow(err);
        }
      }, Number(delay) || 0);
      state.timerIds.add(id);
      return id;
    };
    sandbox.clearTimeout = function clearTimeout(id) {
      state.timerIds.delete(id);
      global.clearTimeout(id);
    };
    sandbox.setInterval = function setInterval(fn, delay) {
      const args = Array.prototype.slice.call(arguments, 2);
      const id = global.setInterval(() => {
        try {
          if (typeof fn === "function") fn.apply(sandbox, args);
        } catch (err) {
          noteThrow(err);
        }
      }, Number(delay) || 0);
      state.timerIds.add(id);
      return id;
    };
    sandbox.clearInterval = function clearInterval(id) {
      state.timerIds.delete(id);
      global.clearInterval(id);
    };
    sandbox.queueMicrotask = function queueMicrotask(fn) {
      global.queueMicrotask(() => {
        try {
          if (typeof fn === "function") fn.call(sandbox);
        } catch (err) {
          noteThrow(err);
        }
      });
    };
  }

  function makeXhr() {
    function XMLHttpRequest() {
      this.readyState = 0;
      this.status = 0;
      this.responseText = "";
      this.response = "";
      this.responseURL = "";
      this.onreadystatechange = null;
      this.onload = null;
      this.onerror = null;
      this._method = "GET";
      this._url = "";
    }
    XMLHttpRequest.prototype.open = function open(method, url) {
      this._method = method;
      this._url = url;
      this.readyState = 1;
    };
    XMLHttpRequest.prototype.setRequestHeader = function setRequestHeader() {};
    XMLHttpRequest.prototype.addEventListener = function addEventListener() {};
    XMLHttpRequest.prototype.abort = function abort() {};
    XMLHttpRequest.prototype.getAllResponseHeaders = function getAllResponseHeaders() { return ""; };
    XMLHttpRequest.prototype.getResponseHeader = function getResponseHeader() { return null; };
    XMLHttpRequest.prototype.send = function send(body) {
      recordSend(this._method, this._url, body);
    };
    return XMLHttpRequest;
  }

  function selectorMatch(el, selector) {
    const text = String(selector || "").trim();
    if (!text || !el || el.nodeType !== 1) return false;
    let rest = text;
    let tag = "";
    const tagMatch = /^[a-zA-Z][\w:-]*/.exec(rest);
    if (tagMatch && !text.startsWith("#") && !text.startsWith(".")) {
      tag = tagMatch[0].toUpperCase();
      rest = rest.slice(tagMatch[0].length);
    }
    let id = "";
    let className = "";
    if (rest.startsWith("#")) id = rest.slice(1);
    else if (rest.startsWith(".")) className = rest.slice(1);
    else if (rest) return false;
    if (!tag && !id && !className) return false;
    if (tag && el.tagName !== tag) return false;
    if (id && el.id !== id) return false;
    if (className) {
      const classes = String(el.className || "").split(/\s+/);
      if (!classes.includes(className)) return false;
    }
    return true;
  }

  function queryAll(root, selector) {
    const out = [];
    const visit = (node) => {
      for (const child of node.children || []) {
        if (child.nodeType !== 1) continue;
        if (selectorMatch(child, selector)) out.push(child);
        visit(child);
      }
    };
    visit(root);
    return out;
  }

  function materialize(raw, doc) {
    if (!raw || raw.nodeType === 3) {
      return { nodeType: 3, textContent: raw ? raw.textContent || "" : "", children: [] };
    }
    const el = {
      nodeType: 1,
      tagName: raw.tagName,
      nodeName: raw.tagName,
      attrs: Object.assign({}, raw.attrs || {}),
      children: [],
      childNodes: null,
      style: {},
      dataset: {},
      ownerDocument: doc,
      parentNode: null,
      parentElement: null,
      id: String((raw.attrs && (raw.attrs.id || "")) || ""),
      className: String((raw.attrs && (raw.attrs.class || "")) || ""),
      src: String((raw.attrs && (raw.attrs.src || "")) || ""),
      href: String((raw.attrs && (raw.attrs.href || "")) || ""),
    };
    el.childNodes = el.children;
    el.classList = {
      contains: (token) => el.className.split(/\s+/).includes(String(token)),
      add: (token) => {
        state.operations.push({op: "classList.add", token: String(token || "")});
        const names = el.className.split(/\s+/).filter(Boolean);
        const value = String(token || "");
        if (value && !names.includes(value)) names.push(value);
        el.className = names.join(" ");
      },
      remove: (token) => {
        state.operations.push({op: "classList.remove", token: String(token || ""), className: el.className});
        el.className = el.className.split(/\s+/).filter((name) => name && name !== String(token)).join(" ");
      },
      toggle: (token, force) => {
        state.operations.push({op: "classList.toggle", token: String(token || "")});
        const value = String(token || "");
        const present = el.className.split(/\s+/).filter(Boolean).includes(value);
        const shouldHave = force === undefined ? !present : Boolean(force);
        if (shouldHave && !present) el.className = (el.className + " " + value).trim();
        if (!shouldHave && present) el.className = el.className.split(/\s+/).filter((name) => name && name !== value).join(" ");
        return shouldHave;
      },
      replace: (oldToken, newToken) => {
        const oldValue = String(oldToken || "");
        const newValue = String(newToken || "");
        const names = el.className.split(/\s+/).filter(Boolean);
        const index = names.indexOf(oldValue);
        if (index < 0) return false;
        names[index] = newValue;
        el.className = names.filter(Boolean).join(" ");
        return true;
      },
      contains: (token) => el.className.split(/\s+/).includes(String(token)),
    };
    Object.defineProperty(el, "textContent", {
      get() { return collectText(el); },
      set(value) {
        state.operations.push({op: "textContent.set", valueLen: String(value == null ? "" : value).length});
        el.children.length = 0;
        el.children.push({ nodeType: 3, textContent: String(value), children: [] });
      },
    });
    Object.defineProperty(el, "innerText", {
      get() { return collectText(el); },
      set(value) { el.textContent = value; },
    });
    Object.defineProperty(el, "contentWindow", {
      get() { return el.tagName === "IFRAME" ? links.childWindow : null; },
    });
    Object.defineProperty(el, "contentDocument", {
      get() { return el.tagName === "IFRAME" ? links.childDocument : null; },
    });
    el.setAttribute = function setAttribute(name, value) {
      const key = String(name).toLowerCase();
      el.attrs[key] = String(value);
      if (key === "id") el.id = String(value);
      if (key === "class") el.className = String(value);
      if (key === "src") el.src = String(value);
    };
    el.getAttribute = function getAttribute(name) {
      const key = String(name).toLowerCase();
      return Object.prototype.hasOwnProperty.call(el.attrs, key) ? el.attrs[key] : null;
    };
    el.removeAttribute = function removeAttribute(name) { delete el.attrs[String(name).toLowerCase()]; };
    el.appendChild = function appendChild(child) {
      if (child) {
        child.parentNode = el;
        child.parentElement = el;
        el.children.push(child);
      }
      return child;
    };
    el.removeChild = function removeChild(child) {
      const index = el.children.indexOf(child);
      if (index >= 0) el.children.splice(index, 1);
      return child;
    };
    el.insertBefore = function insertBefore(child) { return el.appendChild(child); };
    el.addEventListener = function addEventListener() {};
    el.removeEventListener = function removeEventListener() {};
    el.querySelector = function querySelector(selector) {
      return queryAll(el, selector)[0] || null;
    };
    el.querySelectorAll = function querySelectorAll(selector) { return queryAll(el, selector); };
    el.getElementsByTagName = function getElementsByTagName(tag) {
      const want = String(tag || "").toUpperCase();
      return queryAll(el, want.toLowerCase());
    };
    el.cloneNode = function cloneNode() { return materialize({ nodeType: 1, tagName: el.tagName, attrs: {}, children: [] }, doc); };
    for (const child of raw.children || []) {
      const live = materialize(child, doc);
      live.parentNode = el;
      live.parentElement = el;
      el.children.push(live);
    }
    return el;
  }

  function makeDocument(html, win, href) {
    const parsed = parseHtml(html);
    const doc = {
      nodeType: 9,
      nodeName: "#document",
      readyState: "complete",
      hidden: false,
      visibilityState: "visible",
      title: "",
      cookie: "",
      referrer: "",
      URL: href,
      documentURI: href,
      location: null,
      defaultView: win,
      currentScript: null,
      head: null,
      body: null,
      documentElement: null,
    };
    const htmlNode = findTag(parsed, "HTML");
    const tree = htmlNode || { nodeType: 1, tagName: "HTML", attrs: {}, children: parsed.children || [] };
    doc.documentElement = materialize(tree, doc);
    doc.head = queryAll(doc.documentElement, "head")[0] || null;
    doc.body = queryAll(doc.documentElement, "body")[0] || null;
    if (!doc.head) {
      doc.head = materialize({ nodeType: 1, tagName: "HEAD", attrs: {}, children: [] }, doc);
      doc.documentElement.appendChild(doc.head);
    }
    if (!doc.body) {
      doc.body = materialize({ nodeType: 1, tagName: "BODY", attrs: {}, children: [] }, doc);
      doc.documentElement.appendChild(doc.body);
    }
    const titleNode = queryAll(doc.documentElement, "title")[0];
    doc.title = titleNode ? collectText(titleNode) : "";
    doc.createElement = function createElement(tag) {
      return materialize({ nodeType: 1, tagName: String(tag || "DIV").toUpperCase(), attrs: {}, children: [] }, doc);
    };
    doc.createElementNS = function createElementNS(_ns, tag) { return doc.createElement(tag); };
    doc.createTextNode = function createTextNode(text) {
      return { nodeType: 3, textContent: String(text), children: [] };
    };
    doc.createDocumentFragment = function createDocumentFragment() {
      return materialize({ nodeType: 1, tagName: "#fragment", attrs: {}, children: [] }, doc);
    };
    doc.querySelector = function querySelector(selector) {
      return queryAll(doc.documentElement, selector)[0] || null;
    };
    doc.querySelectorAll = function querySelectorAll(selector) {
      return queryAll(doc.documentElement, selector);
    };
    doc.getElementById = function getElementById(id) {
      return queryAll(doc.documentElement, "#" + String(id || ""))[0] || null;
    };
    doc.getElementsByTagName = function getElementsByTagName(tag) {
      const want = String(tag || "");
      if (want.toLowerCase() === "html") return [doc.documentElement];
      return queryAll(doc.documentElement, want.toLowerCase());
    };
    doc.getElementsByClassName = function getElementsByClassName(name) {
      return queryAll(doc.documentElement, "." + String(name || ""));
    };
    doc.addEventListener = function addEventListener() {};
    doc.removeEventListener = function removeEventListener() {};
    doc.createEvent = function createEvent() { return { initEvent() {}, type: "" }; };
    doc.hasFocus = function hasFocus() { return false; };
    doc.write = function write() {};
    return doc;
  }

  function installClasses(sandbox) {
    for (const name of DOM_CLASS_NAMES) {
      if (typeof sandbox[name] !== "function") {
        sandbox[name] = function DOMConstructor() {
          recordConstructor(name, Array.prototype.slice.call(arguments));
        };
      }
    }
  }

  function installShared(sandbox, href) {
    makeTimers(sandbox);
    installClasses(sandbox);
    sandbox.console = { log() {}, warn() {}, error() {}, info() {}, debug() {}, trace() {} };
    sandbox.location = makeLocation(href);
    sandbox.history = { length: 1, state: null, replaceState() {}, pushState() {}, go() {}, back() {}, forward() {} };
    sandbox.navigator = {
      userAgent,
      language: "en-US",
      languages: ["en-US"],
      platform: "Win32",
      webdriver: false,
      hardwareConcurrency: 8,
      cookieEnabled: true,
      maxTouchPoints: 0,
      onLine: true,
      sendBeacon() { return false; },
    };
    sandbox.screen = {
      width: 1920, height: 1080, availWidth: 1920, availHeight: 1040, colorDepth: 24, pixelDepth: 24,
    };
    // ruyijs ApiMonitor 证据（2026-11-07）：挑战在 iframe 面同样读
    // getEntriesByType；mark 有状态、clearMarks 存在（与主 realm 同语义）。
    const perfMarks = [];
    sandbox.performance = {
      now: () => Date.now(),
      timeOrigin: Date.now(),
      getEntries: () => perfMarks.slice(),
      getEntriesByType: (t) => (String(t) === "mark" ? perfMarks.slice() : []),
      getEntriesByName: (n) => perfMarks.filter((e) => e.name === String(n)),
      mark(name) {
        perfMarks.push({
          name: String(name == null ? "" : name),
          entryType: "mark",
          startTime: Date.now(),
          duration: 0,
        });
      },
      clearMarks(name) {
        if (name == null) {
          perfMarks.length = 0;
          return;
        }
        const target = String(name);
        for (let i = perfMarks.length - 1; i >= 0; i--) {
          if (perfMarks[i].name === target) perfMarks.splice(i, 1);
        }
      },
      measure() {},
      clearMeasures() {},
    };
    sandbox.localStorage = makeStorage();
    sandbox.sessionStorage = makeStorage();
    sandbox.XMLHttpRequest = makeXhr();
    sandbox.Symbol = global.Symbol;
    sandbox.Set = global.Set;
    sandbox.Map = global.Map;
    sandbox.WeakMap = global.WeakMap;
    sandbox.WeakSet = global.WeakSet;
    sandbox.Proxy = global.Proxy;
    sandbox.Reflect = global.Reflect;
    sandbox.Function = global.Function;
    sandbox.Object = global.Object;
    sandbox.Array = global.Array;
    sandbox.Event = function Event() { recordConstructor("Event", Array.prototype.slice.call(arguments)); };
    sandbox.DOMException = function DOMException() { recordConstructor("DOMException", Array.prototype.slice.call(arguments)); };
    sandbox.MessageEvent = function MessageEvent() { recordConstructor("MessageEvent", Array.prototype.slice.call(arguments)); };
    sandbox.FormData = function FormData() { recordConstructor("FormData", Array.prototype.slice.call(arguments)); this.append = function append() {}; };
    sandbox.Headers = function Headers() { recordConstructor("Headers", Array.prototype.slice.call(arguments)); };
    sandbox.Request = function Request() { recordConstructor("Request", Array.prototype.slice.call(arguments)); };
    sandbox.Response = function Response() { recordConstructor("Response", Array.prototype.slice.call(arguments)); };
    sandbox.EventSource = function EventSource() { recordConstructor("EventSource", Array.prototype.slice.call(arguments)); this.close = function close() {}; this.addEventListener = function addEventListener() {}; };
    sandbox.WebSocket = function WebSocket() { recordConstructor("WebSocket", Array.prototype.slice.call(arguments)); this.close = function close() {}; this.send = function send() {}; };
    sandbox.fetch = function fetch(url) {
      recordSend("GET", url, null);
      return new Promise(() => {});
    };
    sandbox.atob = function atob(value) { return global.atob(String(value)); };
    sandbox.btoa = function btoa(value) { return global.btoa(String(value)); };
    sandbox.TextEncoder = global.TextEncoder;
    sandbox.TextDecoder = global.TextDecoder;
    sandbox.URL = global.URL;
    sandbox.URLSearchParams = global.URLSearchParams;
    sandbox.Blob = global.Blob;
    sandbox.crypto = {
      getRandomValues(view) { return nodeCrypto.webcrypto.getRandomValues(view); },
      randomUUID() { return nodeCrypto.webcrypto.randomUUID(); },
      subtle: nodeCrypto.webcrypto.subtle,
    };
    sandbox.Worker = function Worker() {
      this.postMessage = function postMessage() {};
      this.terminate = function terminate() {};
      this.addEventListener = function addEventListener() {};
      this.removeEventListener = function removeEventListener() {};
    };
    sandbox.MutationObserver = function MutationObserver() {
      this.observe = function observe() {};
      this.disconnect = function disconnect() {};
    };
    sandbox.IntersectionObserver = function IntersectionObserver() { this.observe = function observe() {}; };
    sandbox.ResizeObserver = function ResizeObserver() { this.observe = function observe() {}; };
    sandbox.matchMedia = function matchMedia() {
      return { matches: false, addListener() {}, removeListener() {}, addEventListener() {} };
    };
    sandbox.getComputedStyle = function getComputedStyle() {
      return { getPropertyValue() { return ""; } };
    };
    sandbox.requestAnimationFrame = function requestAnimationFrame() { return 0; };
    sandbox.cancelAnimationFrame = function cancelAnimationFrame() {};
    sandbox.addEventListener = function addEventListener() {};
    sandbox.removeEventListener = function removeEventListener() {};
    sandbox.dispatchEvent = function dispatchEvent() { return true; };
    sandbox.getSelection = function getSelection() { return null; };
    sandbox.scroll = function scroll() {};
    sandbox.scrollTo = function scrollTo() {};
    sandbox.focus = function focus() {};
    sandbox.blur = function blur() {};
    sandbox.close = function close() {};
    sandbox.open = function open() { return null; };
    sandbox.origin = sandbox.location.origin;
    sandbox.isSecureContext = true;
    sandbox.closed = false;
    sandbox.opener = null;
    sandbox.name = "";
    sandbox.innerWidth = 1920;
    sandbox.innerHeight = 1080;
    sandbox.devicePixelRatio = 1;
    if (typeof sandbox.HTMLScriptElement === "function") {
      sandbox.HTMLScriptElement.prototype = Object.create(null);
      sandbox.HTMLScriptElement.prototype.constructor = sandbox.HTMLScriptElement;
    }
  }

  installShared(parentSandbox, parentHref);
  installShared(childSandbox, frameHref);
  const parentDocument = makeDocument("<html><head></head><body></body></html>", parentSandbox, parentHref);
  const childDocument = makeDocument(frameHtml, childSandbox, frameHref);
  links.childDocument = childDocument;
  parentDocument.location = parentSandbox.location;
  childDocument.location = childSandbox.location;
  parentSandbox.document = parentDocument;
  childSandbox.document = childDocument;

  const parentProxy = new Proxy(parentSandbox, {
    get(target, prop, receiver) {
      if (prop === "postMessage") return recordParentPostMessage;
      return Reflect.get(target, prop, receiver);
    },
    set(target, prop, value) {
      target[prop] = value;
      return true;
    },
    has(target, prop) {
      if (prop === "postMessage") return true;
      return prop in target;
    },
  });

  parentSandbox.window = parentSandbox;
  parentSandbox.self = parentSandbox;
  parentSandbox.globalThis = parentSandbox;
  parentSandbox.top = parentSandbox;
  parentSandbox.parent = parentSandbox;
  parentSandbox.frames = parentSandbox;
  parentSandbox.postMessage = function postMessage() {};

  childSandbox.window = childSandbox;
  childSandbox.self = childSandbox;
  childSandbox.globalThis = childSandbox;
  childSandbox.parent = parentProxy;
  childSandbox.top = parentProxy;
  childSandbox.frames = childSandbox;
  childSandbox.postMessage = function postMessage() {};

  for (const key of NODE_LEAKS) {
    delete parentSandbox[key];
    delete childSandbox[key];
  }

  function leakedKeys(sandbox) {
    return NODE_LEAKS.filter((key) => key in sandbox);
  }

  function assertIsolated() {
    const leaks = leakedKeys(parentSandbox).concat(leakedKeys(childSandbox));
    if (leaks.length) {
      const err = new Error("node-leak");
      err.name = "LeakError";
      throw err;
    }
    if (childSandbox.parent === childSandbox || childSandbox.parent === global) {
      const err = new Error("parent-identity");
      err.name = "RealmError";
      throw err;
    }
    if (childSandbox.top !== childSandbox.parent) {
      const err = new Error("top-identity");
      err.name = "RealmError";
      throw err;
    }
    const frame = parentDocument.createElement("iframe");
    if (frame.contentWindow !== childSandbox || frame.contentDocument !== childDocument) {
      const err = new Error("contentWindow-identity");
      err.name = "RealmError";
      throw err;
    }
    if (frame.contentDocument === parentDocument) {
      const err = new Error("contentDocument-parent");
      err.name = "RealmError";
      throw err;
    }
    const identityOk = vm.runInContext(
      "window===globalThis&&self===window&&parent!==window&&top===parent&&typeof parent.postMessage==='function'",
      childSandbox
    );
    if (identityOk !== true) {
      const err = new Error("child-identity");
      err.name = "RealmError";
      throw err;
    }
  }

  function runFrameScript(code, filename) {
    state.operations.push({op: "frame.start", sourceBytes: String(code || "").length});
    assertIsolated();
    const scriptEl = childDocument.createElement("script");
    scriptEl.src = frameHref;
    childDocument.currentScript = scriptEl;
    try {
      vm.runInContext(String(code || ""), childSandbox, {
        filename: filename || "turnstile-iframe.js",
        timeout: timeoutMs,
      });
      state.frameEval = "ok";
    } catch (err) {
      state.frameEval = "error";
      noteThrow(err);
    } finally {
      childDocument.currentScript = null;
    }
  }

  function ownCount(value) {
    if (!value || typeof value !== "object") return null;
    return Object.keys(value).length;
  }

  function observe() {
    const opt = childSandbox._cf_chl_opt;
    return {
      realmId: "turnstile-frame",
      frameEval: state.frameEval,
      chlOptKeys: ownCount(opt),
      framePqType: typeof childSandbox.PQak3,
      framePqOwn: Object.prototype.hasOwnProperty.call(childSandbox, "PQak3"),
      parentPqOwn: Object.prototype.hasOwnProperty.call(parentSandbox, "PQak3"),
      throwName: state.thrown ? (state.thrown.name || "Error") : null,
      throwMessage: state.thrown ? sanitizeMessage(state.thrown.message) : "",
      sendCount: state.sends.length,
      sends: state.sends.map((row) => ({ method: row.method, pathClass: row.pathClass })),
      parentPostMessageCount: state.parentPostMessageCount,
      parentPostMessageSamples: state.parentPostMessageSamples.slice(),
      constructorCalls: state.constructorCalls.slice(),
      operations: state.operations.slice(-32),
    };
  }

  function dispose() {
    for (const id of state.timerIds) {
      global.clearTimeout(id);
      global.clearInterval(id);
    }
    state.timerIds.clear();
  }

  return {
    runFrameScript,
    observe,
    dispose,
    noteThrow,
    leakedKeys: () => leakedKeys(parentSandbox).concat(leakedKeys(childSandbox)),
  };
}

module.exports = { createRealms, pathClass, sanitizeMessage };
