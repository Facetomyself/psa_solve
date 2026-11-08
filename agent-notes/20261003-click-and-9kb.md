# Click install and the 9KB gap — 2026-10-03

Live runner: `diagnostics/causal-observer-transport-fixed/ruyidom_bridge.causal-observer.transport-fixed.js`
Receipt: `evidence/web/diagnostic-causal-observer/restricted/a7e045b6cf194921bb229b6741e59b8b`
Headed posts: `evidence/web/v8trace-chromium/headed-20261003`

## Why `__clickTs` was absent

`clickErr` is the string `missing`. That string is set only by the page listener when `window.__clickTs` is falsy. It is not an exception name.

`armClick` is the only function that logs `click:arm`. The live `lookupRing` has `click:f0`, `ptr:8`, `click:f1:c1`, and no `click:arm`. So `armClick` never ran, and the chrome `message` listener registered immediately after the `__clickTs` assignment never ran.

That assignment and that listener sit in one `try` with an empty `catch`. `Cu` is not imported in this file. The assignment threw, the catch dropped the error, and the page compartment kept an empty `__clickTs`.

The clicks in the log come from a different timer. Every 400ms it calls `tryClickWidget` directly. The first pass found no iframe (`click:f0`). A later pass found one iframe and synthesized one click (`click:f1:c1`). Eight outer-window `mousemove` events are a third timer (`ptr:8`). None of these three paths installs or calls `__clickTs`.

## The 9KB is not a click trajectory

The shortfall is the two challenge-host posts: 83372 vs 92460, and 86530 vs 95735. The page-host posts are 2252 vs 2380 and 8695 vs 9132. Local `postShape` only kept those two page-host bodies: both start at char code 97 and are base64-like. Headed page-host bodies start with `t`. Those are not the 9KB gap.

The two large headed bodies contain no `mouse`, `click`, `pointer`, `clientX`, comma, or brace. They share a 171-byte prefix and then diverge. Their own length difference is 3275, not a trailing 9KB segment. The local copies of those two bodies were not stored, so the missing bytes cannot be lined up field by field.

A synthesized single click plus eight outer moves is a few events. It does not account for about 9KB on each of two opaque posts. The shortfall stays an opaque size gap.
