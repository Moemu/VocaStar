# VocaStar

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Black CodeStyle](https://img.shields.io/badge/Code%20Style-Black-121110.svg)
![wakatime](https://wakatime.com/badge/user/637d5886-8b47-4b82-9264-3b3b9d6add67/project/d6391b48-7f4e-46ad-94f1-34221f72a2ed.svg)
[![Test and Coverage](https://github.com/Moemu/VocaStar/actions/workflows/pytest.yaml/badge.svg)](https://github.com/Moemu/VocaStar/actions/workflows/pytest.yaml)
![coverage](./src/coverage.svg)

VocaStar 是一个基于 FastAPI 的职业规划与测评平台后端服务。提供用户认证、职业探索、个性化测评、Cosplay 剧本体验等功能，帮助用户发现和规划职业发展路径。

## ✨ 主要特性

- 🔐 **用户认证系统**：JWT Token 认证、登录登出、密码重置
- 📊 **智能测评系统**：个性化职业测评、答题会话管理、自动生成分析报告
- 💼 **职业探索**：职业列表、详情查询、多维度筛选、推荐职业
- 🎭 **Cosplay 剧本**：互动式职业体验、场景选择、总结报告
- 🚀 **高性能架构**：异步数据库操作、Redis 缓存、RESTful API 设计

## 📋 目录

- [快速开始](#快速开始)
  - [环境要求](#环境要求)
  - [本地开发](#本地开发)
  - [Docker 部署](#Docker-部署)
- [API 文档](#api-文档)
- [数据导入](#导入数据)
- [开发指南](#开发指南)
- [贡献](#贡献)
- [许可证](#许可证)

## 快速开始

### 环境要求

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/) (推荐) 或 pip
- Redis >= 6.0

### 本地开发

**1. 克隆仓库**

```shell
git clone https://github.com/Moemu/VocaStar.git
cd VocaStar
```

**2. 安装依赖**

使用 uv (推荐):
```shell
uv sync
```

或使用 pip:
```shell
pip install .
```

**3. 导入初始数据**

```shell
# 使用 uv
uv run python scripts/import_careers_from_yaml.py
uv run python scripts/import_quiz_from_yaml.py
uv run python scripts/import_cosplay_from_yaml.py

# 或使用 python
python scripts/import_careers_from_yaml.py
python scripts/import_quiz_from_yaml.py
python scripts/import_cosplay_from_yaml.py
```

**4. 启动服务**

```shell
# 使用 uv
uv run python -m app.main

# 或使用 python
python -m app.main
```

服务将在 <http://127.0.0.1:8080> 启动

### Docker 部署

**1. 准备数据目录和配置文件**

```shell
# 创建数据持久化目录
mkdir -p app/data

# 创建 .env 文件
# 参考上方环境变量配置，至少需要配置：
```

创建 `.env` 文件：

```env
ENV=prod
CORS_ALLOW_ORIGINS=["https://example.com"]
DATABASE_URL=sqlite+aiosqlite:///app/data/database.db
SECRET_KEY=your-production-secret-key
OPENAI_API_KEY=your-openai-api-key
```

**2. 启动容器**

```shell
docker-compose up --build -d
```

**3. 访问服务**

- API 服务：<http://localhost:8000>
- API 文档：<http://localhost:8000/docs>

**4. 查看日志**

```shell
docker-compose logs -f app
```

**5. 停止服务**

```shell
docker-compose down
```

## API 文档

启动服务后，可以通过以下方式查看 API 文档：

- **本地 Swagger UI**：<http://127.0.0.1:8080/docs>
- **本地 ReDoc**：<http://127.0.0.1:8080/redoc>
- **在线 APIFox 文档**：<https://vocastar.snowy.moe/>

## API 适配情况

**✅ 已完成**

**鉴权相关**

| API                  | 方法 | 说明     |
| -------------------- | ---- | -------- |
| `/api/auth/login`    | POST | 登录接口 |
| `/api/auth/register` | POST | 注册接口 |
| `/api/auth/logout`   | POST | 登出接口 |

**用户相关**

| API                       | 方法 | 说明             |
| ------------------------- | ---- | ---------------- |
| `/api/user/resetpw`       | POST | 重置密码         |
| `/api/user/profile`       | GET  | 获取用户信息     |
| `/api/user/profile`       | POST | 设置用户信息     |
| `/api/user/avatar`        | POST | 上传用户头像     |

**测评（Quiz）相关**

| API                  | 方法 | 说明                         |
| -------------------- | ---- | ---------------------------- |
| `/api/quiz/start`    | POST | 创建/获取测评会话            |
| `/api/quiz/profile`  | POST | 保存/更新用户个性化档案       |
| `/api/quiz/profile`  | GET  | 获取用户个性化档案           |
| `/api/quiz/questions`| GET  | 获取题目与当前作答状态       |
| `/api/quiz/answer`   | POST | 保存作答                     |
| `/api/quiz/submit`   | POST | 提交测评并生成报告           |
| `/api/quiz/report`   | GET  | 查看已生成的测评报告与推荐   |

**职业（Career）相关**

| API                        | 方法 | 说明                                                         |
| -------------------------- | ---- | ------------------------------------------------------------ |
| `/api/career`              | GET  | 分页获取职业列表，支持维度与关键词筛选                         |
| `/api/career/featured`     | GET  | 获取推荐职业列表，可按维度过滤                                 |
| `/api/career/exploration`  | GET  | 职业星球探索数据，支持分类、薪资均值与测评推荐过滤             |
| `/api/career/{careerId}`   | GET  | 获取指定职业的详细信息                                         |

**Cosplay 剧本相关**

| API                                           | 方法 | 说明                                   |
| --------------------------------------------- | ---- | -------------------------------------- |
| `/api/cosplay/scripts`                        | GET  | 获取可用 Cosplay 剧本列表              |
| `/api/cosplay/scripts/{scriptId}`             | GET  | 查看指定 Cosplay 剧本详情             |
| `/api/cosplay/scripts/{scriptId}/sessions`    | POST | 创建或恢复用户 Cosplay 会话           |
| `/api/cosplay/sessions/{sessionId}`           | GET  | 查询 Cosplay 会话当前状态             |
| `/api/cosplay/sessions/{sessionId}/choice`    | POST | 在当前场景中提交选项                  |
| `/api/cosplay/sessions/{sessionId}/report`    | GET  | 获取已完成会话的总结报告              |

**首页聚合相关**

| API                 | 方法 | 说明                   |
| ------------------- | ---- | ---------------------- |
| `/api/home/summary` | GET  | 首页个人信息与推荐聚合 |

**🚧 计划中/开发中**

...

## 📦 导入数据

测评题库数据与职业信息分别存放于 `assets/quizzes.yaml`、`assets/careers.yaml`、`assets/cosplay.yaml`，可根据需要修改。

> ⚠️ **注意**：首次启动服务前必须导入数据，否则 API 将无法正常工作。

运行以下脚本以导入对应数据：

```shell
# 使用 uv
uv run python scripts/import_quiz_from_yaml.py
uv run python scripts/import_careers_from_yaml.py
uv run python scripts/import_cosplay_from_yaml.py

# 或使用 python
python scripts/import_quiz_from_yaml.py
python scripts/import_careers_from_yaml.py
python scripts/import_cosplay_from_yaml.py
```

> 💡 **提示**：Docker 部署时会在容器启动时自动导入数据，无需手动执行。

## 🗄️ 数据库管理

### 重置数据库

删除项目根目录下的 `database.db` 文件即可重置数据库：

```shell
# Windows
del database.db

# Linux/Mac
rm database.db
```

然后重新导入数据。

### 数据迁移

如需进行数据库迁移，请参考 `scripts/migrate_*.py` 脚本。

## ⚙️ 常见配置

| 配置项            | 环境变量               | 默认值                           | 说明 |
| ----------------- | ---------------------- | -------------------------------- | ---- |
| env               | `ENV`                  | `dev`                            | 运行环境标识，`dev` 或 `prod` |
| log_level         | `LOG_LEVEL`            | `DEBUG`(dev) / `INFO`(prod)      | FastAPI 与应用日志等级 |
| host              | `HOST`                 | `127.0.0.1`                      | 应用监听地址 |
| port              | `PORT`                 | `8080`                           | 应用监听端口 |
| cors_allow_origins | `CORS_ALLOW_ORIGINS`   | `[*]` (dev) / `[]` (prod)        | 允许的跨域来源列表（JSON 数组） |
| secret_key        | `SECRET_KEY`           | 示例开发密钥                     | JWT 签名密钥，生产环境务必重置 |
| algorithm         | `ALGORITHM`            | `HS256`                          | JWT 算法 |
| expire_minutes    | `EXPIRE_MINUTES`       | `720`                            | JWT 过期时间（分钟） |
| db_url            | `DATABASE_URL`         | `sqlite+aiosqlite:///./database.db` | SQLAlchemy 异步连接串 |
| redis_host        | `REDIS_HOST`           | `localhost`                      | Redis 主机 |
| redis_port        | `REDIS_PORT`           | `6379`                           | Redis 端口 |
| static_dir        | `STATIC_DIR`           | `app/static`                     | 静态资源目录（可覆盖） |
| avatar_url_prefix | `AVATAR_URL_PREFIX`    | `/static/avatars`                | 头像访问前缀，用于拼接 URL |
| max_avatar_size   | `MAX_AVATAR_SIZE`      | `2097152`                        | 头像大小上限（字节） |
| jwxt_encryption_key | `JWXT_ENCRYPTION_KEY`| 自动生成的示例密钥               | 教务系统密码加密密钥 |
| jwxt_sync_interval_days | `JWXT_SYNC_INTERVAL_DAYS` | `90`                  | 教务数据自动同步间隔 |
| llm_api_base_url  | `LLM_API_BASE_URL`     | 空字符串                         | OpenAI 兼容接口地址 |
| llm_api_key       | `LLM_API_KEY`          | 空字符串                         | LLM 服务访问密钥 |
| llm_default_model | `LLM_DEFAULT_MODEL`    | `gpt-4o-mini`                    | 默认使用的模型名称 |
| llm_request_timeout | `LLM_REQUEST_TIMEOUT`| `30.0`                           | LLM 请求超时时间（秒） |

> ℹ️ 更多可配置项可在 `app/core/config.py` 中查看，所有字段均支持通过同名大写环境变量覆盖。

## 🗃️ 数据库结构

| 表名 | 关键字段 | 关联关系 | 主要用途 |
| ---- | -------- | -------- | -------- |
| `users` | `username`, `email`, `role`, `last_login_at` | `user_profiles`, `quiz_submissions`, `cosplay_sessions`, `user_points` | 存储用户账号、基本信息与状态 |
| `user_profiles` | `career_stage`, `major`, `short_term_goals` | `users.user_id` (一对一) | 保存用户的个性化职业档案 |
| `quizzes` | `title`, `is_published`, `config` | `questions`, `quiz_submissions` | 定义测评题库与发布状态 |
| `questions` | `question_type`, `order`, `settings` | `quizzes.quiz_id`, `options` | 描述测评中的题目内容与配置 |
| `options` | `content`, `dimension`, `score`, `order` | `questions.question_id`, `quiz_answers` | 存储题目备选项及计分信息 |
| `quiz_submissions` | `session_token`, `status`, `expires_at` | `users.user_id`, `quizzes.quiz_id`, `quiz_answers`, `quiz_reports` | 记录用户的测评会话与状态 |
| `quiz_answers` | `option_id`, `option_ids`, `rating_value`, `extra_payload` | `quiz_submissions.submission_id`, `questions.question_id`, `options.option_id` | 持久化用户作答数据 |
| `quiz_reports` | `result_json` | `quiz_submissions.submission_id`, `career_recommendations` | 存储测评生成的分析报告 |
| `career_galaxies` | `name`, `category`, `description` | `careers.galaxy_id` | 职业探索星系分组信息 |
| `careers` | `name`, `holland_dimensions`, `salary_min/max`, `skills_snapshot` | `career_galaxies`, `career_recommendations`, `cosplay_scripts` | 职业星球基础信息与维度配置 |
| `career_recommendations` | `score`, `match_reason` | `quiz_reports.report_id`, `careers.career_id` | 记录测评推荐的职业及匹配理由 |
| `cosplay_scripts` | `career_id`, `title`, `content` | `careers.career_id`, `cosplay_sessions` | 定义职业 Cosplay 剧本与剧情内容 |
| `cosplay_sessions` | `progress`, `state`, `state_payload` | `users.user_id`, `cosplay_scripts.script_id`, `cosplay_reports` | 跟踪用户的 Cosplay 体验进度 |
| `cosplay_reports` | `result_json` | `cosplay_sessions.session_id` | 存储 Cosplay 完成后的总结报告 |
| `user_points` | `points` | `users.user_id`, `point_transactions` | 保存用户可用积分余额 |
| `point_transactions` | `amount`, `reason` | `user_points.user_points_id` | 记录积分增减流水 |

> 📌 以上表结构基于 SQLAlchemy ORM 模型概览整理，实际字段以迁移脚本或数据库实例为准。

## 🛠️ 开发指南

### 运行测试

```shell
# 安装测试依赖
pip install .[test]

# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html

# 查看覆盖率报告
# Windows: start htmlcov/index.html
# Linux/Mac: open htmlcov/index.html
```

### 代码规范

项目使用以下工具保证代码质量：

- **Black**：代码格式化 (120 字符行宽)
- **isort**：导入语句排序
- **mypy**：类型检查
- **flake8**：代码风格检查

安装 pre-commit hook：

```shell
pip install pre-commit
pre-commit install
```

手动运行代码检查：

```shell
pre-commit run --all-files
```

### 项目结构

```
FinancialCareerCommunity/
├── app/                    # 应用主目录
│   ├── api/               # API 路由
│   ├── core/              # 核心配置
│   ├── models/            # 数据库模型
│   ├── repositories/      # 数据访问层
│   ├── schemas/           # Pydantic 模型
│   ├── services/          # 业务逻辑层
│   └── main.py            # 应用入口
├── assets/                # 静态数据文件
├── scripts/               # 工具脚本
├── tests/                 # 测试文件
├── docker-compose.yml     # Docker 编排
├── Dockerfile            # Docker 镜像
└── pyproject.toml        # 项目配置
```

## 🤝 贡献

欢迎贡献代码！请查看 [贡献指南](./CONTRIBUTING.md) 了解详情。

## 📝 许可证

本项目采用 [MIT License](./LICENSE) 许可证。

数据来源:

- 职业数据: [O*Net Web Services](https://services-beta.onetcenter.org/), [学职平台](https://xz.chsi.com.cn/home.action)
- 职业头图: [Pexels](https://www.pexels.com/zh-cn/)