# Function own-constructor baseline

Stamp: `verify_host_execution` / `blocked` / `2026-10-22T08:11:12Z` / session `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`.

The single host change is inside `installLeadingPadFunction`. An inherited `Function` no longer counts as already wrapped. The seen flag applies only when `Function` is an own property of this host. The host own-property flag, the eval own-property flag, trim, the constructor assignment, the worker no-document branch, and the collector were not edited.

Helper sha256 `d076b4636fc47655ba1a2f709326c04951d54fbd2b67289d53004198b67c8f8e`. Scope `5ecc4748d91d9abaa39380450e22bff64697cc7a44e84170362d32a513362c23`. Prior scope `81b63573533c8860d5b22152457783497891584e080a9b299e1d37c088fcb493` keeps baseline `847e1482e8a045539e2b0a1feab52878`.

Official baseline `388141dd6bb54faf88c611ddcf998b7b`: pid 53228, exitCode 1, timedOut false, elapsed 25143934400 ns, failure `execution did not complete successfully`. Diagnostic is line 1 column 34, kind `other`, class `slow-script`, sourceForm `token`, sourceClass `other`. scriptError has no errorName, receiverState, or receiverId. Raw sha256 `36ed24724afec44742581568196e141703169f21e5bfd9370eb76f0665f375e7`, 220 bytes. Side sha256 `784e312374bf73e8e4084e1c2e326d29dc475ef05181c385660ab3903746b740`, 927 bytes. Neither matches `847e1482e8a045539e2b0a1feab52878`. Length column 55373 is still a primitive number. Compile entry is `eval`, realm is `Sandbox`, match is `source`. Events are `host-diagnostic` and `summary`. `summary.ok` is not `serverAccepted`. matched is false. No certificate document POST and no same-lease readback. `localReproduced`, `serverAccepted`, and `requestBoundaryAligned` stay false. `experimentHygiene` stays `ok`. `hostProbe` stays null.

The bound-source in-file check treats column 34 as inside line 1, and that column is not a released stop, so `web_case.py next` stamped `verify_host_execution` with `no-new-host-surface`. The column is not HTMLFormElement.submit at line 1 column 75507.
