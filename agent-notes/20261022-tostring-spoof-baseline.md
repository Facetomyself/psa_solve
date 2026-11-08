# toString spoof baseline

Stamp: `repair_submit_host_behavior` / `blocked` / `2026-10-22T10:04:16Z` / session `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`.

The one host change is inside the existing `Function.prototype.toString` spoof in `installLeadingPadEval`. When `this` is that spoof, it reports the captured native toString. When `this.__leadingPadFunction` is set, it reports the native Function string captured before the wrap. Eval still reports its captured native string. `installLeadingPadFunction`, the clock, the worker no-document branch, and the collector were not edited. No second Function wrap was added.

Helper sha256 `77765cd0c1d74e793df1385542af08308cc1ad5b0b171d1cffe2eddc67009e4a`. Scope `a4846ae48d88eb23358b1fdbfdb97033590e9e50fefd7352f702482db81b3f45`. Prior scope `2492e570730c919d88c1b8bab3e861e5b39d931b76faf63e854507f7b0a6b9b5` keeps baseline `1bffab3b60ae46bf87d6b403c65a4d5a`.

Official baseline `5e9b1196a2594d00a94b4ac5a85e90f0`: pid 18296, exitCode 1, timedOut false, elapsed 22722664000 ns, failure `execution did not complete successfully`. The column did not move. Diagnostic is still in-file line 3 column 544, kind `other`, class `slow-script`, sourceForm `token`, sourceClass `other`. scriptError has no errorName, receiverState, or receiverId. Raw sha256 `3279db9672ab9473b7db77fa43888d05254a826d908eaa41bef9722573665bee`, 221 bytes. Side sha256 `00eaba2f96231c937406f8f1c9856de2b5c66a84721e0ec21c5c6cb99a1f7464`, 935 bytes. Both match `1bffab3b60ae46bf87d6b403c65a4d5a`. Length column 55373 is still a primitive number. Compile entry is `unmatched`. Events are `host-diagnostic` and `summary`. `summary.ok` is not `serverAccepted`. matched is false. No certificate document POST and no same-lease readback. `localReproduced`, `serverAccepted`, and `requestBoundaryAligned` stay false. `experimentHygiene` stays `ok`. `hostProbe` stays null.

Column 544 is still the released slow-script shape, so `web_case.py next` stamped `repair_submit_host_behavior`. The column is not HTMLFormElement.submit at line 1 column 75507.
