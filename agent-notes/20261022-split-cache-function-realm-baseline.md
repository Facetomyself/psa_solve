# split cache function-realm baseline

Stamp: `repair_submit_host_behavior` / `blocked` / `2026-10-22T11:42:26Z` / session `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`.

Line 3 column 544 is `.` on an offset-object property. The value is decoder slot 1567. The decoder then splits one 32116-character table on a one-character separator. That read is not itself `String.prototype.split`, so a wrapper that never replaces the script realm's split cannot intercept it.

The previous installer returned as soon as `Cu.evalInSandbox` did not throw. In this runtime that call exists, so the realm `Function` path never ran. This beat keeps the same cache and runs the `Function` path as well. A fresh copy is still returned. No host getter was added for the dot. The clock, the collector, the orchestrate source, the VM, the worker no-document branch, and the 13s content budget were not edited.

Helper sha256 `626e1672475856e01ebcd3c69726b450e4486eb14d49ef39c87221ed598eb4b0`. Scope `e9dbde8df03e1ac2db4b40b61d5b3e5625ccd6d9379083ef12041f42426a7e32`. Prior scope `dfcc9fb8edadf0fe49c68ec02dd474b54fa249000b2514e3259c13fd6067baeb` keeps baseline `31affd819d1e447dbd5025b49a60116c`.

Official baseline `40b28d0a4e224679920a7f70c9a1b110`: pid 35896, exitCode 1, timedOut false, elapsed 22923205800 ns, failure `execution did not complete successfully`. The column did not move. Diagnostic is still in-file line 3 column 544, kind `other`, class `slow-script`, sourceForm `token`, sourceClass `other`. scriptError has no errorName, receiverState, or receiverId. Raw sha256 `3279db9672ab9473b7db77fa43888d05254a826d908eaa41bef9722573665bee`, 221 bytes. Side sha256 `00eaba2f96231c937406f8f1c9856de2b5c66a84721e0ec21c5c6cb99a1f7464`, 935 bytes. Both match `31affd819d1e447dbd5025b49a60116c`. Length column 55373 is still a primitive number. Compile entry is `unmatched`. Events are `host-diagnostic` and `summary`. `summary.ok` is not `serverAccepted`. matched is false. No certificate document POST and no same-lease readback. `localReproduced`, `serverAccepted`, and `requestBoundaryAligned` stay false. `experimentHygiene` stays `ok`. `hostProbe` stays null.

Both install paths left the watchdog on the same property read. Completion facts stay false.

Column 544 is still the released slow-script shape, so `web_case.py next` stamped `repair_submit_host_behavior`. The column is not HTMLFormElement.submit at line 1 column 75507.
