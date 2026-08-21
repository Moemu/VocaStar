# VocaStar

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Vue](https://img.shields.io/badge/Vue-3.5-42b883)
![Black CodeStyle](https://img.shields.io/badge/Code%20Style-Black-121110.svg)
![wakatime](https://wakatime.com/badge/user/637d5886-8b47-4b82-9264-3b3b9d6add67/project/d6391b48-7f4e-46ad-94f1-34221f72a2ed.svg)
[![Test and Coverage](https://github.com/Moemu/VocaStar/actions/workflows/pytest.yaml/badge.svg)](https://github.com/Moemu/VocaStar/actions/workflows/pytest.yaml)
![coverage](./.github/badges/coverage.svg)

VocaStar 是一个职业规划与测评平台，本仓库包含完整的前后端代码：

- **[`backend/`](./backend/README.md)** — 后端服务 VocaStar：基于 FastAPI，提供用户认证、职业探索、个性化测评、Cosplay 剧本体验、学习社区等功能
- **[`frontend/`](./frontend/README.md)** — Web 前端 CareerVoyage：基于 Vue 3 + Vite 的单页应用

> 🏅 本项目为学校软件设计大赛决赛作品，荣获二等奖（2025/11）。

## ✨ 主要特性

- 🔐 **用户认证系统**：JWT Token 认证、登录登出、密码重置
- 📊 **智能测评系统**：个性化职业测评、答题会话管理、自动生成分析报告
- 💼 **职业探索**：职业列表、详情查询、多维度筛选、推荐职业
- 🎭 **Cosplay 剧本**：互动式职业体验、场景选择、总结报告
- � **学习社区**：小组分类/搜索/详情、成员加入/退出、动态/评论/点赞、资料库聚合
- �🚀 **高性能架构**：异步数据库操作、Redis 缓存、RESTful API 设计

## 📋 目录

- [快速开始](#快速开始)
  - [环境要求](#环境要求)
  - [启动后端](#启动后端)
  - [启动前端](#启动前端)
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
- Node.js `^20.19.0 || >=22.12.0` 与 [pnpm](https://pnpm.io/)（仅前端开发需要）

### 启动后端

**1. 克隆仓库**

```shell
git clone https://github.com/Moemu/VocaStar.git
cd VocaStar
```

**2. 安装依赖并导入初始数据**（以下命令均在 `backend/` 目录下执行）

```shell
cd backend

# 使用 uv (推荐)
uv sync

# 或使用 pip
pip install .
```

```shell
# 使用 uv
uv run python scripts/import_careers_from_yaml.py
uv run python scripts/import_quiz_from_yaml.py
uv run python scripts/import_cosplay_from_yaml.py

# 或使用 python
python scripts/import_careers_from_yaml.py
python scripts/import_quiz_from_yaml.py
python scripts/import_cosplay_from_yaml.py

# 初始化社区模块（可重复执行，安全幂等）
python migrate/add_community_tables.py
python migrate/add_community_posts.py
```

**3. 启动服务**

```shell
# 使用 uv
uv run python -m app.main

# 或使用 python
python -m app.main
```

服务将在 <http://127.0.0.1:8080> 启动。

### 启动前端

前端详见 [`frontend/README.md`](./frontend/README.md)，简要步骤：

```shell
cd frontend
pnpm install
cp .env.example .env   # 默认留空即可
pnpm dev
```

打开 <http://localhost:5173>，开发模式下 `/api` 与 `/static` 请求自动代理到 `http://127.0.0.1:8080`。

### Docker 部署

**1. 准备配置文件**

数据库通过 docker compose 命名卷持久化，无需手动创建数据目录。在 `backend/` 目录下创建 `.env` 文件（compose 的 `env_file` 为必填项，缺失会启动失败）：

```shell
cd backend
```

```env
ENV=prod
CORS_ALLOW_ORIGINS=["https://example.com"]
DATABASE_URL=sqlite+aiosqlite:///app/data/database.db
SECRET_KEY=your-production-secret-key
OPENAI_API_KEY=your-openai-api-key
```

**2. 启动容器**（在仓库根目录执行）

```shell
docker-compose up --build -d
```

**3. 访问服务**

- API 服务：<http://localhost:8080>
- API 文档：<http://localhost:8080/docs>

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
**社区（Community）相关**（已拆分为 3 个子路由）

子路由：`/api/community/groups`

| API                                              | 方法   | 说明                                        |
| ------------------------------------------------ | ------ | ------------------------------------------- |
| `/api/community/groups/categories`               | GET    | 获取学习小组分类列表                         |
| `/api/community/groups`                          | GET    | 小组搜索/筛选（分页）                        |
| `/api/community/groups/{groupId}`                | GET    | 小组详情（含组规/拥有者/是否加入/是否点赞）   |
| `/api/community/groups/{groupId}/join`           | POST   | 加入小组（幂等）                              |
| `/api/community/groups/{groupId}/membership`     | DELETE | 退出小组（幂等）                              |
| `/api/community/groups/{groupId}/members`        | GET    | 小组成员列表（分页，组长优先）                |
| `/api/community/groups/{groupId}/like`           | POST   | 点赞小组（幂等）                              |
| `/api/community/groups/{groupId}/like`           | DELETE | 取消点赞小组（幂等）                          |
| `/api/community/groups/my`                       | GET    | 我加入的小组（分页）                          |
| `/api/community/groups/feed`                     | GET    | 社区动态（分页，最新/最热）                   |
| `/api/community/groups/posts`                    | POST   | 发布动态（支持图片/URL/文档类附件）           |
| `/api/community/groups/posts/{postId}/like`      | POST   | 给动态点赞（幂等）                            |
| `/api/community/groups/posts/{postId}/comments`  | POST   | 在动态下发布评论                              |
| `/api/community/groups/repository`               | GET    | 资料库（分页，按 文档/视频/PDF/代码 分类）     |
| `/api/community/groups/attachments/upload`       | POST   | 上传附件（image/document/video/pdf/code），返回可用 URL |

子路由：`/api/community/partners`

| API                                            | 方法   | 说明                                   |
| ---------------------------------------------- | ------ | -------------------------------------- |
| `/api/community/partners/search`               | GET    | 搜索伙伴（关键词/技能，分页）            |
| `/api/community/partners/hot-skills`           | GET    | 热门技能标签 Top-N                      |
| `/api/community/partners/recommended`          | GET    | 推荐伙伴（登录时排除已绑定，隐藏进度）     |
| `/api/community/partners/{partnerId}/bind`     | POST   | 绑定伙伴（幂等）                         |
| `/api/community/partners/{partnerId}/bind`     | DELETE | 解绑伙伴（幂等）                         |
| `/api/community/partners/my`                   | GET    | 我的伙伴（分页，隐藏技术栈）              |

子路由：`/api/community/mentors`

| API                                            | 方法   | 说明                                   |
| ---------------------------------------------- | ------ | -------------------------------------- |
| `/api/community/mentors/domains`               | GET    | 导师领域列表（自动补全默认领域）          |
| `/api/community/mentors/search`                | GET    | 搜索导师（关键词/技能/领域，分页）        |
| `/api/community/mentors/{mentorId}/request`    | POST   | 创建导师咨询/提问申请（需登录）           |

说明：
- 动态附件中的 URL 会在发布时尝试解析网页 `<title>` 作为标题（失败则为空，不阻塞发布）。
- 资料库是对动态中“文档/视频/PDF/代码”类型附件的聚合，不单独提供上传接口。

**个人中心（Profile Center）相关**

子路由：`/api/profile`

| API                            | 方法 | 说明                               |
| ------------------------------ | ---- | ---------------------------------- |
| `/api/profile/me`              | GET  | 获取我的资料（头像/昵称/简介/积分） |
| `/api/profile/me`              | POST | 设置我的资料（头像/昵称/简介）       |
| `/api/profile/dashboard`       | GET  | 我的首页看板（最近测评画像与推荐）   |
| `/api/profile/explorations`    | POST | 批量写入职业探索进度（幂等 upsert）   |
| `/api/profile/explorations`    | GET  | 获取职业探索进度列表                 |
| `/api/profile/favorites`       | POST | 添加收藏（支持 career 等条目）       |
| `/api/profile/favorites`       | GET  | 收藏列表                             |
| `/api/profile/wrongbook`       | GET  | 错题本（剧本练习错题记录）           |

| API                 | 方法 | 说明                   |
| ------------------- | ---- | ---------------------- |
| `/api/home/summary` | GET  | 首页个人信息与推荐聚合 |

**🚧 计划中/开发中**

...

## 📦 导入数据

测评题库数据与职业信息分别存放于 `backend/assets/quizzes.yaml`、`backend/assets/careers.yaml`、`backend/assets/cosplay.yaml`，可根据需要修改。

> ⚠️ **注意**：首次启动服务前必须导入数据，否则 API 将无法正常工作。

在 `backend/` 目录下运行以下脚本以导入对应数据：

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

删除 `backend/` 目录下的 `database.db` 文件即可重置数据库：

```shell
# Windows
del backend\database.db

# Linux/Mac
rm backend/database.db
```

然后重新导入数据。

### 数据迁移

如需进行数据库迁移，请参考 `migrate/*.py` 脚本：

```powershell
# 初始化/升级社区表结构（幂等，多次执行安全）
python migrate/add_community_tables.py
python migrate/add_community_posts.py
```

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
| uploads_subdir    | `UPLOADS_SUBDIR`       | `uploads`                        | 通用附件子目录（相对 `static_dir`） |
| uploads_url_prefix| `UPLOADS_URL_PREFIX`   | `/static/uploads`                | 通用附件 URL 前缀 |
| max_upload_size   | `MAX_UPLOAD_SIZE`      | `20971520`                       | 通用附件大小上限（字节，默认 20MB） |
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

以下命令均在 `backend/` 目录下执行：

```powershell
# 使用 uv 运行（推荐）
uv run pytest -q
uv run coverage run -m pytest
uv run coverage html  # 生成 html 覆盖率报告

# 或使用 pip/pytest 运行
pip install .[test]
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

手动运行代码检查（在仓库根目录执行）：

```shell
pre-commit run --all-files
```

### 项目结构

```
FinancialCareerCommunity/
├── backend/                # 后端 VocaStar（FastAPI）
│   ├── app/                # 应用主目录
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据库模型
│   │   ├── repositories/   # 数据访问层
│   │   ├── schemas/        # Pydantic 模型
│   │   ├── services/       # 业务逻辑层
│   │   └── main.py         # 应用入口
│   ├── assets/             # 静态数据文件
│   ├── scripts/            # 工具脚本
│   ├── migrate/            # 数据库迁移脚本
│   ├── tests/              # 测试文件
│   ├── docs/               # 后端文档
│   ├── Dockerfile          # 后端 Docker 镜像
│   └── pyproject.toml      # Python 项目配置
├── frontend/               # 前端 CareerVoyage（Vue 3 + Vite）
│   ├── src/                # 前端源码
│   ├── public/             # 静态资源
│   └── vite.config.js      # Vite 配置
├── docker-compose.yml      # Docker 编排
└── README.md
```

## 🤝 贡献

欢迎贡献代码！请查看 [贡献指南](./CONTRIBUTING.md) 了解详情。

## 📝 许可证

本项目采用 [MIT License](./LICENSE) 许可证。

数据来源:

- 职业数据: [O*Net Web Services](https://services-beta.onetcenter.org/), [学职平台](https://xz.chsi.com.cn/home.action)
- 职业头图: [Pexels](https://www.pexels.com/zh-cn/)