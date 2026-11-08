# split cache realm baseline

Stamp: `repair_submit_host_behavior` / `blocked` / `2026-10-22T11:24:38Z` / session `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`.

The previous chrome assignment of the long-string, one-character `String.prototype.split` cache did not replace the method the sandbox script calls. This beat moved that same cache into the realm: `Cu.evalInSandbox` first, otherwise `new host.Function`. A hit still returns a fresh `slice()` copy. Own `toString` and the existing spoof still report the captured native split string when `__splitCache` is set. No host getter was added for the dot at column 544. The clock, the collector, the orchestrate source, the VM, the worker no-document branch, and the 13s content budget were not edited.

Helper sha256 `b7354c950393decba05d7b9d48c36906fd124c6a82ce288c51ef6b09b96ccd5e`. Scope `dfcc9fb8edadf0fe49c68ec02dd474b54fa249000b2514e3259c13fd6067baeb`. Prior scope `7729a0e3ea0f8a2176027d0f56252b2bfb86c442390d0eb3c50bad3cc937f806` keeps baseline `6b9b8eff2f95450dab14641d085fe8a2`.

Official baseline `31affd819d1e447dbd5025b49a60116c`: pid 45624, exitCode 1, timedOut false, elapsed 23122270800 ns, failure `execution did not complete successfully`. The column did not move. Diagnostic is still in-file line 3 column 544, kind `other`, class `slow-script`, sourceForm `token`, sourceClass `other`. scriptError has no errorName, receiverState, or receiverId. Raw sha256 `3279db9672ab9473b7db77fa43888d05254a826d908eaa41bef9722573665bee`, 221 bytes. Side sha256 `00eaba2f96231c937406f8f1c9856de2b5c66a84721e0ec21c5c6cb99a1f7464`, 935 bytes. Both match `6b9b8eff2f95450dab14641d085fe8a2`. Length column 55373 is still a primitive number. Compile entry is `unmatched`. Events are `host-diagnostic` and `summary`. `summary.ok` is not `serverAccepted`. matched is false. No certificate document POST and no same-lease readback. `localReproduced`, `serverAccepted`, and `requestBoundaryAligned` stay false. `experimentHygiene` stays `ok`. `hostProbe` stays null.

The realm install did not leave column 544 inside the 13s watchdog. Either that call still does not use the wrapped `String.prototype.split`, or the loop stays too large after a cache hit. Completion facts stay false.

Column 544 is still the released slow-script shape, so `web_case.py next` stamped `repair_submit_host_behavior`. The column is not HTMLFormElement.submit at line 1 column 75507.
