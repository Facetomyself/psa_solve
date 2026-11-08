# Click install cut — 2026-10-03

Reviewed runner hash left untouched. This run used `diagnostics/click-install-20261003/ruyidom_bridge.click-install.js`. No second causal-observer claim. `serverAccepted` not written.

Session: `evidence/web/click-install-20261003/restricted/a5f1560cff34418a8594433549a87123`
Fresh page 403, orchestrate 200. Engine exit 0.

## Install

`ChromeUtils.exportFunction(armClick, win, { defineAs: "__clickTs" })` threw. `lookupRing` has `click:install:TypeError` and no `click:export`, no `click:arm`. Page probe is still `clickErr=missing`, `clickArm=1`. The message listener in that same `try` did not stay registered. The 400ms poll still logged `click:f0` then `click:f1:c1`, and `ptr:8`.

The stored label is the exception name. The message was not kept.

## Three measurements

| check | this run | prior local | headed |
| --- | --- | --- | --- |
| challenge FO request bytes, 3rd and 4th | 83490, 86647 | 83372, 86530 | 92460, 95735 |
| page FO `cf-chl-out` class | `noform`, length class 3488 | `noform`, 3488 | form after the html responses |
| cert document POST | absent | absent | present |

`forms=0`, `submits=0`. Last page FO still carries the `cf_clearance` name. `msgHit` is `interactiveEnd,complete`.

The two large request lengths moved by about 120 bytes. They stay in the short class. This cut does not move the external boundary.
