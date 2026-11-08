# 子树首次缺失定位 / 2026-10-20

限定合同：`diagnostics/subtree-locate-20261020/authorization.json`。只读既有日志和 canonical 消费链。不造节点，不改 facts。这次定位本身没有再跑目标。次数上限已取消。调度仍是 `refuse_host_enumeration`。

## 定位

同源 canonical（source `05102bb5…`，trace pid 48444）在 `attachShadow`（:98）之后，root 上的第一段子树是：

1. :177 `Document.createElement`，返回值就是下一步挂进去的节点。
2. :181 `root.appendChild`，参数与返回都是 `HTMLStyleElement`。
3. 第一次 `root.querySelector(#id)` 在 :797。此时目标节点已经在该 root 的子树里。

patched 日志在 `shadowAttached`（mode=closed，root=`surface-148`）之后没有该 root 的 `appendChild`。下一条表面事件就是 `shadowQuery`，选择器形状 `#id`，结果 null。随后 `zF` 对这个 null 调用 `appendChild`。

所以第一次缺失在 :177 的 create 和 :181 的 root.appendChild，不是查询本身。查询发生时树还是空的；canonical 的第一次查询远在这两步之后。

## 还不能当成下一刀补丁

patched 的 stdout 没有逐次记录 attach 之后的 `createElement`。因此还不能证明 :177 那次调用没发生，只能证明它的产物没有挂到这次返回的 root 上。旧工厂会丢掉 tag 参数，那是另一条已记录的失真，这份日志没有把它和 :177 对上。本合同时不改工厂、不伪造查询命中。

回执：`diagnostics/subtree-locate-20261020/locate-receipt.json`。
