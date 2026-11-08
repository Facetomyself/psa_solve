# ruyijs parameter-analysis reopen: isolation now enforced

Previous completed run `rj_20261102062310_d7463f5c` finished before the public adapter
proved no-egress. Its `evidence-run.json` metrics record `proxy=false` and
`offline-network` as a self-signed pass. Unmatched Necko was not shown to stay
on a loopback sink.

`tools/web-reverse/run_ruyijs.py` now binds parameter-analysis to an adapter-owned
loopback no-egress sink, proves victim.hits=0 / inbound>=1 / forwarded=0, then
runs `_analyze_on` on that Context. Caller `params.proxy` stays rejected.

The old run remains on disk. It is not isolation-proven, so plane receipt
`ruyijs` returns to `missing` and `parameterAnalysis` returns to `want` for one
new isolated analysis. This does not name `hostBlocker`, `gapKind`, or
`firstDivergence`. attachShadow existence is not re-issued.
