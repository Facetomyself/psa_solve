# Function own-flag baseline

Stamp: `repair_submit_host_behavior` / `blocked` / `2026-10-22T07:52:39Z` / session `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`.

The single host change is inside `installLeadingPadFunction`. The inherited `host.__leadingPadFunction` guard is now an own-property check, matching the eval installer. `host.__leadingPadFunction = 1` still follows a successful wrap. Eval, trim, the constructor assignment, the worker no-document branch, and the collector were not edited.

Helper sha256 `15efd13d07648871c8b34e3f18ec6bb58f0a2a2cef360752357ebdc6406e0590`. Scope `81b63573533c8860d5b22152457783497891584e080a9b299e1d37c088fcb493`. Prior scope `d65a15c2e8ac1aa279625ac560d15fea8ff1b443286417e97b60d3f4dae6f0e3` keeps baseline `ecfae641248b448a8f43bfce7e2ddc72`.

Official baseline `847e1482e8a045539e2b0a1feab52878`: pid 31928, exitCode 1, timedOut false, elapsed 22712776800 ns, failure `execution did not complete successfully`. Diagnostic is still in-file line 3 column 544, kind `other`, class `slow-script`, sourceForm `token`, sourceClass `other`. scriptError has no errorName, receiverState, or receiverId. Raw sha256 `3279db9672ab9473b7db77fa43888d05254a826d908eaa41bef9722573665bee`, 221 bytes. Side sha256 `00eaba2f96231c937406f8f1c9856de2b5c66a84721e0ec21c5c6cb99a1f7464`, 935 bytes. Both match the prior receipt. Length column 55373 is still a primitive number. Compile entry is still `unmatched`. Events are `host-diagnostic` and `summary`. `summary.ok` is not `serverAccepted`. matched is false. No certificate document POST and no same-lease readback. `localReproduced`, `serverAccepted`, and `requestBoundaryAligned` stay false. `experimentHygiene` stays `ok`. `hostProbe` stays null.
