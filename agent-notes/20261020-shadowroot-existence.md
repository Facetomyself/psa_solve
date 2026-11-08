# ShadowRoot append 存在性 / 2026-10-20

本拍只确认返回的 ShadowRoot 在不在，以及这条链已经读过的接合行为。没有改 `body-shadow-surface.cjs`，没有打开 `Document.createElement`，没有跑 live，没有改 facts、workflow 业务轴或 `environmentPatchGate`。

## 浏览器事实

canonical source `05102bb5…`，run `rt_20260929103550_341b734038`。`attachShadow` 之后，`Document.createElement` :177 的返回值在 :181 作为 `HTMLStyleElement` 被 append 进该 root（`argEqualsReturn`）。第一次查询在 :797，命中当时已经在该 root 里的节点。

## 实现已经会留下

`diagnostics/shadowroot-repair-20261020/body-shadow-surface.cjs` 里，返回 root 的 `appendChild` 先 `insert` 到这个 root 的私有子列表，再发出 `shadowAppend`。成功调用不会把子节点记到别的树，也不会在查询里伪造命中。

## 调用没有落到这个 root

patched stdout 在 `shadowAttached`（root `surface-148`，`mode=closed`）之后的下一条表面事件就是同一 root 的 `shadowQuery`，选择器形状 `#id`，结果 null，随后 `zF` 对这个 null 调用 `appendChild`。整份 stdout 没有 `shadowAppend`。`boundary-comparison.json` 的 patched `rootAppendCount` 为 0。attach 和这次查询之间没有“root 拒绝子节点”的异常；唯一未捕获错误在查询之后，接收者是 null，不是这个 root。

因此现有 append 实现已经会留下子节点，缺失的是调用没发生。本拍不改 append 语义，也不为了看起来有子树去插入节点。

## 阻塞

同一属性的 append 实现已经在。第一段缺失构造是 `Document.createElement`。本拍禁止打开那个新表面，没有改工厂，也没有改 `createElement` / `createElementNS` / `setAttribute` / selector fallback。

`status=blocked`。`environmentPatchGate` 仍是 `not-ready`。`businessAcceptance=not-asserted`。没有写 `serverAccepted`。本拍测试 `not-run`。
