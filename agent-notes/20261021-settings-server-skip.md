# settings 测试地址停掉非本地 FATAL

2026-10-21。上一章是 `verify_host_execution`，约束含 `no-new-host-surface`。只加了一处已经存在的远程设置跳过：`services.settings.server` 设为 `data:,#remote-settings-dummy/v1`。`Utils.shouldSkipRemoteActivityDueToTests` 在 `MOZ_DISABLE_NONLOCAL_CONNECTIONS` 下认这个地址，于是不再连 `firefox.settings.services.mozilla.com`。没有改采集器，没有改 `ruyidom.js`，没有写完成轴。

`test_shipped_settings_server_skips_nonlocal_sync` 跑过，输出 `settings-server-ok`。

同一条构造器探针重跑：墙钟 22.472 秒，side 存在。`constructorExit` 为 `returned`，`finished` 为 true，`threw` 为空。`scriptError` 是 slow-script，kind `other`，sourceForm `token`，sourceClass `other`，第 1 行第 1337365 列。stderr 尾部没有 settings FATAL。CLI 仍是 `RUYIDOM_OUTPUT_PARSE_FAILED`，会话层 exitCode 为 -1，因为进程在 side 写出之后没有 JSON 结果行。

helper 从 `2d1afb24f9708bb6` 变为 `faff9c5239ffd0a1fd821f201a8a18f3c9a474712ae4135ce6db29d5efe70891`。随后 `next` 是 `verify_host_scope`，`turnGate=blocked`，仍含 `no-new-host-surface`。这一拍没有重绑 scope，也没有重跑正式 baseline。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。
