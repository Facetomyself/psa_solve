# 2026-10-22 padText charCodeAt reject named

baseline `a92ebd317fe8423bb55c52c3323a9b44` 仍停在第 1 行第 1337365 列。页面窗调用、沙箱调用、以及删掉 `if (!hasDoc) return;` 都没有改变 raw/side。

`padText` 在 `toString` 得到字符串之后，仍执行 `if (head !== via.charCodeAt(0)) return null;` 和 `if (tailCode !== via.charCodeAt(last)) return null;`。对不上就丢掉文本，原对象继续进入 eval。

下一处只允许删掉这两句并直接 `return via`。不得改调用点，不得恢复 document 早退。

- helper `5d577ded69e368de4e8c0a8b4f075f98768d560bc3e21781ff1f43268dd78109` 未改
- scope `706155d2eb5880c423132aff6ef45bc92808ad9027fad0dbc0005904e1886a64` 未重签
- 盖章 `repair_pad_text_charcode_reject` / `blocked` / `2026-10-22T04:09:31Z`
- 完成轴保持 false
