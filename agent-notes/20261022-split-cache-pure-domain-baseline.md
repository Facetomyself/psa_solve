# Split cache pure domain / 2026-10-22

Stamp `2026-10-22T14:35:56Z`, action `repair_submit_host_behavior`, turnGate `blocked`, session `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`.

The Function-realm cache install did not move column 544. This beat changed only the cache applicability. A hit now requires a primitive string receiver, a primitive one-character separator, and a string of at least 4096 characters. The wrapper does not call `String()` before the native method. Boxed receivers and object separators, including a custom `Symbol.split`, stay on the native method. A pure hit still returns a fresh array slice. No host API was added for the column 544 dot. The orchestrate script, the VM, the clock, the worker no-document branch, and the 13 second limit were not changed.

Helper sha256 `7a5996854ea9d800955fba83683292afb6098473e4f11c901a578e77427fce43`. Scope `c8e9652b6374511c8c9bcc30cf43e50a8bb1b67252f55e33091206c848607488`. Prior scope `e9dbde8df03e1ac2db4b40b61d5b3e5625ccd6d9379083ef12041f42426a7e32` keeps baseline `40b28d0a4e224679920a7f70c9a1b110`.

## Official baseline

Directory `a5c33751e7a24338bd7dc2959c349599`. Execution sha256 `a734c702a2e0d7c2d5d83990303c613c37f2cc745dd8e64151b78c265b46d1a8`. pid 39080, exitCode 1, timedOut false, elapsed 22911411500 ns, failure `execution did not complete successfully`.

The stop is still source line 3 column 544, kind `other`, class `slow-script`, sourceForm `token`, sourceClass `other`. raw sha256 `3279db9672ab9473b7db77fa43888d05254a826d908eaa41bef9722573665bee`, 221 bytes. side sha256 `00eaba2f96231c937406f8f1c9856de2b5c66a84721e0ec21c5c6cb99a1f7464`, 935 bytes. Those two hashes match `40b28d0a4e224679920a7f70c9a1b110`. `compileEntry` and `compileRealm` are `unmatched`. `compileMatch` is `absent`. The side file has no split-hit field. The column number is not evidence that the cache ran. Narrowing the cache is not a root-cause claim for column 544.

## Node solver

Two fresh processes of `runtime/run.js`. Each process fetched its own challenge page and orchestrate script, then ran that entry. No browser session and no historical challenge body were copied in.

| | session 1 | session 2 |
| --- | --- | --- |
| started | 2026-10-22T14:33:28.755Z | 2026-10-22T14:34:08.913Z |
| page fetch | 403 | 403 |
| orchestrate fetch | 200 | 200 |
| solver request classes | none | none |
| solver response classes | none | none |
| certificate document POST | no | no |
| same-lease read about 5s later | 403, challenge, title length 16, body length class 5000-19999 | 403, challenge, title length 16, body length class 5000-19999 |

The two runs agree. The certificate document POST did not happen.

## Parity

The headed oracle in `agent-notes/trace-compare-20261005.md` has a clearance exchange and then a certificate document POST, method POST, status 200. These Node runs have no solver request, so they have no method, URL class, status, or body-length class for that exchange or that POST. The classes do not agree. The 403 challenge readback is not the certificate page.

## Facts

`localReproduced`, `serverAccepted`, and `requestBoundaryAligned` stay false. `experimentHygiene` stays `ok`. `hostProbe` stays null. `summary.ok` on the host receipt is not `serverAccepted`.
