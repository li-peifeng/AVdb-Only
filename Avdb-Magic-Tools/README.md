# Avdb Magic Tools

插件版本：`2026.9.12.223`

这是一个面向 Avdb 演员管理的 Emby 插件，提供演员实体删除、按人物 ID 转移影片演员关联，
以及 Emby 客户端影片详情页 `extrafanart` 剧照、演员详情写真、首页每日推荐横幅和演员墙。

这是一个全新身份的插件：GUID 为 `28abc939-6af7-44d1-99d3-7bc5e2d52610`，程序集和 DLL
均为 `Avdb.MagicTools.Plugin`，管理与业务 API 继续使用 `/Plugins/AvdbMagicTools/...`，
同源 Web 静态资源和图片资源使用 `/magictools/static/...`、`/magictools/resource/...`。
它不接受
旧插件的 GUID、程序集、路由、设置或更新清单，不能原地覆盖升级。

## 快速安装

### 新安装

1. 下载 `Avdb.MagicTools.Plugin.dll`。
2. 把它放进 Emby 的 `plugins` 目录。
3. 重启 Emby。
4. 打开“控制台 → 插件 → Avdb Magic Tools”，按需开启影片剧照、写真、每日推荐和演员墙。

设置页将 AVDB 服务地址和 API Key 单独放在最后的“AVDB”标签；依赖 AVDB 的“图片”
以及“演员”标签会在各自底部说明所需配置。预告片隐藏选项已并入“主题 & UI”标签。
地址和 API Key 只由 Emby 服务器使用，不会写入客户端脚本或图片地址。

### R18 图片补全计划任务

插件向 Emby 注册两个独立的手动计划任务：“R18 海报和封面补全”和“JavDB 剧照补全”。
前者只处理 Poster/Primary 和 Thumb，后者只处理附加 Backdrop。两项任务默认不添加自动触发器，
管理员可以在“计划任务”中直接点击“运行”，任务使用图片设置页的媒体库范围；留空表示全部媒体库。
任务按媒体库根节点逐库、每页 256 项扫描，先跳过没有可识别番号的项目，不会一次性载入全库。
设置页中的 `OverwriteExistingPoster` 和 `OverwriteExistingThumb` 分别控制海报和封面是否覆盖已有图片；
关闭对应开关时只补缺，不替换已有图片。剧照任务默认只补全没有任何附加 `fanartX`（例如 `fanart1.jpg`）的影片；
`fanart.jpg`、`fanart0.jpg` 和 `Backdrop/0` 主背景不计入。勾选 `OverwriteExistingBackdrop` 后，手动运行“JavDB 剧照补全”
才会下载并替换已有附加剧照。某个媒体库读取失败时会记录库 ID 并继续处理其他媒体库，完成日志会给出扫描、识别番号、
写入和失败统计。剧照按实际 Backdrop 索引读取，即使主背景缺失或索引中间有空洞，也不会隐藏后续已登记的剧照。

图片设置页中的 `启用影片剧照` 只控制详情页显示已经登记的剧照，不会触发补全或覆盖；
`启用剧照补全` 独立控制按需补全和“JavDB 剧照补全”计划任务。按需补全只在本地没有附加 `fanartX` / Backdrop 剧照时执行，
不使用剧照成功或失败冷却期；覆盖开关只对手动运行“JavDB 剧照补全”生效。
打开“添加新媒体时自动下载剧照”后，Emby 每次新增视频条目时会在图片设置页所选媒体库内按番号检索 JavDB 并补充缺失剧照；该开关独立于详情页按需补全和计划任务，始终保留已有附加剧照，不受覆盖开关影响。

番号回退解析与 AVDB 保持一致，支持欧美点号日期格式，例如 `Blacked.16.07.09`；两位年份会按
`20xx` 规范化后用于 JavDB 查询。

### JavDB 评分同步

启用“JavDB 评分同步”后，打开影片详情页会优先从影片同名 NFO 的 `<num>` 读取严格番号，
没有有效 NFO 番号时才回退到 Emby 项目的 `ProviderIds.Num`；剧照显示和补全也使用同一套番号解析。
插件通过 Avdb 后端按番号精确匹配 JavDB 影片，并将 JavDB 的 5 分制 `movie.score` 乘以 2
写入 Emby 的 `CommunityRating`，不会写入 `UserRating`；评分通过 Emby 的 `MetadataEdit` 项目更新路径保存，
保存成功后详情页只局部更新评分，不会重新加载海报、背景、章节和剧照。
接口响应和日志会返回实际番号以及非敏感的处理原因，例如 `provider_number_missing`、
`score_missing`、`javdb_authentication_error`，方便判断为什么没有更新。

即时请求和批量任务共用 Avdb 的 `javdb_rating_cache` 持久化缓存，缓存键是规范化番号，记录
原始 JavDB 分数、结果原因和 `cached_at` 时间戳；缓存有效期为 10 天，命中时不会访问 JavDB。
查询到有效分数时，如果媒体旁已有 NFO，插件会维护标准的
`<ratings><rating name="javdb" max="5" default="false">` 节点；NFO 只作为可移植的评分备份，
缓存的新鲜度仍以 Avdb 的 `cached_at` 为准，不使用 Emby 的 `CommunityRating` 作为缓存判断。
缓存不存在或已过期时才查询 JavDB，查询完成后立即写入缓存。

插件同时注册“JavDB 评分同步”计划任务，支持 Emby 的“立即运行”和默认每周日 03:30 执行。
“允许 JavDB 评分覆盖已有社区评分”关闭时只填充空值或 0；无有效 NFO/ProviderIds 番号、无精确匹配、
无评分、JavDB 账号失效、Avdb/JavDB 请求失败或保存失败时，都保留 Emby 原有评分，不写入空值或 0。
“保护 JavDB 社区评分”开启后，其他元数据源更新影片后会再次按番号同步有效 JavDB 评分。

常见目录：

- Docker：宿主机映射到 `/config` 的目录下，例如
  `/srv/emby/config/plugins/Avdb.MagicTools.Plugin.dll`。
- Windows：`%ProgramData%\Emby-Server\programdata\plugins\Avdb.MagicTools.Plugin.dll`。
- Linux 原生安装：以 Emby 控制台“日志”页显示的程序数据目录为准，在其中找到 `plugins`。

只复制这一个 DLL，不要复制构建目录中的 `MediaBrowser.*.dll` 或 `Emby.*.dll`。

### 已安装 Avdb Actor Tools

旧插件不能自动升级到本插件，请按顺序操作：

1. 在旧插件设置中关闭四个 Web 功能并保存。
2. 停止 Emby。
3. 从 `plugins` 目录移走 `Avdb.ActorTools.Plugin.dll`。
4. 放入 `Avdb.MagicTools.Plugin.dll`，再启动 Emby。
5. 进入新插件设置页重新配置；旧设置不会继承。

不要同时保留两个 DLL。Docker 用户若无法先正常关闭旧 Web 功能，在移走旧 DLL 后执行一次
`docker compose up -d --force-recreate emby`，让新容器恢复原始 Web 入口，再加载新插件。

### Docker 只需判断一件事

如果 `EmbyServer` 进程以 root 运行，并且容器没有设置 `read_only: true`，直接放入 DLL 即可，
不需要初始化脚本。否则再增加这一条挂载：

```yaml
volumes:
  - ./ui/avdb:/etc/cont-init.d/avdb:ro
```

把仓库里的 `Avdb-Magic-Tools/avdb` 复制为 `./ui/avdb` 并执行
`chmod 755 ./ui/avdb`。新增挂载后运行：

```bash
docker compose config --quiet
docker compose up -d --force-recreate emby
```

不知道 Emby 是否以 root 运行时，用下面的命令确认 `EmbyServer` 那一行：

```bash
docker top emby -eo pid,user,group,comm
```

容器名不是 `emby` 时替换成实际名称。更完整的权限判断和排错见后文“官方 Docker 镜像”。

删除接口：

```text
POST /Plugins/AvdbMagicTools/Items/{id}/DeletePerson
```

按人物 ID 转移单部影片的演员关联：

```text
POST /Plugins/AvdbMagicTools/Items/{itemId}/TransferPerson
```

列出选定媒体库中的附属影片条目 ID：

```text
POST /Plugins/AvdbMagicTools/Items/AdditionalParts/Ids
```

请求体使用 `LibraryIds` 指定媒体库，可选 `PersonIds` 按 Emby 的数字人物
`InternalId` 筛选。该接口通过 Emby 内部 `ExtraType.AdditionalPart` 查询，返回的
每个 ID 都是独立的影片条目；Avdb 会继续读取这些条目自身的 `People`，因此映射改名、
完全同名演员合并和删除前残留清理不会只更新主条目而遗漏附属影片。

影片剧照接口：

```text
GET /Plugins/AvdbMagicTools/Items/{itemId}/ExtraFanart
```

该接口返回已经被 Emby 登记为 Backdrop 的附加图片索引和缓存标签：支持当前影片
`extrafanart` 目录内的图片、与影片文件同目录的 `fanart1.jpg`、`fanart2.jpg`，也支持
由 Emby 固化到元数据目录的附加 Backdrop；索引为 0 的主背景图不会重复放进剧照墙。
接口不返回或暴露媒体文件系统路径、AVDB 地址或 API Key。

当已配置 `AvdbApiBaseUrl` 与 `AvdbApiKey` 且已启用剧照补全时，该接口会按 Emby `ProviderIds.Num` 中已经标准化的番号原值
完整查询 JavDB `preview_images`；详情页自动补全只在影片尚不存在附加 `fanartX` / Backdrop 剧照时启动，
手动任务勾选覆盖后才允许覆盖已有剧照；
若 `ProviderIds.Num` 为空，则从影片现有标题、原始标题、排序标题、文件名或父目录名中
提取番号原值。提取结果原样传给 AVDB，不会再次大写、补零、增删分隔符或做其他标准化。查询只读取
JavDB 剧照候选，不使用 JavDB 封面冒充剧照，也不直接访问 R18.DEV 网站。
插件最多并发下载 8 张 AVDB 代理图片；插件保存前检查图片至少 30KB。合格图片逐张保存为 `Backdrop`；插件固定将新
JavDB 剧照写入每部影片目录下的 `extrafanart/fanartN`，并将实际路径登记为
Emby 的附加 `Backdrop`；不再提供保存位置输入或切换开关。该保存方式不依赖 Emby 的图片保存约定，但要求 Emby
进程对影片目录具有写权限；已有剧照不会自动迁移，也不影响 R18 海报和封面。
每张保存后立即写入 Emby 图片仓库，后续图片沿用同一个影片实体继续追加；客户端轮询时可以
逐步看到已完成的剧照，不会因重新读取未写库的旧实体而反复覆盖同一个文件名。
没有附加剧照时，插件会在第一张合格 JavDB 剧照准备保存前开始写入，并从索引 1 开始登记；勾选覆盖并手动运行任务时，会先删除旧的附加
`Backdrop` / `fanartX`，再写入本次完整检索得到的剧照，不会触碰索引为 0 的主背景。检索结果为空、服务端不可用、认证失败或返回不完整结果时，均保留原有内容，
不会因为空结果清理旧的附加剧照。客户端在补全进行中会把新登记的剧照追加到已有横向列表，不重建滚动容器，因此不会在每张图片保存后把浏览位置拉回左侧。
剧照全量候选受 Emby 可登记的附加 Backdrop 槽位上限保护，当前最多写入 511 张；这不是原先的 3 张阈值。

## Emby Web 扩展与统一注入

插件启动时会在服务器自带的 `dashboard-ui/index.html` 中注入一段内嵌 Web Bootstrap，
并把未修改的入口文件备份到插件数据目录。Bootstrap 只负责读取已认证的
`Client/Config`、加载 `Client/Script`、处理版本兼容和服务器切换；四项业务代码由同一份
Shared Client Core 在运行时提供。注入带有唯一的起止标记，重复启动不会重复写入；插件升级
时只替换标记内的 Bootstrap。若 Emby 升级替换了整个 Web 入口，插件会在下次启动时先备份
新的原始入口，再重新注入。

在 iOS Safari 26.2 及后续版本检测到浏览器原生 Navigation API 时，Bootstrap 会在 Emby
延迟加载主程序前让当前页面回退到 Emby 自带的 History API 兼容层。该兼容只作用于服务器
直连的 Emby Web，不阻止边缘返回、不增加导航延时，也不影响 Android、macOS Safari、
WKWebView 或 `app.emby.media`。它用于规避 iOS 交互式返回与 Emby 的手动滚动拦截组合导致的
旧页面快照滞留、短暂无响应、模糊瓦片和位置恢复异常。

影片剧照、演员写真、每日推荐和演员墙共用同一个 `Avdb Magic Tools web customizations`
注入块，不会分别修改 `index.html`；只有四个 Web 功能全部关闭时才移除整个注入块。

四项功能共用一个页面生命周期观察器和一组路由事件，不再各自观察整个 `body`。Shared Client
Core 也不再长期保存每一轮推荐创建过的 DOM 和事件监听器；旧轮播帧从页面移除后即可由
浏览器或 macOS WebKit 回收，切换服务器或销毁 Loader 时只清理仍在当前文档中的插件节点。
Core 还直接接入 Emby 的 `viewbeforehide`、`viewbeforeshow`、`viewhide`、`viewshow` 与页面
可见性事件：历史手势开始切页时会同步停止首页轮播、作废详情页未完成的写真/剧照响应并释放
已解码图片，避免隐藏 View 继续创建大图合成层。这套路径同时用于 Safari、Android WebView
和 macOS WKWebView，不依赖 Android 原生返回键。各功能的延迟同步也先检查当前真实路由，
演员墙和推荐图不会再因为列表页、设置页等无关 DOM 变化反复启动定时检查。

### 影片剧照

影片详情页存在附加 Backdrop 时，会在“演职人员”下方、紧靠“章节”区域之前显示“剧照”：
横版缩略图复用 Emby 章节卡片的块级结构和间距，并同步当前页面章节卡片的实际计算宽度与
圆角；窗口尺寸变化后会重新同步。剧照横条使用正确的 customized built-in 方式创建
Emby `emby-scroller`，并强制使用原生水平滚动；即使旧版 Android WebView 没有及时升级
自定义元素，也有独立的 `overflow-x` 与惯性滚动兜底。普通上下滚动继续交给详情页。点击后使用 Emby Web 原生全屏
画廊左右浏览。没有合格
图片时不显示整个区域。若服务端正在后台导入或重建剧照，客户端会在导入期间短间隔刷新索引；
它不会等待所有候选下载完成才阻塞详情页，已经由 Emby 固化的附加 Backdrop 可以先显示。后台轮询返回新剧照时只追加新卡片，
复用当前滚动容器并保留横向位置，滑到后面的剧照不会因索引刷新跳回第一张。

部分影片没有章节，或 Emby Web 在该详情页隐藏了章节区块。此时插件使用与横版卡片一致的
响应式默认宽度、16:9 高度和圆角，避免尺寸变量缺失导致剧照卡片计算为 `0 × 0`、页面只
剩“剧照”标题；页面存在章节卡片时仍以章节的实际尺寸为准。

在 Emby 控制台打开“插件 → Avdb Magic Tools → 设置”，可以通过“图片”“演员”“主题 & UI”“STRM”“AVDB”标签切换分类；
标签栏采用 Emby“首页/收藏”同款的胶囊式横向滚动样式并水平居中；背景阴影按标签内容宽度自适应，窄屏滚动时会尽量把选中标签保持在中间；选中项使用更明显的高亮和阴影，宽屏会适当增加标签点击宽度。预告片隐藏选项已并入“主题 & UI”，可在同一标签中配置。
页面也支持选择操作及显示媒体库、自定义“剧照”标题，
并单独决定是否对非管理员开放。底层配置项
`EnableExtraFanartGallery` 默认为 `true`，只控制影片详情页显示已经登记的剧照；
`EnableExtraFanartCompletion` 默认为 `true`，控制按需补全和“JavDB 剧照补全”计划任务；
按需补全只在影片没有附加 `fanartX` / Backdrop 剧照时执行；勾选“覆盖原有剧照”后，手动运行“JavDB 剧照补全”才会重新下载并替换已有剧照，
不依赖剧照成功或失败冷却期。
保存后会立即注入或移除标记范围内的脚本，不需要重启 Emby，已经打开的浏览器页面刷新
一次后生效。卸载插件时也会自动移除标记范围内的脚本，同时保留其他 Web 文件改动。

### 演员头像来源

插件向 Emby 注册一个原生远程图片提供者 `Gfriends.Avdb`，只支持 `Person` 的主图。管理员在 Emby
演员详情中打开“编辑图像 → 搜索”时，Emby 自带的 `TheMovieDb` 来源保持不变并继续由 Emby
检索；选择 `Gfriends.Avdb` 来源时，插件按演员当前名称调用 AVDB 的 Gfriends 数据库索引，AVDB 负责
数据库别名匹配并返回 CDN 优先的原图地址和索引中的宽高。插件不会通过 AVDB 重复请求 TMDB，也不会自动覆盖现有演员头像。

头像提供者由独立的 `EnableAvdbPersonImageProvider` 开关控制，默认关闭，不受写真显示开关
影响。启用时与写真和影片剧照补全共用 `AvdbApiBaseUrl`，并额外要求管理员填写 `AvdbApiKey`。API Key 只由
Emby 服务器以 `X-API-Key` 请求头发送给 AVDB，不进入 `Client/Config`、客户端功能脚本或图片
地址。AVDB 返回的图片必须是 Gfriends 仓库的受信任 GitHub CDN 或 Raw 原图地址；AVDB 图片代理、跨域地址、Jalbum
写真地址和其他路径都会被插件拒绝。插件优先直接获取 AVDB 索引返回的 CDN；AVDB 没有可用 CDN 候选时才返回 Raw；下载和保存仍由 Emby 原生
远程图片流程完成。

AVDB 搜索接口只返回数据库中已经记录的 Gfriends 原图宽高，插件直接填写 Emby 原生
`RemoteImageInfo` 字段；不会在搜索请求内等待探测，也不会主动请求未选中的图片。尺寸字段不会
进入客户端功能脚本，也不会把 API Key 写入图片地址；头像原图请求不经过 AVDB 图片代理。

如果不使用 AVDB 头像来源，可以关闭独立开关并安装
[龙王的头像来源插件](https://github.com/jzdxjk/Jav-Actors-Mapping/releases)。该外部插件与
Magic Tools 的 AVDB 头像提供者互不冲突，只是同时开启会有重复头像产生，龙王的头像来源插件功能更加丰富，AVDB 头像来源的优点只是复用了数据库，不需要文件树。

### 演员写真

演员详情页先按当前 Emby Person ID 读取真实演员条目，再把完整名称交给 AVDB 已有的
Jalbum 数据库索引做精确名称或数据库别名匹配。客户端不下载 `Filetree.json`、不递归构建
`buildFolderIndex()`，也不加载演员映射文件，因此不会在 macOS WebKit 主线程展开整棵写真树；
写真 URL 只保留在当前演员详情状态中，不再跨页面永久缓存超大演员图集。
AVDB 的定时任务独立负责索引刷新；写真请求本身只读数据库，不触发远端版本检查或索引重建。

写真位于演员简介下方、影片列表上方。桌面端默认每页 33 张（11 列、3 行），移动端默认
每页 9 张（3 列、3 行），支持上一页/下一页；所有设备都可直接在写真网格上左右滑动或拖动
翻页，鼠标、触摸和触控笔均可使用，普通纵向页面滚动不受影响。点击任意写真后使用 Emby 原生全屏画廊浏览
完整写真集。写真索引只通过已认证的
`GET /Plugins/AvdbMagicTools/Client/ActorStills?Name=...` 由 Emby 服务器桥接到 AVDB
现有的 Jalbum 数据库索引。插件设置中的 `AvdbApiBaseUrl` 必须由管理员明确填写，
例如 `http://10.0.0.3:8000`；留空、超时或没有匹配时均不显示写真，客户端和服务端都不会
回退到本地文件树或未受信任的其他镜像。AVDB Token 和服务地址不会进入客户端脚本。
写真查询只在 Emby 服务器端读取 AVDB 的 Jalbum 索引。返回给浏览器的 `Original` 和
`Thumbnail` 是 Emby-relative 的 `/magictools/resource/actor-still` 资源路径；浏览器只向
Emby 当前 Origin 发起图片请求，插件服务器再校验受信任的 Jalbum GitHub CDN/Raw 地址并转发
图片。没有 CDN 候选时由服务器使用 GitHub Raw，外部地址不会直接作为浏览器的图片源。
AVDB 地址可以继续使用内网 IP、HTTPS 域名或嵌入式客户端访问，因为它只承担已认证的索引查询
和服务器端图片桥接。
与影片 `extrafanart` 的本地 Backdrop 接口、DOM 类名和画廊实例相互独立。

AVDB 索引只返回写真原图地址，写真网格和 Emby 原生全屏画廊共用同一份原图地址，
不再通过 `/img-proxy` 现场裁切或编码 WebP。写真卡片接近可视区域时才进入加载队列；桌面端
先按设备能力同时处理 12–16 张，移动端先处理 4–6 张，并在一张完成解码后继续补入下一张。
若连续图片的传输、解码和主线程队列延迟都很低，会逐档提高到当前设置允许的有效上限；出现明显
解码或队列压力时则退回上一档，桌面端最低 6–8 张，移动端最低 3–4 张。
插件设置中的“写真最大并发数”默认为 `0`（自动）：最大并发取当前页实际展示数且不超过 50，
例如每页 16 张时有效上限就是 16，每页 33 张时有效上限为 33；填写 `1–50` 可改为自定义上限。
实际并发仍不会超过当前页图片数，插件也不会为凑并发预取并解码不可见的下一页。该设置只是允许
的最大值，现有的传输、解码与主线程压力检测仍可自动降档。这样性能充足的设备仍能尽量提高当前页
加载速度，同时避免弱设备把下载、解码和垃圾回收集中在同一时刻。
旧版 `ActorStillsImage` 路由仍保留用于兼容已部署的旧客户端；当前客户端使用
`GET /magictools/resource/actor-still?Path=...`。新旧路由都只接受插件生成的受信任 AVDB
图片代理路径，拒绝任意外部地址和非图片上游，不会把插件变成开放转发器，也不访问写真文件树。

确认当前条目是 Emby Person 后，插件会在写真数据准备完成后把写真区插入演员简介下方、影片列表上方；
加载期间不插入前置占位块，不会把“正在加载中…”显示在演员详情内容之前。有写真时显示图片网格；
没有写真或请求失败时会移除整个区块，不留下空白区域。

插件设置页可配置 `EnableActorStillsGallery`、`EnableAvdbPersonImageProvider`、`AvdbApiBaseUrl`、
`AvdbApiKey`、区块标题、桌面端行数与
列数、移动端行数与列数、写真最大并发数，以及是否跳过数据库索引中的第一张封面图。每页数量由
对应的行数 × 列数自动计算，不再单独提供总数设置。写真也可单独设置是否对非管理员可见及其
允许媒体库；写真功能默认开启，非管理员开关默认关闭。保存后刷新已打开的 Emby Web 页面即可生效。

### 首页每日推荐与演员墙

插件设置页可分别开启“每日推荐横幅”和“演员墙”。这两项默认关闭，避免普通的演员工具
升级在未经选择时改变首页；启用后的主要行为如下：

- 每日推荐从指定媒体库随机读取电影和剧集，只显示带横版 Backdrop、并满足最小宽度的
  项目；支持自动切换、左右触控手势、预览卡片、详情跳转和手动刷新。图片只需宽度大于
  高度，不使用原文件中未接入实际轮播路径的 `1.5` 宽高比限制。
- 每日推荐可在设置页切换“每日推荐”与“沉浸式”。后者参考
  `homeswip.js` 的全幅背景、底部文字逐层进入、右下角 Logo 和右侧纵向页码，但继续复用
  插件现有的数据源、缓存和页面生命周期；两种样式互斥，只会挂载一个轮播区块。
- 普通“每日推荐”右下角的 3 个影片快捷预览可在设置页单独关闭；该开关不参与沉浸式
  渲染，沉浸式的布局、Logo 和右侧纵向页码保持不变。
- 页面宽度达到 `112.5em`（默认字号下约 1800 CSS 像素）时，每日推荐会同时保留前一部、
  当前和后一部三张主图。当前主图使用独立的近景轮廓与双层投影；左右主图缩小到 88%、整体
  下沉到后景并降低到 44% 亮度，交叠边缘向中间渐暗，舞台底部另有柔和环境光，因此不是三张
  同平面图片直接相盖。左右后景的露出和重合根据中间主图实际宽度自适应；超宽屏轮播根区块
  仍与非超宽屏一样贴齐窗口左右边缘，不额外保留横向内边距。
- 超宽屏“沉浸式”先读取 Backdrop 原始宽高比，以舞台 70% 宽度为上限完整显示图片，并在舞台
  内垂直居中。舞台高度按当前 Backdrop 的真实宽高比动态收拢，只在图片上下各保留约
  `12–32px` 的自适应缓冲，不再因整页宽度留下大块下方空白。舞台、主框、图片容器和下方
  留白全部使用透明背景，不再出现黑色底板；图片下缘只对原图本身使用透明遮罩渐隐，不再生成或叠加倒影。
  纵向页码独立挂在舞台最右侧，不覆盖中间主图。
- 超宽屏普通“每日推荐”不套用沉浸式的完整原图限制：中间主图保持舞台 70% 宽度，Backdrop
  以 16:9 画面轻微放大后裁剪，轮播高度随视口宽度按中间主图的 16:9 比例同步增长，并以
  `92vh` 为极端超宽屏上限，避免屏幕越宽画面越扁。缩放锚点和裁剪基准固定在右上角；
  主图底缘不再生成或叠加倒影，也不增加黑色底板。
  超宽屏下方的页面指示条独立挂在轮播舞台层，始终水平居中，不会随三张海报平移或换层。
  左右两层只显示 Backdrop 图片，不显示标题、简介、按钮、页码或快捷预览。低于该断点时
  继续使用原有单张主图布局，不改变平板、普通桌面和移动端显示。
- 演员墙直接请求 Emby 自身的 `Persons` 接口，不再随机读取影片后展开每部影片的 `People`，
  也完全不接触写真、演员文件树或写真文件树。只保留有 `Primary` 头像标签且头像 URL 能成功加载的演员，
  没有头像或头像已失效的演员不会留下空白占位卡片；结果按 Emby Person ID 去重并分页显示圆形头像；每日推荐
  开启时紧跟在横幅下方，关闭时可独立显示在首页内容最前面。演员头像点击不设置人为导航锁或
  点击冷却时间，导航去重由 Emby 自身负责；所有设备均可在演员网格上用鼠标、触摸或触控笔
  左右滑动或拖动翻页。
- 每日推荐和演员墙的媒体库由设置页读取 Emby 当前用户可访问的媒体库并提供勾选菜单；
  另外可配置推荐数量、自动切换秒数、最小背景图宽度、加载占位画面、包含/排除模式、
  每库读取演员数和每页行数。
- 四项界面功能都可以独立开启“对非管理员可见”，并分别选择非管理员媒体库。运行时严格取
  配置媒体库与当前用户 Emby 可访问媒体库的交集：无交集或未选择时不显示该功能，管理员仍按
  原有功能开关和管理员媒体库设置工作。影片剧照还会校验当前影片所属媒体库；演员写真因 Person
  本身不属于单一媒体库，在当前用户至少拥有一个交集媒体库时显示。
- 影片剧照、演员写真和演员墙标题均可在设置页自定义；演员墙标题同时使用 Emby 原生标题
  容器、标题和页面左右缩进类，并保留原生标题外边距，和首页自带模块对齐。
- 推荐和演员墙只使用当前 Shared Client Runtime 的内存缓存，不写 `localStorage`；切换服务器
  或销毁 Loader 会清空缓存，也不会清理 Emby 或其他扩展的数据。
- 横幅只识别明显的水平手势，不调用 `preventDefault()`；普通竖向触控和鼠标滚动继续交给
  Emby 首页。实现不依赖外部 CDN，也不再携带原文件中未调用的旧轮播代码和整套 Swiper。
- HomeSwiper 样式没有复制原脚本内嵌的 Swiper 11，也不会修改全局 `.swiper`、Emby Header、
  页面滚动条或 `CACHE|*` 键，因此不会与现有每日推荐、影片剧照及其他 Web 扩展争用样式和事件。
- 普通“每日推荐”样式在移动端把横向分页指示条固定在底部居中；“沉浸式”在桌面和
  移动端都保留舞台右侧的纵向页码，超宽屏页码位于整个舞台最右侧，不压在中间主图上，
  也不为底部横向页码预留大块空间。详情按钮下方仅
  保留紧凑的安全间距，右下角 Logo 与内容区使用相同的底部基线。
- 设置页使用两行预设色块分别选择普通页码和当前页码颜色；所选颜色由插件配置持久化，
  同时应用于普通“每日推荐”和“沉浸式”，不会改变两种主题各自的页码方向、位置和尺寸。
- 普通宽度下首页推荐图片继续使用约 0.55 秒的整帧渐隐渐出；iPad（包括 iPadOS 桌面版 UA）
  的普通“今日推荐”改用与“沉浸式”相同的同步整帧交叉淡入淡出，普通桌面保持原有顺序淡出；
  超宽屏点击前后按钮时，三张主图按前后顺序在约 0.55 秒内同步滑入、滑出和换层。进入中间位置的新主图会保持内容透明后再
  显示；超宽屏仅显示 Logo 或标题及无文字图标按钮，评分信息、简介和详情文字不显示。
- 设置页标签按“图片 → 演员 → 主题 & UI → STRM → AVDB”排列，标签栏使用 Emby“首页/收藏”同款胶囊式横向滚动样式并水平居中；背景和阴影跟随实际标签内容宽度，窄屏切换时尽量居中已选标签，宽屏适当放大标签点击区域；“演员”标签合并演员写真/头像与演员墙两个设置区，栏目之间保留垂直间距和分隔线。
- 非超宽屏推荐切换只使用整帧透明度过场；超宽屏只对三张独立主图做平移、缩放、垂直错层、
  交叠暗角和投影换层，不缩放整个首页区块。页码短横条普通页使用半透明雾灰色，当前页使用
  柔和玫红色并加长，在深色背景上保持清晰但不抢画面。
- 首页离开前只记录实际纵向滚动容器的位置；历史返回时等推荐图、演员墙及其卡片恢复原高度后
  只写回一次，不再用多组并发定时器反复强制滚动。用户开始触摸或滚轮操作后会立即放弃待恢复
  快照，避免与 Safari/WebView 的边缘返回动画和后续点击争抢主线程。
- 文字标题最多显示两行，超出部分在末尾使用省略号截断；标题不再叠加与实际行高冲突的
  固定高度上限，沉浸式标题也使用更宽松的行高，避免第二行文字底部被裁切。
- 宽屏 Backdrop 限制为 1920px，并放在右侧约四分之三画面；沉浸式超宽屏沿用普通非超宽主题的
  主图处理，不额外叠加大面积底部 `mask-image`、模糊或透明渐隐层，只保留紧凑的自适应舞台间距，
  避免底部透明区域侵入主图。
- 推荐图存在时会关闭透明 Header 原有的 `backdrop-filter` 模糊层，离开首页时同步恢复原生样式，
  避免 Safari/WebView 上划期间把 Header 的离屏模糊瓦片绘制成遮挡内容的矩形块。
- 今日推荐在超宽屏普通和沉浸式主题均移除主图阴影遮罩；普通主题同时移除黑色兜底边框，两套主题统一使用黑色文字
  描边并加深文字阴影，其他桌面和移动端内容保持原样。
- 普通宽度下的今日推荐切换改为先将当前主图完整渐隐，再让下一张主图渐现，文字在图片到位后进入，避免整张新图突然闪现。
- 普通宽度下旧主图渐隐期间保留原有遮罩，避免遮罩先消失导致图片在淡出时突然变亮或像从遮罩下钻出。
- 所有轮播模式的文字均在新图开始进入后延迟约 `0.2s` 进入，不再等待图片加载完成；普通宽度的旧图淡出阶段单独扣除过渡等待时间，保持文字与图片的相对时序一致。
- 首页页码指示条基础长度略微增加；项目超过 10 个时按项目数量自动缩短，普通和沉浸式方向保持同一套自适应比例。
- 演员墙和写真区域的上一页/下一页按钮扩大点击区域并同步放大箭头。
- 每日推荐右下角的三张影片预览卡片增加自适应圆角，并由卡片容器统一裁切图片和文字区域。
- 每日推荐预览卡片标题居中，并按当前轮播帧的大尺寸主图平均色调自动切换文字颜色、文字背景和阴影；旧 WebView 或取样失败时使用可读性兜底样式。
- 超宽屏沉浸式主图使用 `cover` 轻微放大填满圆角框，并以右上角为放大原点，避免两侧留空破坏圆角。
- 超宽屏左右侧卡片仍保持暗色层次，但将靠近中间主图的渐隐收窄并降低黑色不透明度，避免重合边缘形成黑条。
- 仅超宽屏普通“今日推荐”主题的主标题字号缩小一档。
- 超宽屏“今日推荐”和“沉浸式”的标题内容区在主图内使用全宽布局，标题不再受左侧窄栏限制。
- 超宽屏普通“今日推荐”和“沉浸式”均只保留当前影片的标题（普通主题使用 Logo 时保留其标题 Logo）；
  评分、年份、题材、标语、简介、辅助 Logo 和详情文字均隐藏，上一部、下一部和刷新仍保留为无文字图标按钮。
- 演员墙根据实际可用宽度按多档列数自动递增，最少保持 5 列；窗口或设备方向变化时会自动重排并重新分页。
- 首页统一由 sections 父容器使用 `2em` 的 `row-gap` 管理推荐图、演员墙和 Emby 原生栏目的
  外部垂直间距，并清零各 section 自带的底部 margin，避免不同 Emby/WebView 版本出现双倍空隙。
  演员墙标题到第一排头像保留响应式内间距，避免标题贴住头像。
- 在宽度不超过 `50em` 的小屏页面保留评分和年份，只隐藏题材与分级 tags，并把文字标题
  缩小到原 tags 的 `1rem` 字号；两套轮播样式的小屏展示图统一使用竖版 Poster 并从顶部
  居中裁切，没有 Poster 时自动回退到横版 Backdrop，并从右上角开始裁切。桌面端继续使用
  横版 Backdrop，横竖屏切换时由浏览器自动重新选择图片源，不需要重新生成轮播。

首页功能只在 Home View 内查找和插入节点；影片剧照只在影片详情的 `.itemView` 内工作。
两者的节点类名、缓存键和事件范围相互独立，因此不会改变影片剧照的章节式水平滚动或
原生画廊点击行为。

使用 Emby 的 Home 按钮从详情页返回首页时，插件会跟随首页视图属性和 Chromium 路由变化重新挂载
每日推荐轮播图与演员墙；不会误选 Emby 保留在 DOM 中的隐藏旧首页视图。

Emby 4.10 的首页 View 在 `viewbeforeshow` 阶段不保证已经带有可识别的控制器名称或 CSS
类。插件会在收到 `type=home` 时补充 `data-type="home"`，并把横幅作为首页 sections
容器的前置兄弟节点插入，与原脚本的实际挂载位置一致；共享 MutationObserver 会在首页异步
生成或重绘 sections 后通知各功能重新检查挂载。

首页的滚动容器是固定高度的纵向 flex 布局。轮播根节点使用 `verticalSection` 并
明确设置 `flex-shrink: 0`、固定 flex-basis 和最小高度，避免横幅虽然已加载完整内容和
Backdrop、却被其他首页 section 挤压成 `0px` 高度。
首页非横向布局只取消整个 sections 滚动内容最外层的 Header 顶部留白，让全幅推荐图贴顶；
不会改写任意两个栏目之间的原生间距，也不会取消沉浸式右侧纵向页码。

服务器提供的 `/web/` 页面由插件自动注入。使用独立内置前端的 Emby macOS、Android 等
客户端不会读取服务器的 `dashboard-ui/index.html`；这些客户端只有在对应版本已通过
`Client-Injector` 安装 Loader 后，才会从当前服务器加载同一份 Shared Client Script。
本版本同时更新了 Loader 的超时句柄清理；已经注入的旧 Loader 与服务端仍兼容，但要获得
这项客户端本地优化，需要使用发布目录中的新 `AvdbMagicTools.js` 重新生成应用副本。
未注入的官方客户端仍不在四项界面功能的支持范围内。若 Emby 程序目录为只读，插件会记录
警告并跳过服务器 Web 注入，演员管理接口仍可正常使用。

### 官方 Docker 镜像

官方镜像通过 `UID` / `GID` 环境变量决定 `EmbyServer` 进程的身份；镜像内的
`/system/dashboard-ui` 则默认属于 `root:root`。是否需要初始化脚本取决于
`EmbyServer` 进程能否写入 `/system/dashboard-ui/index.html`，而不是这些文件最初由谁创建：

- `EmbyServer` 确实以 `root`（UID 0）运行，且容器根文件系统可写：不需要初始化脚本。
- 容器的 s6/PID 1 是 root，但 `EmbyServer` 按 `UID` / `GID` 以普通用户运行：需要脚本。
- 当前文件曾被手动改成可写，但 `EmbyServer` 不是 root：仍建议保留脚本；更新镜像后，新
  `index.html` 会再次变成 `root:root`。
- Compose 使用了 `read_only: true`：root 也不能修改镜像层中的入口文件。需要取消只读根
  文件系统，或自行维护完整且可写的 `dashboard-ui`；本脚本不能绕过只读挂载。

官方镜像推荐使用普通 UID/GID 运行 Emby。初始化脚本只调整 `dashboard-ui` 目录和
`index.html`，比让整个 Emby 服务长期以 root 运行的权限范围更小。

#### 1. 确认 Emby 的实际运行用户

以下命令中的 `embyserver` 是容器名；若实际名称不同请替换：

```bash
docker top embyserver -eo pid,user,group,comm
docker inspect embyserver --format '{{.HostConfig.ReadonlyRootfs}}'
```

查看 `EmbyServer` 所在行，而不是 s6、init 或 PID 1：

- 用户是 `root`，并且第二条命令返回 `false`：可以使用下文的 root 方案，不挂载脚本。
- 用户是数字 UID 或普通用户名：使用非 root 方案并挂载脚本。
- 第二条命令返回 `true`：先解决 `/system/dashboard-ui` 的只读问题。

也可以使用实际 UID/GID 直接测试写权限。例如 Emby 配置为 `1000:100` 时：

```bash
docker exec --user 1000:100 embyserver \
  sh -c 'test -w /system/dashboard-ui/index.html'
```

返回码为 0 才代表该用户当前可写；但非 root 实例仍建议挂载脚本，以覆盖以后重新创建
容器或更新镜像的情况。

#### 2. 在新 Docker 主机上准备文件

以下示例假设 Compose 项目目录为 `/srv/emby`，并把 Emby 的 `/config` 映射到
`/srv/emby/config`。已有实例应使用自己现有的 `/config` 宿主机目录，不要新建另一个空
配置目录：

```bash
cd /srv/emby
mkdir -p config/plugins ui
cp /path/to/Avdb.MagicTools.Plugin.dll \
  ./config/plugins/Avdb.MagicTools.Plugin.dll
chmod 644 ./config/plugins/Avdb.MagicTools.Plugin.dll
```

非 root 方案还需要复制仓库中的启动脚本：

```bash
cp /path/to/Avdb-Magic-Tools/avdb ./ui/avdb
chmod 755 ./ui/avdb
```

目录结构应类似：

```text
/srv/emby/
├── docker-compose.yaml
├── config/
│   └── plugins/
│       └── Avdb.MagicTools.Plugin.dll
└── ui/
    └── avdb
```

只复制 `Avdb.MagicTools.Plugin.dll`，不要把构建目录中的 `MediaBrowser.*.dll`、
`Emby.*.dll` 或其他 SDK 文件放入 `plugins`。

#### 3A. 推荐的非 root Compose 配置

把下面两项合并到现有 Emby 服务。`UID` / `GID` 要继续使用当前媒体库和 `/config` 所需的
实际数值：

```yaml
services:
  emby:
    image: emby/embyserver:latest
    environment:
      UID: "1000"
      GID: "100"
    volumes:
      - ./config:/config
      - ./ui/avdb:/etc/cont-init.d/avdb:ro
```

不要同时用 Compose 的 `user:` 强制普通用户启动官方镜像；官方镜像需要先以 root 运行 s6
初始化，再按 `UID` / `GID` 启动 Emby。脚本在 Emby 服务启动前执行，只把
`dashboard-ui` 目录和 `index.html` 的所有者调整为配置的 `UID:GID`，不会把某个旧版本的
入口文件挂载进容器。

SELinux 主机若拒绝读取脚本，可按宿主机策略为该挂载增加标签，例如：

```yaml
- ./ui/avdb:/etc/cont-init.d/avdb:ro,Z
```

#### 3B. EmbyServer 确实以 root 运行时

只有确认 `EmbyServer` 本身是 UID 0、根文件系统可写时，才可以省略 `avdb` 挂载：

```yaml
services:
  emby:
    image: emby/embyserver:latest
    environment:
      UID: "0"
      GID: "0"
    volumes:
      - ./config:/config
```

以 root 运行会扩大 Emby 和插件对容器内文件及媒体挂载的权限。若没有其他明确需求，建议
仍使用 3A 的非 root 方案。

#### 4. 重新创建容器并加载插件

首次增加初始化脚本属于挂载配置变更，仅执行 `docker compose restart` 不会应用新挂载，
必须重新创建容器：

```bash
cd /srv/emby
docker compose config --quiet
docker compose up -d --force-recreate emby
```

在 Synology Container Manager、QNAP Container Station、Portainer 或其他图形界面中，
需要添加相同的文件挂载后选择“重新创建/重新部署”，而不是只点“重启”。容器内目标必须是
`/etc/cont-init.d/avdb`，并设为只读。

#### 5. 验证安装

先确认插件程序集和 Web 注入入口均已启动：

```bash
docker compose logs emby | grep -E \
  'Avdb.MagicTools.Plugin|WebCustomizationEntryPoint|Web 扩展'
```

日志中应看到 `Loading Avdb.MagicTools.Plugin`、`Starting entry point`，以及“已注入”或
“客户端脚本已是最新版本”。然后确认 Web 入口只有一组注入标记：

```bash
curl -fsS http://DOCKER_HOST:8096/web/index.html \
  | grep -c 'Avdb Magic Tools web customizations:begin'
```

预期输出为 `1`。最后在浏览器中强制刷新 Emby Web，打开一部没有 `fanartX` 剧照的影片：
插件会优先使用 `ProviderIds.Num`，为空时从现有标题或路径提取番号原值。确认日志出现
`[JavDB剧照]` 固化结果，并在 Emby 图片管理中看到全部合格 JavDB Backdrop；影片剧照应位于
演职人员下方、章节上方，点击后进入原生画廊。服务器提供的 `/web/` 支持该功能；使用独立内置前端的 Emby App 需要先通过
`Client-Injector` 安装 Loader，才能从服务器加载同一份功能脚本。

#### 6. 升级插件

Docker 场景不需要备份容器本身或镜像内的 `dashboard-ui`；这些内容可以通过重新创建容器
恢复。手动升级时直接替换持久化 `/config/plugins` 中的 DLL 并重启 Emby：

```bash
cd /srv/emby
docker compose stop emby
cp /path/to/new/Avdb.MagicTools.Plugin.dll \
  ./config/plugins/Avdb.MagicTools.Plugin.dll
chmod 644 ./config/plugins/Avdb.MagicTools.Plugin.dll
docker compose up -d emby
```

只有 DLL 变化而 Compose 未变化时，不需要强制重新创建容器。更新 Emby 镜像时，非 root
方案中的初始化脚本会处理新镜像内的 `index.html`，插件随后重新注入当前版本脚本。

#### 7. 常见问题与回滚

- 日志提示 `index.html` 不可写：确认 `avdb` 是可执行文件、挂载目标正确、Compose 中的
  `UID/GID` 是数字，并且已经重新创建容器。
- 插件已加载但没有剧照：确认已填写 AVDB 服务地址和 API Key；插件会优先使用 `ProviderIds.Num`，
  为空时从现有标题或路径提取番号原值。JavDB 无匹配、返回空结果或所有图片低于 30KB 时会保留已有剧照，
  没有本地剧照时该区域会整体隐藏。
- Web 页面仍是旧效果：先确认标记数量为 1，再强制刷新浏览器或清理该站点的 Service
  Worker 缓存。
- 需要回滚 DLL：停止 Emby，把准备好的可用版本重新复制为
  `config/plugins/Avdb.MagicTools.Plugin.dll`，再启动 Emby。
- 需要临时关闭剧照显示或补全：在 Emby 控制台打开“插件 → Avdb Magic Tools → 设置”，
  分别关闭“启用影片剧照”或“启用剧照补全”并保存，然后刷新浏览器，不需要重启 Emby。
- 需要彻底卸载或入口文件异常：停止 Emby，删除持久化 `/config/plugins` 中的插件 DLL，
  删除 Compose 中的 `avdb` 挂载，然后重新创建容器。新容器会从镜像恢复原始
  `dashboard-ui`。

注意，重新创建容器只会恢复镜像层；`./config:/config` 是持久化数据，其中的插件 DLL、
Emby 数据库和配置不会自动回滚。因此插件自身出问题时，应先替换或删除 DLL，再重新创建
容器。插件内部自动保存的 Web 入口备份只用于开关功能或正常卸载时原地清除注入，不需要
用户手工复制或维护。

请求体（新接口推荐使用列表，一次性处理同一影片上的多个来源 ID）：

```json
{
  "SourcePersonIds": [223674, 240785],
  "TargetPersonId": 240784
}
```

转移接口只接受 `SourcePersonIds` 列表，不保留旧的单值字段或路由别名。来源和目标 ID 是
Emby 的数字 `InternalId`。插件会为参与转移的 Person 保存一个 AVDB 专用
且基于数字 `InternalId` 的唯一 ProviderId，并在 `IItemRepository.UpdatePeople` 写入
关系时只使用这个唯一标记定位 Person。这里不能使用 Person Guid，因为部分迁移库中的
完全同名重复 Person 会共享 Guid。使用 `InternalId` 后，即使演员完全同名、Guid 相同、
普通 ProviderId 为空或重复，Emby 也不会把目标重新解析成来源。

同一影片上的多个来源 ID 会在一次 `UpdatePeople` 写入中转移，避免先转移一部分后另一
部分失败。

同一影片上的多个并发转移会在插件内串行执行。每个请求都会在取得影片锁后重新读取
最新演员列表，避免两个不同演员合并同时修改一部影片时后写请求覆盖先写请求。

接口会先读取当前演员关联，写入后再次读取验证：目标 ID 必须存在，来源 ID 必须消失。
验证失败时会用同一唯一标记恢复原始演员列表，并返回失败，不会把未验证的结果报告为
成功。

删除接口只接受管理员请求，并且只处理 `Person` 实体。Avdb 在调用前负责确认该 ID
确实是演员；插件本身不把电影、导演、编剧等媒体关联当作可删除目标。它调用 Emby 的
`ILibraryManager.DeleteItems` 删除 Person 记录，不删除影片、视频文件、目录或
其他媒体库项目。

## 与 Strm Assistant 的关系

这个项目是根据公开的 Strm Assistant Person 清理行为独立编写的兼容实现，未复制
Strm Assistant PRO 的二进制文件、闭源代码、资源或插件标识。它复用相同的 HTTP
路由，Avdb 会调用独立的 `/Plugins/AvdbMagicTools/Items/{id}/DeletePerson`，因此
可以与 Strm Assistant 原有的 `/Items/{id}/DeletePerson` 同时安装和运行。

## 安装注意事项

插件可以与 Strm Assistant 共存。安装时只需将编译得到的
`Avdb.MagicTools.Plugin.dll` 放入 Emby 的 `plugins` 目录并重启服务器；不要替换
Strm Assistant，也不要让两个插件使用同一个程序集文件名。封面使用
`cover.webp`，它会嵌入插件 DLL；插件通过 Emby 的 `IHasThumbImage` 接口提供封面，
由 Emby 内置的 `/Plugins/{id}/Thumb` 路由返回，不需要额外安装图片文件。

当前发布版本使用公开的 Emby `4.8.11` 稳定 SDK、`.NET Standard 2.0` 编译，作为
4.8+ 的兼容基线，兼容 Emby 4.8、4.9.5 及后续 4.10.x 服务器。接口同时接受 Emby
的数字型 Item ID（例如 `5918`）和 Guid 型 Item ID；数字型 ID 会按 Emby 的
`InternalId` 查找。不要使用 4.10 beta SDK 重新编译后直接发给旧版服务器，否则可能
出现插件程序集已扫描但服务和路由没有注册的情况。正式安装前仍应先在备份或隔离库
验证，因为 Person 删除是不可逆的数据库操作。

## 发布构建与代码保护

源码和普通 Debug/Release 构建保持可读；发布给 Emby 的 DLL 使用固定版本的
Obfuscar 做最后一步混淆。执行以下命令时，参数应指向发布仓库中最终要上传的 DLL：

```bash
cd avdb-magic-tools-plugin
./scripts/build-obfuscated-release.sh \
  /path/to/AVdb-Only/Avdb-Magic-Tools/Avdb.MagicTools.Plugin.dll
```

混淆只处理 `Avdb.MagicTools.Plugin.dll`，不会处理 Emby 依赖程序集。Emby 需要通过反射、
路由、序列化和嵌入资源访问的公开入口会保留名称；私有实现、内部符号和字符串会进行混淆。
`.pdb` 不进入发布目录，调试符号映射只应在发布者的私有环境中保存。混淆会提高静态反编译
和修改门槛，但不能阻止拥有服务器管理员权限的人进行运行时分析；API Key 和核心数据库逻辑
仍应放在 AVDB 服务端，不能写入插件或客户端脚本。

## 插件自动更新

插件会向 Emby 注册一个名为“插件自动/手动更新”的计划任务，安装后默认不设置
自动触发器。用户可以在 Emby 的计划任务页面自行添加触发时间或间隔，也可以随时点击“运行”
手动检查。任务只读取
`AVdb-Only/Avdb-Magic-Tools/plugin-manifest.json`，
并在发现新版本时依次校验插件 GUID、DLL 文件名、最低 Emby 版本、程序集版本和 SHA-256，
然后直接替换现有 DLL（不创建旧版本 DLL 备份）并调用 Emby 自重启接口。

首次安装必须手动把新 DLL 放入 Emby 的 `plugins` 目录并重启 Emby。更新任务需要当前 Emby
实例支持自重启；如果 `CanSelfRestart` 为 false，
任务会停止更新，不会替换现有 DLL。未配置触发器时，任务不会自动运行，但手动运行仍然可用。
任务完成后会在 Emby 活动记录中写入“已是最新版本”、发现更新、更新完成、取消或失败等结果。
任务运行栏显示数字阶段进度；Emby 的标准 `IProgress<double>` 不支持在百分比位置显示自定义文字，
因此“已是最新版本”等文字结果位于活动记录中。

默认版本清单地址：

```text
https://raw.githubusercontent.com/li-peifeng/AVdb-Only/refs/heads/main/Avdb-Magic-Tools/plugin-manifest.json
```

每次读取 manifest 时会自动添加缓存绕过参数，避免 GitHub Raw 或中间代理返回旧版本清单。
发布目录中的 manifest、SHA-256 文件和安装说明位于 `AVdb-Only/Avdb-Magic-Tools`。

Emby 计划任务页面按任务分类和名称排序，因此“插件自动/手动更新”会位于本插件任务组的最后，
排在 `STRM 媒体信息预提取` 和“R18 海报和封面补全”“JavDB 剧照补全”之后。

### 从 Avdb Actor Tools 手动迁移

Avdb Actor Tools 与本插件完全不兼容，旧发布目录不会提供迁移 DLL，也不能通过旧计划任务
自动更新到本插件。迁移前请在旧插件设置中关闭所有 Web 功能并保存，使旧注入块正常移除；
随后停止 Emby，删除 `Avdb.ActorTools.Plugin.dll`，再复制
`Avdb.MagicTools.Plugin.dll` 并启动 Emby。不要同时保留两个 DLL。

新插件使用独立 GUID，旧设置不会继承。安装完成后需要重新选择媒体库、轮播主题、写真行列数
等设置。若旧插件已无法启动或旧注入块仍残留，Docker 用户可在移走旧 DLL 后重新创建容器，
让镜像恢复原始 `dashboard-ui/index.html`，再启动新插件完成注入。
