# Interfaces

Case: `psa-cf-5s-shield-20260815`

Endpoint catalog. The machine contract is `contracts/request-parameter-lineage.v1.json`. Do not paste raw request bodies.

## Notes

- 挑战链：证书文档 GET 403，orchestrate GET 200，页面 `/fo/` POST 200，Turnstile 主机三次 `/fo/` POST 200，页面清关 `/fo/` POST 200。cookie 名只记 `__cf_bm` 和 `cf_clearance`。
- 业务链：有头在清关之后有证书路径 document POST 200，并写下 `psa-locale` 和 `env`。本地没有这条 POST。
- `jsd` 在业务页之后，不是清关前提。路径写成类别模板，证书编号不进文档。
- 机器表里的 `fo-body` / `form-body` 是类别名。`/fo/` 的线上类型是 `text/plain` 或 `text/html`，不是已还原的表单字段。

<!-- generated:interfaces -->
| id | method | path | payloadShape | parameterCount | evidence |
| --- | --- | --- | --- | --- | --- |
| cert-document-get | GET | /cert/ | none | 1 | evidence/web/ruyitrace/rt_20260929103550_341b734038/evidence-run.json |
| orchestrate-get | GET | /cdn-cgi/challenge-platform/orchestrate | none | 1 | evidence/web/ruyitrace/rt_20260929103550_341b734038/evidence-run.json |
| page-fo | POST | /cdn-cgi/challenge-platform/fo/ | unknown | 1 | evidence/web/ruyitrace/rt_20260929103550_341b734038/evidence-run.json |
| clearance-fo | POST | /cdn-cgi/challenge-platform/fo/ | unknown | 2 | evidence/web/ruyitrace/rt_20260929103550_341b734038/evidence-run.json |
| cert-document-post | POST | /cert/ | form | 2 | evidence/web/ruyitrace/rt_20260929103550_341b734038/evidence-run.json |
<!-- /generated:interfaces -->
