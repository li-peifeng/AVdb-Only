<p align="center">
  <a href="https://peifeng.li"><img width="184px" alt="logo" src="public/logo.svg" />
  </a>
</p>
<p align="center">
  <a href="https://hub.docker.com/r/leolitaly/avdb">
    <img src="https://img.shields.io/docker/pulls/leolitaly/avdb?color=#48BB78&logo=docker&label=pulls" alt="Downloads" />
  </a>
</p>

# Avdb

Avdb 是一个面向个人影视资源管理的全流程自动化系统，覆盖「站点采集 -> 规则筛选 -> 下载入库 -> Emby 联动 -> 消息通知 -> 可视化管理」。

项目由 Python FastAPI 后端与 React 前端组成，支持本地部署与 Docker 部署，适合长期运行和定时任务场景。

## 核心特色

### 1. 双站点采集引擎（智能增量 + 全量）
- 内置 色花堂 / X1080X 采集任务。
- 支持断点续爬（按游标增量）与全量回填两种模式。
- 支持按版块过滤、并发参数控制、异常重试。

### 2. 规则驱动自动下载
- 可配置多条规则（版块、分类、关键字、时间窗口等）自动筛选资源。
- 支持任务编排后按路由一键入库。
- 下载记录可追踪，便于回溯和排错。

### 3. 多下载器统一接入
- 统一下载适配层，当前支持：
  - qBittorrent
  - Transmission
  - 迅雷
  - CloudNAS / CloudDrive
  - 115
- 下载器配置热更新，无需重启整套服务。

### 4. Emby 深度联动
- 支持 Emby Webhook 增删事件处理。
- 资源番号与媒体库匹配（含增量游标、批量匹配、松弛匹配逻辑）。
- 支持 Emby 定时自动刷新。
- 提供演员资料补全能力（可选头像与简介补全流程）。

### 5. 可观测任务调度
- 基于 APScheduler 的 Cron 调度系统。
- 任务支持：新增、编辑、启停、立即执行、运行中状态追踪。
- 具备最小调度间隔保护（防止高频误触发）和线程数规范化。

### 6. 通知中心（模板化推送）
- 支持 Telegram / 企业微信通知。
- Telegram 支持轮询和 Webhook 推送
- 支持模板消息、图片链接、按通知器开关控制。
- 下载完成与 Emby 事件可联动推送。

### 7. 前后端一体化交付
- 后端可直接托管前端构建产物（frontend/dist）。
- 统一访问入口，简化部署与运维。
- 内置图片代理、缓存与登录页海报墙能力。

## 技术栈

- 后端：FastAPI, SQLAlchemy, APScheduler
- 数据库：PostgreSQL（推荐）/ SQLite（可选）
- 前端：React + Vite + TanStack Router + Tailwind CSS（独立仓库 Avdb-UI）
- 下载协议与三方集成：qBittorrent、Transmission、迅雷、CloudDrive/115、Emby

## 数据库配置（PostgreSQL / SQLite）

项目支持 PostgreSQL 与 SQLite 两种数据库。

- 推荐 PostgreSQL（并发与维护能力更好）。
- 轻量部署或单机测试可直接使用 SQLite。

当同时配置了 `DATABASE_URL` 与 `POSTGRES_*` 时，优先使用 `DATABASE_URL`。

### PostgreSQL 示例

```env
POSTGRES_HOST=10.0.0.8
POSTGRES_PORT=5433
POSTGRES_USER=avdb
POSTGRES_PASSWORD=your_password
POSTGRES_DB=avdb
DATABASE_URL=postgresql://avdb:your_password@10.0.0.3:5433/avdb
```

### SQLite 示例

```env
# 使用 SQLite 时，直接填写 DATABASE_URL 即可
DATABASE_URL=sqlite:///./data/avdb.db

# 可留空（或移除）POSTGRES_* 配置
POSTGRES_HOST=
POSTGRES_PORT=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
```

### 切换建议

- 从 PostgreSQL 切到 SQLite：建议使用独立数据库文件，避免混用旧数据。
- 从 SQLite 切到 PostgreSQL：建议先全量导出/迁移数据后再切换生产环境。
- 首次切换后，建议启动一次服务并观察日志中数据库方言输出是否符合预期。

## Docker Compose 部署示例

如果你使用 Docker 部署，推荐使用下面两种 compose 方式之一。

### 方式 1：SQLite（最简单）

```yaml
services:
  avdb:
    image: leolitaly/avdb:latest
    container_name: avdb
    network_mode: bridge
    ports:
      - "8000:8000"
    volumes:
      - ./data:/data
    environment:
      - DATABASE_URL=sqlite:////data/avdb.db
```

### 方式 2：PostgreSQL（推荐使用）

```yaml
services:
  postgres:
    image: postgres:16-alpine
    container_name: postgres
    restart: unless-stopped
    environment:
      - POSTGRES_USER=avdb
      - POSTGRES_PASSWORD=change_me
      - POSTGRES_DB=avdb
    volumes:
      - ./postgres-data:/var/lib/postgresql/data

  avdb:
    image: leolitaly/avdb:latest
    container_name: avdb
    restart: unless-stopped
    depends_on:
      - postgres
    ports:
      - "8000:8000"
    volumes:
      - ./data:/data
    environment:
      - DATABASE_URL=postgresql://avdb:change_me@postgres:5432/avdb
      # 下面这组可留空；若同时配置，程序优先使用 DATABASE_URL
      - POSTGRES_HOST=
      - POSTGRES_PORT=
      - POSTGRES_USER=
      - POSTGRES_PASSWORD=
      - POSTGRES_DB=
```

提示：首次启动后可在日志中确认（sqlite/postgresql）是否符合预期。

仓库已内置可直接运行的 [docker-compose.yml](docker-compose.yml)：

## 典型使用流程

1. 配置下载器（qBittorrent/Transmission/迅雷/CloudDrive/115）
2. 新建采集与入库任务（智能增量或全量）
3. 配置规则并触发自动下载
4. 打开 Emby 集成与 Webhook
5. 开启通知推送，接收入库与状态变更消息

## 安全建议

- 生产环境请关闭不必要的跨域配置并限制来源。
- 使用强密码与独立数据库账号。
- Webhook 建议开启签名或密钥校验。
- 通过反向代理（如 Nginx）启用 HTTPS。

## Telegram 交流群

https://t.me/avdb_chat

## 免责声明

本项目仅用于个人学习与技术研究，请遵守当地法律法规及相关站点服务条款。