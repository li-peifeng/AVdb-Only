<p align="center">
  <a href="https://peifeng.li"><img width="184" alt="AVDB logo" src="../../../public/logo.svg" /></a>
</p>
<p align="center">
  <a href="https://hub.docker.com/r/leolitaly/avdb"><img src="https://img.shields.io/docker/pulls/leolitaly/avdb?color=%2348BB78&logo=docker&label=pulls" alt="Docker pulls" /></a>
</p>

# Avdb Magic Tools 客户端自动化注入工具

本目录提供一个交互式 Bash 工具，用于把 `AvdbMagicTools.js` Loader 注入 Emby 官方
macOS 客户端或 Android APK，并完成副本制作、依赖检查、重新签名、打包和结果校验。

[插件安装与配置](../README.md) · [插件更新日志](../CHANGELOG.md)

本工具用于加载客户端中的插件网页功能。通过 Emby API 读取 NGi STRM 原片大小不需要客户端注入；直接访问 Emby 服务器自带的 Web 页面也由服务端插件处理注入。

脚本默认在当前用户目录创建：

```text
~/AvdbMagicTools
```

所选原文件只会被读取和复制。解包、修改、签名、打包、日志和输出文件全部留在这个工作
目录中，不会直接修改用户选择的 `.app`、`.dmg`、`.zip` 或 `.apk`。

## 目录文件

| 文件 | 用途 |
| --- | --- |
| `bootstrap.sh` | 远程启动入口；下载并校验下面两个文件，再启动主脚本 |
| `avdb-magic-tools-injector.sh` | 自动化注入、签名和打包主脚本 |
| `AvdbMagicTools.js` | 与当前插件客户端协议配套的稳定 Loader |
| `SHA256SUMS` | 本次发布文件的 SHA-256 |

## 一条 SSH 命令远程下载运行

把 `USER@HOST` 换成实际 SSH 用户和主机：

```bash
ssh -t USER@HOST \
  'curl -fsSL "https://raw.githubusercontent.com/li-peifeng/AVdb-Only/refs/heads/main/Avdb-Magic-Tools/Client-Injector/bootstrap.sh?cacheBust=$(date +%s)" | bash'
```

`-t` 很重要：它给交互菜单、路径输入、依赖安装确认和签名密码输入分配终端。通过 SSH
运行时不会打开远端图形文件选择器；请按提示粘贴远端机器上的文件绝对路径。

已经登录 SSH 后，可直接运行：

```bash
curl -fsSL "https://raw.githubusercontent.com/li-peifeng/AVdb-Only/refs/heads/main/Avdb-Magic-Tools/Client-Injector/bootstrap.sh?cacheBust=$(date +%s)" | bash
```

也可以跳过菜单并直接指定远端输入文件：

```bash
# Android APK
ssh -t USER@HOST \
  'curl -fsSL "https://raw.githubusercontent.com/li-peifeng/AVdb-Only/refs/heads/main/Avdb-Magic-Tools/Client-Injector/bootstrap.sh?cacheBust=$(date +%s)" | bash -s -- --android /absolute/path/Emby.apk'

# macOS 应用（目标主机必须是 macOS）
ssh -t USER@HOST \
  'curl -fsSL "https://raw.githubusercontent.com/li-peifeng/AVdb-Only/refs/heads/main/Avdb-Magic-Tools/Client-Injector/bootstrap.sh?cacheBust=$(date +%s)" | bash -s -- --mac /Applications/Emby.app'
```

远程入口会把经过 SHA-256 校验的主脚本和 Loader 保存到
`~/AvdbMagicTools/bootstrap/`。再次运行时，旧下载会先复制到
`~/AvdbMagicTools/bootstrap/archive/`。

> 远程执行前可以先单独下载并检查 `bootstrap.sh`。入口脚本只下载本目录内固定名称的
> 主脚本和 Loader，且任何一个文件校验值不一致都会立即停止。

## 本地运行

克隆仓库后运行：

```bash
cd Avdb-Magic-Tools/Client-Injector
./avdb-magic-tools-injector.sh
```

或只下载入口脚本：

```bash
curl -fLO "https://raw.githubusercontent.com/li-peifeng/AVdb-Only/refs/heads/main/Avdb-Magic-Tools/Client-Injector/bootstrap.sh"
bash bootstrap.sh
```

启动后菜单为：

```text
1. macOS Emby 官方原版（ARM64 / Intel AMD64）
2. Android Emby 官方原版（arm64-v8a / armeabi-v7a / x86 / x86_64）
3. Android 签名生成
4. 依赖环境检查
0. 退出
```

## 平台支持

### macOS Emby

- 主机必须是 macOS，因为重新签名和 DMG 打包依赖 Apple 的 `codesign`、`plutil`、
  `ditto`、`hdiutil` 和 `lipo`。
- 输入支持 `.app`、`.dmg` 和包含 `.app` 的 `.zip`。
- 支持 Apple Silicon `arm64`、Intel `x86_64` 以及 Universal 应用；脚本不会修改原生
  可执行文件架构。
- 默认使用 ad-hoc 签名，适合当前 Mac 本机测试。分发安装时应使用有效的 Developer ID。

### Android Emby

- Android 流程可在 macOS、Linux、Windows Git Bash/MSYS2/Cygwin 或 WSL 中运行。
- 输入为官方原版 `.apk`；脚本读取 APK 内实际 ABI，因此同一流程适用于
  `arm64-v8a`、`armeabi-v7a`、`x86`、`x86_64` 或通用 APK。
- Windows 原生 `cmd.exe`/PowerShell 不能直接运行 Bash 脚本，请从 Git Bash 或 WSL
  启动；图形选择器不可用时会自动改为终端路径输入。
- macOS 客户端流程不能在 Windows 上签名。

当前实际客户端基线为 Android Emby `3.5.42` 与 macOS Emby `2.2.53`。脚本对注入锚点
采用失败即停止策略：如果新版客户端不再包含已验证的 `app.js` 或 `apphost.js` 结构，不会
猜测位置并产出一个未经验证的安装包。

## macOS 执行流程

选择菜单 `1` 或使用 `--mac` 后，脚本会依次：

1. 检查 Apple Command Line Tools；缺少时询问是否启动安装。
2. 选择或读取 `.app`、`.dmg`、`.zip` 路径。
3. 记录源文件关键内容和签名状态，并复制到独立任务目录。
4. 验证原应用签名和实际架构。
5. 在副本的 `www/app.js` 注册 `./modules/AvdbMagicTools.js`。
6. 在副本的 `native/ios/apphost.js` 或 `native/macos/apphost.js` 中关闭
   `restrictedplugins`。
7. 写入本目录提供且已校验的 Loader。
8. 设置独立 Bundle ID 与显示名称，避免和官方应用混淆。
9. 重新签名并执行严格签名校验。
10. 同时生成 `.zip` 和 `.dmg`。
11. 再次核对用户选择的源文件没有发生变化。

默认值：

```text
Bundle ID:    com.emby.avdb.macos
显示名称:     Emby-Avdb-Mac
签名身份:     -（ad-hoc）
```

指定 Developer ID 的示例：

```bash
bash avdb-magic-tools-injector.sh \
  --mac /path/to/Emby.app \
  --sign-identity "Developer ID Application: Your Name (TEAMID)"
```

## Android 执行流程

选择菜单 `2` 或使用 `--android` 后，脚本会依次：

1. 检查 `curl`、解压工具、Java JDK、Apktool、`zipalign` 和 `apksigner`。
2. 缺少依赖时说明来源并询问是否安装到 `~/AvdbMagicTools/tools/`。
3. 选择或读取官方 APK 路径，计算 SHA-256 后复制到任务目录。
4. 验证原始 APK 签名。
5. 使用 Apktool 解包副本，并报告 APK 中实际检测到的 ABI。
6. 修改副本中的 `assets/www/app.js` 与
   `assets/www/native/android/apphost.js`，再写入 Loader。
7. 重新构建 APK，执行 `zipalign`，选择或创建签名并使用 `apksigner` 签名。
8. 验证最终 APK 的签名、对齐、Loader 内容和两个注入点。
9. 再次核对原 APK 的 SHA-256，确认源文件未改变。

最终 APK 位于：

```text
~/AvdbMagicTools/jobs/android-时间-进程号/output/
```

自签名 APK 通常不能覆盖安装由 Emby 官方签名的版本。若签名不同，Android 会要求卸载
官方版后再安装，这可能清除该应用的本地数据。后续升级必须继续使用同一个 Keystore。

## Android 签名生成

菜单 `3` 或 `--generate-keystore` 会使用 Java `keytool` 生成 RSA 3072 位、PKCS12 格式的
本地签名，有效期为 36500 天。签名与说明文件保存到：

```text
~/AvdbMagicTools/keystore/
```

密码只在当前进程内用于签名，不写入日志或说明文件。请离线备份 Keystore、Alias 和密码；
丢失其中任意一项后，无法用相同签名升级已经安装的 APK。

## 依赖与安装边界

脚本不会静默安装依赖。检测到缺失后会显示原因并要求用户确认：

- Java：Adoptium Temurin 17 便携式 JDK，安装到工作目录。
- Apktool：从 [Apktool 官方 GitHub Releases](https://github.com/iBotPeaches/Apktool/releases)
  下载固定版本，并校验发布中内置的 SHA-256。
- Android Build Tools：从
  [Google Android Command-line Tools](https://developer.android.com/studio#command-tools)
  下载固定版本并校验 SHA-256；Google SDK License 必须由用户亲自确认。
- Apple 工具：缺少时只启动 `xcode-select --install`，安装完成后需要重新运行脚本。

Android SDK 使用受 [Google Android SDK License](https://developer.android.com/studio/terms)
约束。脚本不会替用户自动接受许可。

## 命令行参数

```text
--mac FILE             注入 macOS .app、.dmg 或 .zip
--android FILE         注入 Android .apk
--generate-keystore    生成 Android 签名
--loader FILE          指定其他 AvdbMagicTools.js
--keystore FILE        指定已有 Android Keystore
--alias NAME           指定 Android Key Alias
--bundle-id ID         指定 macOS Bundle Identifier
--display-name NAME    指定 macOS 应用名称
--sign-identity NAME   指定 macOS codesign 身份，默认 -（ad-hoc）
--check                只显示依赖状态
--self-test            运行注入、幂等性与源文件不变性自检
--help                 显示帮助
```

示例：

```bash
# 只看依赖，不安装、不修改客户端
bash avdb-magic-tools-injector.sh --check

# 运行内置安全自检
bash avdb-magic-tools-injector.sh --self-test

# 使用指定签名构建 Android APK
bash avdb-magic-tools-injector.sh \
  --android /path/to/Emby.apk \
  --keystore /path/to/avdb-magic-tools.p12 \
  --alias avdbmagictools
```

## 环境变量

| 变量 | 默认值或用途 |
| --- | --- |
| `AVDB_MAGIC_TOOLS_HOME` | 工作根目录，默认 `~/AvdbMagicTools` |
| `AVDB_LOADER_PATH` | 自定义 Loader 路径 |
| `AVDB_ANDROID_KEYSTORE` | 默认 Android Keystore 路径 |
| `AVDB_ANDROID_KEY_ALIAS` | 默认 Alias，值为 `avdbmagictools` |
| `AVDB_ANDROID_BUILD_TOOLS_VERSION` | 默认 `36.0.0` |
| `AVDB_APKTOOL_URL` | 自定义 Apktool JAR URL |
| `AVDB_APKTOOL_SHA256` | 自定义 Apktool JAR 的 SHA-256 |
| `AVDB_MAC_BUNDLE_ID` | 默认 `com.emby.avdb.macos` |
| `AVDB_MAC_DISPLAY_NAME` | 默认 `Emby-Avdb-Mac` |
| `AVDB_MAC_SIGN_IDENTITY` | 默认 `-`，即 ad-hoc |

## 工作目录

```text
~/AvdbMagicTools/
├── bootstrap/       # 远程入口下载的已校验脚本和 Loader
│   └── archive/     # 再次下载前保留的旧文件
├── downloads/       # 用户确认后下载的依赖安装包
├── jobs/            # 每次任务的输入副本、工作副本与最终输出
├── keystore/        # Android 签名及不含密码的说明
├── logs/            # 完整运行日志
├── self-test/       # 内置自检产生的隔离文件
└── tools/           # 便携式 Java、Apktool、Android SDK
```

每次任务使用独立的时间戳目录。失败时不会删除任务副本和日志，便于定位具体步骤；脚本会
输出失败原因、当前步骤和日志路径。

## Loader 与认证

 注入客户端的 `AvdbMagicTools.js` 只是稳定 Loader。业务脚本由已连接的 Emby Server 插件
通过 `Client/Config` 和 `Client/Script` 提供。Loader 使用当前 Emby 客户端已有的
`ApiClient` 与登录会话，不包含管理员密码、数据库密码、固定 Token 或服务器内部路径。
当前 Loader 会在请求完成后立即移除对应的超时句柄，避免 macOS 客户端长时间运行时累积
已经结束的请求记录。已注入的旧副本仍可兼容当前服务端协议，但需要重新执行注入才能获得
这项 Loader 本地生命周期优化。

因此，客户端必须连接到已经安装并启用 Avdb Magic Tools 的 Emby Server；只重新打包
客户端不会凭空提供服务端 API。

## 校验发布文件

在本目录执行：

```bash
shasum -a 256 -c SHA256SUMS
```

Linux 也可以使用：

```bash
sha256sum -c SHA256SUMS
```

## 常见问题

### 找不到文件选择器

SSH、无桌面 Linux 或图形选择器不可用时，这是正常行为。脚本会提示在终端粘贴绝对路径。
输入文件必须存在于实际运行脚本的那台机器上。

### 提示找不到注入锚点

说明所选 Emby 客户端的前端结构与已验证版本不同。脚本会停止，不生成伪成功产物。请保留
`~/AvdbMagicTools/logs/` 中的日志，并同时记录客户端版本与平台架构。

### macOS 应用打不开

先查看任务日志中的 `codesign --verify` 结果。默认 ad-hoc 签名只面向本机测试；若系统仍
阻止启动，请确认运行的是任务输出目录中的应用副本，而不是原应用，并检查 macOS 安全设置。

### Android 无法覆盖官方版

这是 Android 签名身份不同导致的正常限制。除非持有官方相同签名，否则只能卸载官方版后
安装自签名版。卸载前请确认是否需要保留本地应用数据。

### Windows 运行说明

推荐 WSL，其次是新版 Git Bash。Android 路径已经针对 Windows/MSYS 与 WSL 做转换和
文件选择回退，但 Windows 各发行版环境差异较大；首次使用应先运行 `--check` 和
`--self-test`，再对 APK 副本执行完整流程。macOS 重新签名仍必须回到 Mac 上完成。
