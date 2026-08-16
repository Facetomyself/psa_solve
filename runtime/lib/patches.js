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

function install(g) {
  // ---- P1: UpvLO0 = XOR 流解密器 ----
  if (typeof g.UpvLO0 !== "function") {
    g.UpvLO0 = function (p) {
      const parts = String(p).split("$");
      const k = Buffer.from(parts[0], "base64");
      const d = Buffer.from(parts[1], "base64");
      const out = new Uint8Array(d.length);
      for (let i = 0; i < d.length; i++) {
        out[i] = d[i] ^ k[i % k.length];
      }
      return out;
    };
  }

  // ---- P2: ZHfDS6 = 原生 eval 别名 ----
  if (typeof g.ZHfDS6 !== "function") {
    g.ZHfDS6 = eval;
  }
}

module.exports = { install };
