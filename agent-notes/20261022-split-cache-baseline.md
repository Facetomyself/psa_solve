# split cache baseline

Stamp: `repair_submit_host_behavior` / `blocked` / `2026-10-22T11:11:18Z` / session `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`.

The one host change caches `String.prototype.split` for one long string and a one-character separator. `installLeadingPadFunction` installs it before the inherited-Function return, so the page window, the sandbox, and a document global get it. The worker no-document branch does not. A hit returns a fresh `slice()` copy. Own `toString` and the existing `Function.prototype.toString` spoof both report the captured native split string when `__splitCache` is set. The clock, the collector, the orchestrate source, and the VM were not edited. No host getter was added for the dot at column 544.

Helper sha256 `89d716290d16cceb7fc3ccba18e0e341f9b66736ee488441e4c30da4850dbe7f`. Scope `7729a0e3ea0f8a2176027d0f56252b2bfb86c442390d0eb3c50bad3cc937f806`. Prior scope `a4846ae48d88eb23358b1fdbfdb97033590e9e50fefd7352f702482db81b3f45` keeps baseline `5e9b1196a2594d00a94b4ac5a85e90f0`.

Official baseline `6b9b8eff2f95450dab14641d085fe8a2`: pid 11636, exitCode 1, timedOut false, elapsed 22719680500 ns, failure `execution did not complete successfully`. The column did not move. Diagnostic is still in-file line 3 column 544, kind `other`, class `slow-script`, sourceForm `token`, sourceClass `other`. scriptError has no errorName, receiverState, or receiverId. Raw sha256 `3279db9672ab9473b7db77fa43888d05254a826d908eaa41bef9722573665bee`, 221 bytes. Side sha256 `00eaba2f96231c937406f8f1c9856de2b5c6cb99a1f7464`, 935 bytes. Both match `5e9b1196a2594d00a94b4ac5a85e90f0`. Length column 55373 is still a primitive number. Compile entry is `unmatched`. Events are `host-diagnostic` and `summary`. `summary.ok` is not `serverAccepted`. matched is false. No certificate document POST and no same-lease readback. `localReproduced`, `serverAccepted`, and `requestBoundaryAligned` stay false. `experimentHygiene` stays `ok`. `hostProbe` stays null.

The decoder calls the same function that splits one long table on every call. Caching that split did not leave column 544 inside the 13s watchdog. The loop may still be too large after the cache, or that call may not be using the wrapped `String.prototype.split`. Completion facts stay false.

Column 544 is still the released slow-script shape, so `web_case.py next` stamped `repair_submit_host_behavior`. The column is not HTMLFormElement.submit at line 1 column 75507.
