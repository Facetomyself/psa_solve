/*
 * lib/host-dom.js — 元素 stub / document / cookie jar / storage
 *
 * 职责：DOM 面（元素操作 no-op 但结构健全）+ cookie jar 浏览器语义
 * （document.cookie 赋值是增量合并，Set-Cookie 应用不得覆盖已存在条目）。
 */
"use strict";

function install(g, cfg) {
  let headEl = null;
  let bodyEl = null;

  const elementConstructors = {
    html: "HTMLHtmlElement",
    head: "HTMLHeadElement",
    body: "HTMLBodyElement",
    div: "HTMLDivElement",
    a: "HTMLAnchorElement",
    span: "HTMLSpanElement",
    script: "HTMLScriptElement",
    style: "HTMLStyleElement",
    link: "HTMLLinkElement",
    input: "HTMLInputElement",
    form: "HTMLFormElement",
    canvas: "HTMLCanvasElement",
    iframe: "HTMLIFrameElement",
    img: "HTMLImageElement",
  };

  function elementConstructor(tag) {
    const name = elementConstructors[String(tag || "").toLowerCase()] || "HTMLElement";
    const Ctor = g[name];
    if (typeof Ctor !== "function") return null;
    if (Ctor.name !== name) Object.defineProperty(Ctor, "name", { value: name });
    return Ctor;
  }

  function makeElement(tag) {
    const cls = new Set();
    const Ctor = elementConstructor(tag);
    const el = Ctor ? Object.create(Ctor.prototype) : {};
    Object.assign(el, {
      tagName: String(tag).toUpperCase(),
      nodeType: 1,
      children: [],
      style: {},
      attrs: {},
      dataset: {},
      innerHTML: "",
      textContent: "",
      className: "",
      classList: {
        add: (...names) => names.forEach((n) => cls.add(n)),
        remove: (...names) => names.forEach((n) => cls.delete(n)),
        contains: (n) => cls.has(n),
        toggle: (n) => { cls.has(n) ? cls.delete(n) : cls.add(n); return cls.has(n); },
      },
      setAttribute(k, v) {
        this.attrs[k] = String(v);
        if (k === "class") { String(v).split(/\s+/).forEach((n) => n && cls.add(n)); }
        if (k === "id") this.id = String(v);
        if (k === "name" || k === "value" || k === "type" || k === "action" || k === "method") {
          this[k] = String(v);
        }
        if (String(this.tagName).toLowerCase() === "script" && String(k).toLowerCase() === "src") {
          this.src = String(v);
        }
      },
      getAttribute(k) { return this.attrs[k]; },
      removeAttribute(k) { delete this.attrs[k]; },
      appendChild(c) {
        const note = g[Symbol.for("psa.noteNodeAppend")];
        if (typeof note === "function" && c && typeof c === "object") note(this, c);
        this.children.push(c);
        // 动态内联脚本：真 DOM 在插入时同步执行（HTML5 script insertion 算法）。
        // ruyijs 参考链证据：FO r1 响应后挑战 JS 注入内联/外链脚本驱动下一阶段；
        // 本 stub 此前只处理 src 外链（scheduleScript），内联脚本静默丢弃 → 链断。
        if (c && typeof c === "object" &&
            String(c.tagName || "").toUpperCase() === "SCRIPT" &&
            !c.src && typeof c.__inlineCode === "string" && c.__inlineCode &&
            !c.__inlineRan) {
          c.__inlineRan = true;
          const previous = g.document && g.document.currentScript;
          if (g.document) g.document.currentScript = c;
          try { runPageScript(c.__inlineCode); }
          catch (e) {}
          finally { if (g.document) g.document.currentScript = previous; }
        }
        return c;
      },
      removeChild(c) {
        const i = this.children.indexOf(c);
        if (i >= 0) this.children.splice(i, 1);
        return c;
      },
      insertBefore(c) { this.children.unshift(c); return c; },
      addEventListener() {},
      removeEventListener() {},
      getBoundingClientRect() {
        return { top: 0, left: 0, width: 0, height: 0, right: 0, bottom: 0 };
      },
      cloneNode() { return makeElement(this.tagName); },
      focus() {},
      click() {},
      parentElement: bodyEl,
      parentNode: bodyEl,
      nextSibling: null,
      previousSibling: null,
      firstChild: null,
      lastChild: null,
      childNodes: [],
      ownerDocument: null,
      offsetWidth: 0,
      offsetHeight: 0,
      clientWidth: 0,
      clientHeight: 0,
      src: "",
    });
    if (String(tag).toLowerCase() === "script") {
      let src = "";
      Object.defineProperty(el, "src", {
        configurable: true,
        enumerable: true,
        get() { return src; },
        set(value) {
          src = String(value == null ? "" : value);
          scheduleScript(el);
        },
      });
      // 内联脚本内容面：text / textContent 赋值只暂存；真 DOM 语义是插入时执行
      // （appendChild 路径负责同步执行一次，见上）。
      const scriptEl = el;
      const setInline = (value) => {
        scriptEl.__inlineCode = String(value == null ? "" : value);
      };
      Object.defineProperty(el, "text", {
        configurable: true, enumerable: true,
        get() { return el.__inlineCode || ""; },
        set: setInline,
      });
      const prevTextContent = el.textContent;
      Object.defineProperty(el, "textContent", {
        configurable: true, enumerable: true,
        get() { return prevTextContent; },
        set: setInline,
      });
    }
    el.querySelector = () => makeElement("div");
    el.querySelectorAll = () => [makeElement("div")];
    el.getElementsByTagName = (t) => [makeElement(t)];
    el.remove = () => {};
    el.replaceChildren = () => {};
    let markup = "";
    Object.defineProperty(el, "innerHTML", {
      configurable: true,
      enumerable: true,
      get() { return markup; },
      set(value) {
        markup = String(value == null ? "" : value);
        if (!/<form\b|<input\b/i.test(markup)) return;
        el.children.length = 0;
        appendFormMarkup(el, markup);
      },
    });
    return el;
  }

  function runPageScript(code) {
    const vm = require("vm");
    // 609KB FO 下一阶段 JS 编译+首轮执行超 10s（证据：runPageScript 抛
    // SyntaxError 形态的中断 = vm timeout 击杀）。capture 求解 110s 窗口，
    // 单脚本同步段放宽到 60s。
    const options = { filename: "script-src.js", timeout: 60000 };
    if (cfg.CF_DIAGNOSTICS) {
      try {
        runPageScript.__n = (runPageScript.__n || 0) + 1;
        require("fs").writeFileSync(
          "diag-script-" + runPageScript.__n + ".js", String(code));
      } catch (e) {}
    }
    // 动态脚本 opcode 诊断：switch 变量名因函数而异（km / nv / nv[0]…），
    // 对每个 default:throw Error() 就近回溯所属 switch(VAR) 并带值抛出。
    let codeToRun = code;
    if (cfg.CF_DIAGNOSTICS && typeof code === "string") {
      // Jm 调度器指令流记录：switch(nv){ 入口 push nv，供 206 未命中前的序列回溯
      codeToRun = code.replace(/switch\(nv\)\{/g,
        "switch(nv){(global.__vmSeq=global.__vmSeq||[]).push(nv);");
      codeToRun = code.replace(/default:throw Error\(\)\}/g, (match, offset) => {
        const sw = codeToRun.lastIndexOf("switch(", offset);
        const varExpr = sw >= 0 ? codeToRun.slice(sw + 7, codeToRun.indexOf(")", sw)) : "?";
        const safeVar = /^[A-Za-z_$][\w$]*(\[\d\])?$/.test(varExpr) ? varExpr : "?";
        return "default:throw new Error('vm-default " + safeVar +
            "='+(typeof " + safeVar + "!=='undefined'?" + safeVar + ":'?')+' seqTail='+String(global.__vmSeq?global.__vmSeq.slice(-12):[]))}";
      });
      codeToRun = codeToRun.replace(/default:throw (\w+)\((\d+),Error\)/g,
        "default:throw new Error('vm-default2 seed=$2 op=Err fn=$1 ctx='+(typeof km!=='undefined'?km:(typeof TH!=='undefined'?TH:'?')))");
    }
    try {
      if (vm.isContext(g)) vm.runInContext(codeToRun, g, options);
      else vm.runInThisContext(codeToRun, options);
    } catch (e) {
      if (cfg.CF_DIAGNOSTICS) process.stderr.write(
        "[diag] runPageScript threw: " + String(e && e.name || "?") + ": " +
        String(e && e.message || e).slice(0, 400) + "\n");
      throw e;
    }
  }

  function absoluteScriptUrl(src) {
    try {
      const base = (g.location && g.location.href) || cfg.CF_TARGET_URL;
      const parsed = new URL(String(src || ""), base);
      if (parsed.protocol !== "https:" && parsed.protocol !== "http:") return "";
      return parsed.href;
    } catch (e) {
      return "";
    }
  }

  function scheduleScript(el) {
    if (!el || el.__scriptStarted) return;
    const src = absoluteScriptUrl(el.src);
    if (!src) return;
    const XHR = g.XMLHttpRequest;
    if (typeof XHR !== "function") return;
    el.__scriptStarted = true;
    const xhr = new XHR();
    xhr.open("GET", src);
    xhr.setRequestHeader("Sec-Fetch-Dest", "script");
    xhr.setRequestHeader("Sec-Fetch-Mode", "no-cors");
    xhr.onload = function () {
      if (xhr.status !== 200) return;
      const code = String(xhr.responseText || "");
      if (!code) return;
      const previous = g.document.currentScript;
      g.document.currentScript = el;
      try { runPageScript(code); }
      catch (e) {}
      finally { g.document.currentScript = previous; }
    };
    xhr.send(null);
  }

  function markupAttrs(source) {
    const attrs = {};
    const re = /([A-Za-z_:][-A-Za-z0-9_:.]*)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+))/g;
    let match;
    while ((match = re.exec(String(source || "")))) {
      attrs[match[1].toLowerCase()] = match[2] ?? match[3] ?? match[4] ?? "";
    }
    return attrs;
  }

  function applyMarkupAttrs(node, attrs) {
    for (const key of ["id", "name", "value", "type", "action", "method"]) {
      if (Object.prototype.hasOwnProperty.call(attrs, key)) node.setAttribute(key, attrs[key]);
    }
  }

  function appendInputs(parent, source) {
    const re = /<input\b([^>]*)\/?>/gi;
    let match;
    while ((match = re.exec(String(source || "")))) {
      const input = makeElement("input");
      applyMarkupAttrs(input, markupAttrs(match[1]));
      parent.appendChild(input);
    }
  }

  function appendFormMarkup(parent, source) {
    const html = String(source || "");
    const formRe = /<form\b([^>]*)>([\s\S]*?)<\/form>/gi;
    let formMatch;
    let sawForm = false;
    while ((formMatch = formRe.exec(html))) {
      sawForm = true;
      const form = makeElement("form");
      applyMarkupAttrs(form, markupAttrs(formMatch[1]));
      appendInputs(form, formMatch[2]);
      parent.appendChild(form);
    }
    if (!sawForm && String(parent.tagName || "").toLowerCase() === "form") appendInputs(parent, html);
  }

  headEl = makeElement("head");
  bodyEl = makeElement("body");

  const documentStub = {
    nodeType: 9,
    head: headEl,
    body: bodyEl,
    documentElement: makeElement("html"),
    title: "Just a moment...",
    readyState: "complete",
    location: g.location,
    defaultView: g,
    documentURI: cfg.CF_TARGET_URL,
    URL: cfg.CF_TARGET_URL,
    hidden: false,
    visibilityState: "visible",
    referrer: cfg.CF_REFERER,
    currentScript: null,
    createElement: (tag) => makeElement(tag),
    createElementNS: (ns, tag) => makeElement(tag),
    createTextNode: (t) => ({ nodeType: 3, textContent: String(t) }),
    createDocumentFragment: () => makeElement("#fragment"),
    getElementById: () => makeElement("div"),
    getElementsByTagName: (tag) =>
      tag === "head" ? [headEl] : tag === "body" ? [bodyEl] : [makeElement(tag)],
    getElementsByClassName: () => [makeElement("div")],
    querySelector: () => makeElement("div"),
    querySelectorAll: () => [makeElement("div")],
    addEventListener: g.addEventListener,
    removeEventListener: g.removeEventListener,
    dispatchEvent: g.dispatchEvent,
    write(markup) {
      // 真语义：向文档流写入并解析执行。<script src> 走 scheduleScript（XHR+runPageScript），
      // 内联 <script>body</script> 直接 runPageScript。ruyijs 参考链：下一阶段脚本经
      // document 写入后立即执行；此前 no-op 会静默断链。
      const source = String(markup == null ? "" : markup);
      if (!source) return;
      const re = /<script\b([^>]*)>([\s\S]*?)<\/script>/gi;
      let match;
      while ((match = re.exec(source))) {
        const attrsRaw = match[1] || "";
        const body = match[2] || "";
        const srcMatch = /\ssrc\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/i.exec(attrsRaw);
        if (srcMatch) {
          const url = srcMatch[1] || srcMatch[2] || srcMatch[3] || "";
          const el = makeElement("script");
          el.setAttribute("src", url); // 触发 scheduleScript
          if (documentStub.head && typeof documentStub.head.appendChild === "function") {
            documentStub.head.appendChild(el);
          }
        } else if (body.trim()) {
          const previous = g.document && g.document.currentScript;
          if (g.document) g.document.currentScript = null;
          try { runPageScript(body); }
          catch (e) {}
          finally { if (g.document) g.document.currentScript = previous; }
        }
      }
    },
    hasFocus: () => false,
  };
  documentStub.fonts = {
    status: "loaded",
    size: 0,
    check(font) {
      const text = String(font || "").toLowerCase();
      return /\b(serif|sans-serif|monospace|cursive|fantasy|system-ui|emoji|math|fangsong|arial|calibri|cambria|candara|consolas|constantia|corbel|courier new|georgia|impact|segoe ui|tahoma|times new roman|trebuchet ms|verdana|comic sans ms|lucida console|microsoft sans serif)\b/.test(text);
    },
    load() { return Promise.resolve([]); },
    forEach() {},
    add() {},
    delete() { return false; },
    has() { return false; },
  };
  documentStub.fonts.ready = Promise.resolve(documentStub.fonts);
  documentStub.elementFromPoint = function (x, y) {
    const nx = Number(x);
    const ny = Number(y);
    if (!Number.isFinite(nx) || !Number.isFinite(ny) || nx < 0 || ny < 0) return null;
    const view = this.defaultView;
    const width = view ? Number(view.innerWidth) : NaN;
    const height = view ? Number(view.innerHeight) : NaN;
    if (Number.isFinite(width) && Number.isFinite(height) && width > 0 && height > 0) {
      if (nx >= width || ny >= height) return null;
    }
    return this.body || this.documentElement || null;
  };

  // ---- cookie jar（浏览器语义：增量合并，属性段过滤） ----
  const __cookieJar = new Map();
  const __COOKIE_ATTRS = new Set(["expires", "max-age", "path", "domain", "secure",
    "httponly", "samesite", "partitioned", "priority"]);
  function cookieSet(raw) {
    String(raw).split(";").forEach((part) => {
      const kv = part.trim();
      const eq = kv.indexOf("=");
      if (eq <= 0) return;
      const name = kv.slice(0, eq).trim();
      const value = kv.slice(eq + 1).trim();
      if (__COOKIE_ATTRS.has(name.toLowerCase())) return;
      if (value === "") { __cookieJar.delete(name); } else { __cookieJar.set(name, value); }
    });
  }
  Object.defineProperty(documentStub, "cookie", {
    get: () => Array.from(__cookieJar.entries()).map(([k, v]) => `${k}=${v}`).join("; "),
    set: (v) => { cookieSet(v); },
    configurable: true,
  });
  documentStub.__cookieSet = cookieSet;  // transport.js 复用（Set-Cookie 应用）

  g.document = documentStub;

  installFrameAccessors(g);

  // ---- storage ----
  function makeStorage() {
    const m = new Map();
    return {
      getItem: (k) => (m.has(k) ? m.get(k) : null),
      setItem: (k, v) => { m.set(k, String(v)); },
      removeItem: (k) => { m.delete(k); },
      clear: () => { m.clear(); },
      key: (i) => Array.from(m.keys())[i] ?? null,
      get length() { return m.size; },
    };
  }
  g.localStorage = makeStorage();
  g.sessionStorage = makeStorage();
  installFormSubmit(g, cfg);

  // ---- 顶层 window 的 frameElement ----
  // 证据（2026-11-06 bridge diag missingGlobals）：FO r1 后挑战代码探测
  // window.frameElement。真实浏览器顶层 frameElement=null。
  // 注意：window.turnstile 不 stub——turnstile api.js（fo-2）自装 window.turnstile，
  // 预置 stub 会让它报 "Turnstile already has been loaded" 走错分支。
  if (!Object.prototype.hasOwnProperty.call(g, "frameElement")) {
    Object.defineProperty(g, "frameElement", {
      configurable: true, enumerable: true, get() { return null; },
    });
  }
}

function formControls(node, out) {
  const children = node && node.children;
  if (!Array.isArray(children)) return out;
  for (const child of children) {
    if (!child || child.nodeType !== 1) continue;
    const tag = String(child.tagName || "").toLowerCase();
    if (tag === "input" || tag === "select" || tag === "textarea") out.push(child);
    else if (tag !== "form") formControls(child, out);
  }
  return out;
}

function controlPair(node) {
  if (node.disabled) return null;
  const tag = String(node.tagName || "").toLowerCase();
  const type = String(node.type || (node.attrs && node.attrs.type) || "").toLowerCase();
  if (tag === "input" && (type === "submit" || type === "button" || type === "reset" || type === "image" || type === "file")) {
    return null;
  }
  const name = node.name != null && node.name !== "" ? node.name : (node.attrs && node.attrs.name);
  if (!name) return null;
  const value = node.value != null ? node.value : ((node.attrs && node.attrs.value) || "");
  return encodeURIComponent(String(name)) + "=" + encodeURIComponent(String(value));
}

const framePairs = new WeakMap();
const REALM_NAMES = [
  "Function", "Array", "Object", "Number", "String", "Boolean", "Symbol", "BigInt",
  "Date", "RegExp", "Promise", "Map", "Set", "WeakMap", "WeakSet", "Error", "TypeError",
  "RangeError", "SyntaxError", "ReferenceError", "EvalError", "URIError", "ArrayBuffer",
  "Uint8Array", "Uint16Array", "Uint32Array", "Int8Array", "Int16Array", "Int32Array",
  "Float32Array", "Float64Array", "Uint8ClampedArray", "DataView", "TextEncoder",
  "TextDecoder", "URL", "URLSearchParams", "Intl", "Reflect", "Proxy", "JSON", "Math",
  "parseInt", "parseFloat", "isNaN", "isFinite", "decodeURI", "decodeURIComponent",
  "encodeURI", "encodeURIComponent", "escape", "unescape", "Infinity", "NaN",
  "queueMicrotask", "structuredClone", "atob", "btoa", "setTimeout", "clearTimeout",
  "setInterval", "clearInterval", "requestAnimationFrame", "cancelAnimationFrame",
  "Blob", "File", "FormData", "Headers", "Request", "Response", "AbortController",
  "Text", "Comment", "Node", "Element", "Document", "DOMParser", "XMLHttpRequest",
  "MutationObserver", "ResizeObserver", "MessageChannel", "console", "performance",
  "crypto", "navigator", "screen", "history", "localStorage", "sessionStorage",
];

function framePair(g, iframe) {
  const existing = framePairs.get(iframe);
  if (existing) return existing;
  const realm = Object.create(Object.prototype);
  for (const name of REALM_NAMES) {
    if (typeof g[name] !== "undefined") realm[name] = g[name];
  }
  realm.eval = eval;
  const win = Object.create(realm);
  const doc = Object.create(g.document);
  Object.defineProperty(doc, "defaultView", {
    configurable: true,
    enumerable: true,
    get() { return win; },
  });
  bindIframeDocumentTree(doc, g.document);
  win.document = doc;
  win.frameElement = iframe;
  win.location = g.location;
  win.parent = g;
  win.top = g;
  win.self = win;
  win.window = win;
  win.length = 0;
  win.closed = false;
  win.opener = null;
  win.frames = win;
  win.postMessage = function () {};
  win.addEventListener = function () {};
  win.removeEventListener = function () {};
  bindIframeFunction(win, doc);
  const pair = { win, doc };
  framePairs.set(iframe, pair);
  return pair;
}

function bindIframeDocumentTree(doc, parentDocument) {
  const create = parentDocument && parentDocument.createElement;
  if (typeof create !== "function") return;
  const html = create.call(parentDocument, "html");
  const head = create.call(parentDocument, "head");
  const body = create.call(parentDocument, "body");
  if (html && typeof html.appendChild === "function") {
    html.appendChild(head);
    html.appendChild(body);
  }
  if (html) {
    html.parentNode = null;
    html.parentElement = null;
  }
  if (head) {
    head.parentNode = html;
    head.parentElement = html;
  }
  if (body) {
    body.parentNode = html;
    body.parentElement = html;
  }
  for (const [key, value] of [["documentElement", html], ["head", head], ["body", body]]) {
    Object.defineProperty(doc, key, {
      configurable: true,
      enumerable: true,
      writable: true,
      value,
    });
  }
}

function bindIframeFunction(win, doc) {
  const vm = require("vm");
  const box = {
    document: doc,
    window: win,
    parent: win.parent,
    top: win.top,
    self: win,
    location: win.location,
  };
  vm.createContext(box);
  Object.defineProperty(win, "Function", {
    configurable: true,
    writable: true,
    enumerable: false,
    value: vm.runInContext("Function", box),
  });
}

function installFrameAccessors(g) {
  const Ctor = g.HTMLIFrameElement;
  if (typeof Ctor !== "function") return;
  const proto = Ctor.prototype;
  if (!Object.prototype.hasOwnProperty.call(proto, "contentWindow")) {
    Object.defineProperty(proto, "contentWindow", {
      configurable: true,
      enumerable: true,
      get() { return framePair(g, this).win; },
    });
  }
  if (!Object.prototype.hasOwnProperty.call(proto, "contentDocument")) {
    Object.defineProperty(proto, "contentDocument", {
      configurable: true,
      enumerable: true,
      get() { return framePair(g, this).doc; },
    });
  }
}

function installFormSubmit(g, cfg) {
  const Ctor = g.HTMLFormElement;
  if (typeof Ctor !== "function" || typeof Ctor.prototype.submit === "function") return;
  Object.defineProperty(Ctor.prototype, "elements", {
    configurable: true,
    get() { return formControls(this, []); },
  });
  Ctor.prototype.submit = function submit() {
    const method = String(this.method || (this.attrs && this.attrs.method) || "get").toUpperCase() === "POST" ? "POST" : "GET";
    const action = String(this.action || (this.attrs && this.attrs.action) || (g.location && g.location.href) || cfg.CF_TARGET_URL);
    const body = formControls(this, []).map(controlPair).filter(Boolean).join("&");
    let url = action;
    if (method === "GET" && body) url += (url.includes("?") ? "&" : "?") + body;
    const XHR = g.XMLHttpRequest;
    if (typeof XHR !== "function") return;
    const xhr = new XHR();
    xhr.open(method, url);
    if (method === "POST") {
      xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
      xhr.send(body);
    } else {
      xhr.send(null);
    }
  };
}

module.exports = { install };
