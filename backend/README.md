# VocaStar Backend

VocaStar 是一个基于 FastAPI 的职业规划与测评平台后端服务，提供用户认证、职业探索、个性化测评、Cosplay 剧本体验、学习社区等功能。项目总览见[仓库根 README](../README.md)。

## 环境要求

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/) (推荐) 或 pip
- Redis >= 6.0

## 本地开发

以下命令均在本目录（`backend/`）下执行：

```shell
# 安装依赖
uv sync        # 或 pip install .

# 导入初始数据（首次启动前必须执行）
uv run python scripts/import_careers_from_yaml.py
uv run python scripts/import_quiz_from_yaml.py
uv run python scripts/import_cosplay_from_yaml.py

# 初始化社区模块（幂等，可重复执行）
python migrate/add_community_tables.py
python migrate/add_community_posts.py

# 启动服务
uv run python -m app.main
```

服务将在 <http://127.0.0.1:8080> 启动，API 文档见 <http://127.0.0.1:8080/docs>。

## 配置

所有配置项均支持通过环境变量覆盖（如 `DATABASE_URL`、`SECRET_KEY`、`REDIS_HOST` 等），完整配置表见[根 README 的常见配置节](../README.md#️-常见配置)。本地开发可在本目录创建 `.env` 文件加载。

## 测试

```shell
uv run pytest -q
```
