/*
 * lib/config.js — 运行参数与目标 URL 派生
 *
 * 环境变量（demo/上层注入，复用其他目标时覆盖）：
 *   CF_TARGET_URL  页面 URL（默认 PSA case）
 *   CF_USER_AGENT  UA（默认 Firefox 155）
 *   CF_REFERER     Referer（默认等于页面 URL）
 */
"use strict";

const CF_TARGET_URL = process.env.CF_TARGET_URL || "https://www.psacard.com/cert/143963534/psa";
const CF_USER_AGENT = process.env.CF_USER_AGENT ||
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:155.0) Gecko/20100101 Firefox/155.0";
const CF_REFERER = process.env.CF_REFERER || CF_TARGET_URL;

// 诊断开关：缺失面记录（生产关闭）
const CF_DIAGNOSTICS = process.env.CF_DIAGNOSTICS === "1";

let __targetParsed = null;
try { __targetParsed = new URL(CF_TARGET_URL); } catch (e) { __targetParsed = null; }
const TARGET = __targetParsed || {
  origin: "https://www.psacard.com",
  protocol: "https:",
  host: "www.psacard.com",
  hostname: "www.psacard.com",
  port: "",
  pathname: "/cert/143963534/psa",
  search: "",
  hash: "",
  href: CF_TARGET_URL,
};

module.exports = { CF_TARGET_URL, CF_USER_AGENT, CF_REFERER, CF_DIAGNOSTICS, TARGET };
