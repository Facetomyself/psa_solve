# Function inherited-skip baseline

Stamp: `repair_submit_host_behavior` / `blocked` / `2026-10-22T08:24:24Z` / session `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`.

Baseline `388141dd6bb54faf88c611ddcf998b7b` stopped at line 1 column 34. On the bound source that column is inside `window` at the start of an assignment whose right-hand side is `false`. There is no `for` or `while` before it. The engine kind is `other` and sourceForm is `token`, so the gate's in-file check is only `column <=` the bound line length. The stop appeared after `installLeadingPadFunction` shadowed an inherited Function with a second wrapper.

The correction returns when `Function` is not an own property of this host, or when that own constructor is already wrapped. An own, not-yet-wrapped constructor is still replaced. Eval, trim, the constructor assignment, the worker no-document branch, and the collector were not edited.

Helper sha256 `af0511a8bf8ff45166b3d1c5d2778e5155dd4bb476bca3500608c3e9a1a597c2`. Scope `2492e570730c919d88c1b8bab3e861e5b39d931b76faf63e854507f7b0a6b9b5`. Prior scope `5ecc4748d91d9abaa39380450e22bff64697cc7a44e84170362d32a513362c23` keeps baseline `388141dd6bb54faf88c611ddcf998b7b`.

Official baseline `1bffab3b60ae46bf87d6b403c65a4d5a`: pid 29620, exitCode 1, timedOut false, elapsed 25147664100 ns, failure `execution did not complete successfully`. Diagnostic is again in-file line 3 column 544, kind `other`, class `slow-script`, sourceForm `token`, sourceClass `other`. scriptError has no errorName, receiverState, or receiverId. Raw sha256 `3279db9672ab9473b7db77fa43888d05254a826d908eaa41bef9722573665bee`, 221 bytes. Side sha256 `00eaba2f96231c937406f8f1c9856de2b5c66a84721e0ec21c5c6cb99a1f7464`, 935 bytes. Both match `847e1482e8a045539e2b0a1feab52878`. Length column 55373 is still a primitive number. Compile entry is `unmatched`. Events are `host-diagnostic` and `summary`. `summary.ok` is not `serverAccepted`. matched is false. No certificate document POST and no same-lease readback. `localReproduced`, `serverAccepted`, and `requestBoundaryAligned` stay false. `experimentHygiene` stays `ok`. `hostProbe` stays null.

Column 544 is the released slow-script shape, so `web_case.py next` stamped `repair_submit_host_behavior`. The column is not HTMLFormElement.submit at line 1 column 75507.
