# 身份文档不再泵事件

2026-10-21。`next` 放行 `repair_submit_host_behavior`：baseline `f1e44ef3` 停在 helper 第 1439 行第 21 列，kind `other`，sourceForm `url`。同一 scope 只改一处：`loadIdentityDocument` 打开字符串通道后直接返回，不再创建定时器，也不再调用线程事件泵。eval 剥空白、XHR、脚本时限、`__watchEval` 没改。时限仍是 13。

helper sha256 `7833680f96bce1cc91dc50df409c34a60847ca01479102885a0a1de7cae667f9`。scope 重签为 `75fe61cf541e6e34f494fdf1732f4adb6ddaf6d86473d065344f2418fa6e54d5`。`4b38ab2bb03779b64cac600f247718bd84ceb601f9a2c9753c1dc9daee0aa311` 与 baseline `f1e44ef3dfda48a4aaafa2752655b0c7` 留在 priorScope。

官方 baseline `356e17e4159e4aee8da0a6cc37d3d8c8`：status failed，exitCode 1，timedOut false，约 9.1s。stderr 与 stdout 都是 0 字节，FATAL 计数 0。raw 222 字节，sha256 `534609ca23a0472c035bc74092454398420761e448eb632583db28adac35ac2c`。事件只有 `host-diagnostic` 和 `summary`。没有 `host-observation`。

诊断第 2 行第 3028 列，matched false，source 哈希等于编排脚本。该列在第 2 行以内（行长 23576），落在标识符 `function` 上，不是第 1 行第 75507 列的 `HTMLFormElement.submit`。side 的 class 和 kind 都是 `other`，没有 sourceForm，finished false。这不是慢脚本警告。没有证书 document POST，也没有同租约回读。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。
