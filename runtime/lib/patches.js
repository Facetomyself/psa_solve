/*
 * lib/patches.js — 缺口补丁（外部宿主面，逐条证据）
 *
 * P1 window.UpvLO0 缺失 → XOR 流解密器
 *    证据：VM 程序 window["UpvLO0"].call(window, "base64$base64")；
 *    jcLw7 同构（字节码重建）：o[i] = k[i] ^ s.charCodeAt(i % s.length)
 *
 * P2 window.ZHfDS6 缺失 → 原生 eval 别名
 *    证据：程序检查 ZHfDS6.toString()===eval.toString()；传入重建函数
 *    源码（eval 注册）与 1.3MB 空白字符串（性能指纹基准）
 *
 * P3 setTimeout/setInterval 变长参数透传 → 见 host-async.js（此处不再重复）
 *
 * 禁止：VM/opcode/bytecode/WASM 内部 patch。
 */
"use strict";

const { createSurface } = require("../../diagnostics/shadowroot-repair-20261020/body-shadow-surface.cjs");

function install(g) {
  // ---- P1: UpvLO0 = XOR 流解密器 ----
  if (typeof g.UpvLO0 !== "function") {
    // 2026-11-07 域修正：返回 latin1 字符串而非 Uint8Array。
    // 字节码重建语义 o[i]=k[i]^s.charCodeAt(i%s.length) 是 charCode 算术 →
    // JS 字符串拼接（ruyijs 参考链）。对拍证据：第二层解码输入 ruyijs=规范
    // base64 文本（charCode<128），Node=二进制——同一程序变量的域分歧。
    // Uint8Array 走下游 atob 时成二进制域（99.6% 域外字节），字符串则保持
    // 编码域。XOR 产物 charCode 全 <256，latin1 字符串无损承载。
    g.UpvLO0 = function (p) {
      const parts = String(p).split("$");
      const k = Buffer.from(parts[0], "base64");
      const d = Buffer.from(parts[1], "base64");
      let out = "";
      for (let i = 0; i < d.length; i++) {
        out += String.fromCharCode(d[i] ^ k[i % k.length]);
      }
      return out;
    };
  }

  // ---- P2: ZHfDS6 = 原生 eval 别名 ----
  if (typeof g.ZHfDS6 !== "function") {
    g.ZHfDS6 = eval;
  }

  // Same property already proven: the shadow root returned for this body keeps
  // the caller-supplied child. createElement's HTMLStyleElement return is unchanged.
  const body = g.document && g.document.body;
  if (body && typeof g.HTMLBodyElement === "function" && typeof body.attachShadow !== "function") {
    const surface = createSurface();
    surface.install(g.HTMLBodyElement, g.document, body);
    Object.defineProperty(g, Symbol.for("psa.noteNodeAppend"), {
      value: surface.noteAppend,
      configurable: true,
      enumerable: false,
      writable: true,
    });
  }
}

module.exports = { install };
