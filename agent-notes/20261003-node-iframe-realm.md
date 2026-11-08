# 生产 runtime iframe realm（2026-10-03）

离线命令：`D:\reverse_ENV\tools\node\node.exe runtime\run.js frame`。未开浏览器，未发网络，未回放历史 FO body / cookie / token。退出码 0 只表示 runner 完成观测，`ok:false` 是脚本抛错，不是补环境完成。

## 第 1 刀

- 假设：把同一份 Turnstile iframe inline script 放进独立子 `vm.Context`（`window/self/globalThis` 为自身，`parent/top` 为父窗口代理，iframe `contentWindow/contentDocument` 指向子 realm）后，脚本若会真实 `define` `PQak3`，`framePqOwn` 会变成 true。`parent.postMessage` 只记次数与 data 的 typeof/constructor，不投递 MessageEvent。
- 改动文件：`runtime/lib/iframe-realm.js`（新增），`runtime/run.js`（新增 `frame` 模式，不替换原求解 CLI）。
- 脚本：238636 bytes，SHA-256 `05102bb5158cd0ba9a41329021f124cad8778a9a556db9a0e802b11c07115262`。未记录脚本正文。
- 重跑前：生产 runtime 没有独立 iframe realm；canary `v8-20261003152520-xgv5ln` 为 `frameEval=ok`、`chlOptKeys=37`、`framePqType=undefined`、`framePqOwn=false`，随后 DOM/状态 TypeError，`sendCount` 未形成 FO。
- 重跑后：`frameEval=ok`，`chlOptKeys=37`，`framePqType=undefined`，`framePqOwn=false`，`parentPqOwn=false`，`throwName=TypeError`，`throwMessage=h[bb(...)] is not a constructor`，`parentPostMessageCount=0`，`sendCount=0`，`boundary=boundary-unchanged`。

## 停止

抛错名仍是 TypeError，`PQak3` own/type 都没变，也没有 send。这不是新的异常名，没有越过 canary 的 DOM/状态 TypeError 进入 FO / response boundary。按停止规则不把结果改写成 `boundary-moved`。未做 postMessage 投递、未补 query/innerText 假元素、未加 eval/blob loader，未写 `window.PQak3`。

## 结论

`PQak3` 没有出现真实 define。独立 iframe realm 能执行这段 238636 byte inline script，并把 `_cf_chl_opt` own-key count 记到 37，但子窗口和父窗口都没有 `PQak3` own property。卡住的仍是与 canary 同级的 DOM/状态 TypeError（本刀观测到的消息是 `is not a constructor`，canary 定时器消息是 `is not a function`），`boundary-unchanged`。`environmentPatchGate.status`、`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 not-ready / false。
