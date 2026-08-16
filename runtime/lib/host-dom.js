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

  function makeElement(tag) {
    const cls = new Set();
    const el = {
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
      },
      getAttribute(k) { return this.attrs[k]; },
      removeAttribute(k) { delete this.attrs[k]; },
      appendChild(c) { this.children.push(c); return c; },
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
    };
    el.querySelector = () => makeElement("div");
    el.querySelectorAll = () => [makeElement("div")];
    el.getElementsByTagName = (t) => [makeElement(t)];
    el.remove = () => {};
    el.replaceChildren = () => {};
    Object.defineProperty(el, "contentWindow", {
      get: () => ({
        location: g.location,
        document: g.document,
        postMessage() {},
        addEventListener() {},
        eval,
      }),
    });
    Object.defineProperty(el, "contentDocument", {
      get: () => g.document,
    });
    return el;
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
    addEventListener() {},
    removeEventListener() {},
    write() {},
    hasFocus: () => false,
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
}

module.exports = { install };
