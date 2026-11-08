# Sandbox eval own-flag baseline

Stamp: `verify_host_execution` / `blocked` / `2026-10-22T07:32:09Z` / session `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`.

The named repair is in `installLeadingPadEval` only. The inherited `host.__leadingPad` return is now `Object.prototype.hasOwnProperty.call(host, "__leadingPad")`. `host.__leadingPad = 1` still runs after a successful wrap. `installLeadingPadFunction` was not changed. The worker no-document branch was not changed. `trimInCompartment`, `leadingPadSource`, and `RealFunction.prototype.constructor=fn` were not changed. The `Number.prototype.length = 0` statements stay absent.

Helper sha256 `5a7b10ef62841c551a97d025f182c9b2872b8f338ed36d49d8c2aabc4c8da1c6`. Scope `d65a15c2e8ac1aa279625ac560d15fea8ff1b443286417e97b60d3f4dae6f0e3`. Prior scope is `535f4944dfc84bb3b47d1cda5535bb6b41e027776cd8db7f21c788edf2c552c8` with baseline `13e79448ee6a4d55b6dff4d705bdfa0b` and execution `a2678312c86237cf27cbcff250e8fc409df0bd26bf312b43bd423ef79836b993`.

Official baseline `ecfae641248b448a8f43bfce7e2ddc72`: pid 17740, exitCode 1, timedOut false, elapsed 24723503400 ns, failure `execution did not complete successfully`. Execution sha256 `d0e80def1bd99bac0e340cc1f906a0457162cf43683ae98016971c82e85fb433`. Diagnostic is in-file line 3 column 544, kind `other`, class `slow-script`, sourceForm `token`, sourceClass `other`. Raw sha256 `3279db9672ab9473b7db77fa43888d05254a826d908eaa41bef9722573665bee`, 221 bytes. Side sha256 `00eaba2f96231c937406f8f1c9856de2b5c66a84721e0ec21c5c6cb99a1f7464`, 935 bytes. Events are `host-diagnostic` and `summary`. `summary.ok` is true and is not `serverAccepted`. matched is false. stdout is empty.

Length observation is unchanged: column 55373, object `number`, source `call-argument`, holder `primitive`, proto `none`, this `Sandbox`, callee entry `eval`, realm `Sandbox`. Compile entry is `unmatched`, realm `unmatched`, match `absent`. No worker field. Column 544 is not a released in-file stop, so `_out_of_file_slow_script` returns null and `next` stays on `verify_host_execution` with `no-new-host-surface`.

No certificate document POST and no same-lease readback. `localReproduced`, `serverAccepted`, and `requestBoundaryAligned` stay false. `experimentHygiene` stays `ok`. `hostProbe` stays null.
