/*
 * code.js — PSA CF 5s 盾 vanilla Node 补环境主入口
 *
 * Case: psa-cf-5s-shield-20260815
 * 定位：RuyiDOM（真实 Gecko）是诊断执行层；本文件是最终运行时形态——
 * vanilla Node 补环境，产出提交 URL + 载荷，由上层 client 发送验收。
 *
 * 模块（runtime/lib/，按宿主面拆分）：
 *   config.js        运行参数与目标 URL 派生（CF_TARGET_URL/CF_USER_AGENT/CF_REFERER）
 *   host-globals.js  window 别名 / 屏幕 / navigator / performance / DOM 类
 *   host-dom.js      元素 stub / document / cookie jar / storage
 *   host-async.js    Worker / 观察者 / 定时器 / Blob / URL
 *   patches.js       缺口补丁 P1-P2（UpvLO0/ZHfDS6，逐条证据注释）
 *   transport.js     XHR shim（真实网络 + cookie/响应头浏览器语义 + 观测）
 *
 * 本入口负责：
 *   - 按序安装各模块（config → globals → dom → async → patches → transport）
 *   - VM Proxy 垫底（orchestrate 的 Proxy 探测 null target——外部宿主面补丁）
 *   - 可选诊断（CF_DIAGNOSTICS=1 时记录缺失面）
 */
"use strict";

const cfg = require("./lib/config.js");
const hostGlobals = require("./lib/host-globals.js");
const hostDom = require("./lib/host-dom.js");
const hostAsync = require("./lib/host-async.js");
const patches = require("./lib/patches.js");
const transport = require("./lib/transport.js");

const g = globalThis;

// 1. 全局面（含 DOM 类构造函数）
hostGlobals.install(g, cfg);

// 2. DOM / storage / cookie jar
hostDom.install(g, cfg);

// 3. 异步宿主面
hostAsync.install(g);

// 4. 缺口补丁（P1/P2）
patches.install(g);

// 5. XHR transport（观测 + 提交）
transport.install(g, cfg);

// 5.5 atob I/O 记录器（CF_ATOB_TRACE=1，对拍 driver 用——见 lib/atob-trace.js）
require("./lib/atob-trace.js").install(g);

// 6. VM Proxy 垫底：orchestrate 的 Proxy 探测可能以 null/undefined 为 target
//    （外部宿主面补丁——探测行为在 Node 环境无可观察对象）
(function () {
  const __origProxy = Proxy;
  g.__proxyNullTargets = [];
  g.Proxy = function (t, h) {
    if (t === undefined || t === null) {
      if (g.__proxyNullTargets.length < 10) {
        g.__proxyNullTargets.push(
          String(new Error().stack || "").split("\n").slice(1, 4).join(" | ").slice(0, 300));
      }
      t = {};
    }
    return new __origProxy(t, h);
  };
  g.Proxy.revocable = __origProxy.revocable;
})();

// 7. 可选诊断（CF_DIAGNOSTICS=1）：记录缺失的全局/宿主属性
if (cfg.CF_DIAGNOSTICS) {
  g.__missingGlobals = new Set();
  g.__missingHostProps = new Set();
  function traceMissing(obj, name) {
    return new Proxy(obj, {
      get(t, k) {
        if (typeof k === "string" && k !== "then" && !k.startsWith("__") &&
            !(k in t) && typeof t[k] === "undefined") {
          g.__missingHostProps.add(name + "." + k);
        }
        return t[k];
      },
    });
  }
  g.window = new Proxy(g, {
    get(t, k) {
      if (typeof k === "string" && k !== "then" && !(k in t) && !k.startsWith("__")) {
        t.__missingGlobals.add(String(k));
      }
      return t[k];
    },
  });
}

module.exports = { booted: true, config: cfg, document: g.document };
