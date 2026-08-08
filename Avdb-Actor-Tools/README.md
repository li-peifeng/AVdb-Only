# Avdb Actor Tools 发布文件

这个目录保存 Avdb Actor Tools 的可安装插件和 Emby 计划任务自动更新所需的版本清单。

文件说明：

- `Avdb.ActorTools.Plugin.dll`：放入 Emby 的 `plugins` 目录的插件文件。
- `plugin-manifest.json`：计划任务读取的版本清单，包含版本、下载地址、兼容版本和 SHA-256。
- `Avdb.ActorTools.Plugin.dll.sha256`：插件 DLL 的 SHA-256 校验文件。

当前发布版本：`3.0.0`

## 首次安装

将 `Avdb.ActorTools.Plugin.dll` 放入 Emby Server Data Folder 下的 `plugins` 目录，然后重启 Emby。
不要把 `MediaBrowser.*.dll`、`Emby.*.dll` 或其他 SDK 依赖一起复制进去；这些文件由 Emby Server 提供。

首次安装 `3.0.0` 后，Emby 的计划任务页面会出现“Avdb Actor Tools 插件自动更新”。任务安装后
默认不设置自动触发器，不会自行运行；用户可以在 Emby 计划任务页面自行添加触发时间或间隔，
也可以随时手动运行。检查到新版本后，插件会验证清单和 DLL，备份旧文件为
`Avdb.ActorTools.Plugin.dll.old`，替换成功后调用 Emby 自重启。

版本清单的固定地址：

```text
https://raw.githubusercontent.com/li-peifeng/AVdb-Only/main/Avdb-Actor-Tools/plugin-manifest.json
```

`2.0.1` 及更早版本不包含自动更新任务，必须先手动安装 `3.0.0`。已经安装 `2.1.0` 的实例也必须
先手动替换为 `3.0.0`，因为 `2.1.0` 的下载任务存在进度回调缺失问题，无法自行下载修复版本。
