# 第 1439 行是看门狗落点

2026-10-21。`next` 仍是 `verify_host_execution`，`turnGate=blocked`，约束含 `no-new-host-surface`。helper 没有改，baseline 没有重跑，完成轴没有写。

baseline `f1e44ef3dfda48a4aaafa2752655b0c7` 的 side 来自慢脚本警告。helper 只在警告文本是脚本超时终止时写入 `class=slow-script`，并带上 `sourceClass` 和 `sourceForm`。这张 side 的 kind 是 `other`，sourceForm 是 `url`，sourceClass 是 `helper`，第 1439 行第 21 列。sourceForm `url` 表示 sourceName 含 `://`，sourceClass `helper` 表示其中含有 `document-principal`。

helper 第 1439 行是 `wrapped` 里的 `var origOpen = slot.origOpen`。第 21 列是 `slot`。`contentOpenSlot` 返回普通对象，`origOpen` 是数据属性，值在返回前已经取过：`proto && proto.open` 在该函数的 return 上。第 1439 行只读这个已经存好的值，不再访问 document 原型的 `open`。

因此这列不是 `origOpen` 的 getter 失败。看门狗把超时记在 helper 脚本当时的程序位置上，这个位置是 `contentOpenSlot` 返回之后的属性读取。`proto.open` 的那次取值在 `contentOpenSlot` 内部，行号不是 1439。剥空白循环在第 1391 行附近，也不是这列。

编排源只有 3 行。kind `other` 且 sourceForm `url` 不放行宿主修补。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。没有证书 document POST，也没有同租约回读。
