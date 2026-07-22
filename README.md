<p align="center">
  <a href="https://peifeng.li"><img width="184" alt="AVDB logo" src="public/logo.svg" /></a>
</p>
<p align="center">
  <a href="https://hub.docker.com/r/leolitaly/avdb"><img src="https://img.shields.io/docker/pulls/leolitaly/avdb?color=%2348BB78&logo=docker&label=pulls" alt="Docker pulls" /></a>
</p>

# Avdb

Avdb 是面向个人影视资源管理的全流程自动化系统，覆盖「站点采集 → 规则筛选 → 下载入库 → Emby 联动 → 消息通知 → 可视化管理」。

## 核心特色

### 双站点采集引擎

- 内置色花堂 / X1080X 采集任务。
- 支持按游标智能增量与全量回填。
- 支持版块过滤、并发控制、异常重试与采集后资源库导出。

### 规则驱动自动下载

- 按版块、分类、关键字和时间窗口筛选资源。
- 规则可指定下载器与保存目录，任务触发后自动提交下载。
- 支持下载记录追踪与快捷下载模式。

### 多下载器统一接入

- 支持 qBittorrent、Transmission、迅雷、CloudNAS / CloudDrive 与 115。
- 下载器配置可即时更新，无需重启整套服务。

### Emby 深度联动与演员管理

- 支持媒体库匹配、Webhook、自动刷新和快捷播放入口。
- 可补齐演员头像、简介、性别、TMDB ID 等资料。
- 提供演员搜索、重名检测、头像管理、重命名、删除与映射表维护工具。

### 可观测任务调度

- 基于 APScheduler 的 Cron 任务系统，支持新增、编辑、启停、立即执行与运行状态追踪。
- 支持资源库自动导出、在线更新检查与运行日志查看。

### 通知中心

- 支持 Telegram / 企业微信通知、模板消息和事件开关。
- 下载完成与 Emby 媒体新增、删除事件均可联动推送。

### 前后端一体化与移动端适配

- 后端直接托管前端构建产物，统一访问入口。
- 支持图片代理与缓存、登录页海报墙、图片预览与下载、PWA 移动端适配。

## 文档与指南

详细配置、部署和维护文档均在 Wiki：

| 文档 | 内容 |
| --- | --- |
| [Avdb 使用指南](https://github.com/li-peifeng/AVdb-Only/wiki) | 全部页面、功能说明与使用路径。 |
| [安装与部署指南](https://github.com/li-peifeng/AVdb-Only/wiki/%E5%AE%89%E8%A3%85%E4%B8%8E%E9%83%A8%E7%BD%B2%E6%8C%87%E5%8D%97) | Docker Compose、容器作用、端口、数据卷与部署检查。 |
| [更新日志](https://github.com/li-peifeng/AVdb-Only/wiki/%E6%9B%B4%E6%96%B0%E6%97%A5%E5%BF%97) | 版本更新历史。 |

**AVDB by LeoLi** · [Telegram：@avdb_chat](https://t.me/avdb_chat) ☕️ [爱发电](https://ifdian.net/a/leoavdb)
