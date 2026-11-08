# 2026-10-21 同 scope 修补未落地

`web_case.py next` 盖章 `repair_submit_host_behavior`，`turnGate=blocked`。约束含 `same-scope`、`one-host-behavior`、`submit-callsite-only`、`no-completion-facts`、`tool-evidence-required`。

用户已放行：kind=`other` 且 sourceForm=`token` 的源文件外慢脚本，可以做同一 scope 的一处宿主行为。回执 `329f75aa9405418dbc6332d9af2780a8`，scope `66687399f484a9e2`。失败位置是第 1 行第 1337365 列。调用点仍是 `HTMLFormElement.submit` 第 1 行第 75507 列。该列没有写成 host-observation。

已索引笔记和 browser-fact 摘要里，提交链点名的目的地是这次 `HTMLFormElement.submit`。同索引里另外出现的 `Element.attachShadow`、`Document.createElement`、`Document` body getter、`performance.getEntries` 已经装过，或属于另一面。Patch Queue 开放项「清关后不建表」没有给出这一列的属性名。因此这一处宿主行为没有改 helper、runner 或 scope。

已试过且保持原样：无参 `Date` 与 `Date.now` 同锚点；`dom.max_script_run_time=13`；pad eval 短路保持删除。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。没有证书 document POST，没有同租约回读。
