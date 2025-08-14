# JetTask

高性能分布式任务队列系统，带有实时 Web 监控界面。

## 特性

- 🚀 **高性能**: 基于 Redis 和异步 IO 的高性能任务处理
- 📊 **实时监控**: 美观的 Web UI 实时监控任务状态
- 🔄 **分布式**: 支持多队列、多 Worker 的分布式架构
- 📈 **数据可视化**: 任务处理趋势图表和统计分析
- 🎯 **灵活配置**: 支持多种任务类型和处理策略
- 🔍 **任务追踪**: 完整的任务生命周期追踪

## 安装

### 使用 pip 安装

```bash
pip install jettask
```

### 从源码安装

```bash
git clone https://github.com/yourusername/jettask.git
cd jettask
pip install -e .
```

## 快速开始

### 1. 初始化系统

```bash
jettask init
```

### 2. 启动 Web UI

```bash
jettask webui
# 或指定端口
jettask webui --port 8080
```

访问 http://localhost:8001 查看监控界面

### 3. 启动 Worker

```bash
jettask worker main:app --queues default --concurrency 4
```

### 4. 检查系统状态

```bash
jettask status
```

## 系统要求

- Python 3.8+
- Redis 6.0+
- PostgreSQL 12+

## 环境配置

创建 `.env` 文件配置系统参数：

```env
# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# PostgreSQL 配置
JETTASK_PG_HOST=localhost
JETTASK_PG_PORT=5432
JETTASK_PG_DB=jettask
JETTASK_PG_USER=jettask
JETTASK_PG_PASSWORD=123456
```

## 命令行工具

JetTask 提供了丰富的命令行工具：

```bash
# 查看帮助
jettask --help

# 启动 Web UI
jettask webui

# 启动 Worker
jettask worker app:tasks --queues queue1,queue2

# 启动 WebUI 数据消费者
jettask webui-consumer

# 启动监控器
jettask monitor

# 初始化数据库
jettask init

# 查看系统状态
jettask status
```

## 开发

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black jettask/
```

## 架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Producer  │────▶│    Redis    │◀────│   Worker    │
└─────────────┘     └─────────────┘     └─────────────┘
                           │                     │
                           ▼                     ▼
                    ┌─────────────┐     ┌─────────────┐
                    │ PostgreSQL  │     │  Monitoring │
                    └─────────────┘     └─────────────┘
                           │                     │
                           └──────────┬──────────┘
                                      ▼
                              ┌─────────────┐
                              │   Web UI    │
                              └─────────────┘
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 支持

- 文档: https://jettask.readthedocs.io
- Issue: https://github.com/yourusername/jettask/issues
- 邮箱: support@jettask.io