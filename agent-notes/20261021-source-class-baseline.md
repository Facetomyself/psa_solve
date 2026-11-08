# sourceClass 基线 35d601aa

scope `963fff7353f4deda`。helper 的慢脚本侧记现在写入 `sourceClass`，取值只有 empty、probe、helper、page、other。warning 对象没有 sourceName。

官方 baseline `35d601aa61ba43c0acc68b16eec6daa3`：status=failed，exitCode=1，timedOut=false，约 22.7s。failure 是 `execution did not complete successfully`。

side.scriptError：kind=`other`，class=`slow-script`，sourceClass=`other`，第 1 行第 1337365 列。字段是 class、column、kind、line、sourceClass。

sourceClass=`other` 表示 warning 的 sourceName 非空，且不含 probe、helper、page 这三类文件标记。kind 仍是 `other`，所以 sourceName 也不含 `chl_page` 或 `orchestrate`。原文没有落盘。

raw 两行：host-diagnostic matched=false，然后 summary.ok=true。没有 host-observation，没有 wire / necko / resp。

上一回执 `76d1701ab1a94749937cbc0a5d79ac38` 在 priorScope。完成轴保持 false。随后 `next` 是 `verify_host_execution`，带 `no-new-host-surface`。没有授权 repair。
