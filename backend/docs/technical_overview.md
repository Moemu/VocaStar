# 后端技术说明文档

## 1. 总览

- **项目定位**：面向高校学生的职业探索与测评服务，提供职业推荐、能力分析、每日积分激励以及 Cosplay 式职业体验。
- **核心目标**：以数据驱动的方式帮助用户了解自身优势，建立成长路径，并通过游戏化机制提升平台活跃度。
- **实现概况**：基于 FastAPI 的异步服务，结合 SQLAlchemy ORM、Redis 缓存、Pydantic 模型与 JWT 鉴权，形成可扩展的业务分层架构。

## 2. 技术栈与基础设施

| 层级 | 选型 | 说明 |
| ---- | ---- | ---- |
| Web 框架 | FastAPI | 提供异步 REST API，内置 OpenAPI 文档生成 |
| ORM | SQLAlchemy 2.0 (Async) | 统一数据模型定义，支持 SQLite/PostgreSQL |
| 配置 | pydantic-settings | 环境变量驱动配置，便于部署差异化 |
| 鉴权 | JWT (PyJWT) | 登录认证、权限校验、过期控制 |
| 缓存/队列 | Redis | 存放会话、临时数据，预留扩展空间 |
| 前后端通信 | JSON + REST | 所有响应使用 Pydantic 模型序列化 |
| 静态部署 | Docker / docker-compose | 提供容器化部署脚本 |
| 开发工具 | uv | 快速创建隔离的 Python 环境 |

## 3. 系统架构

```
┌──────────────────────────────────────┐
│               FastAPI               │
│   ┌────────────┬────────────┬──────┐ │
│   │   auth     │   quiz     │home  │ │
│   │   career   │ cosplay    │user  │ │
│   └────────────┴────────────┴──────┘ │
│         ↕依赖注入 / Pydantic↕        │
└──────────────────────────────────────┘
             │ AsyncSession
┌──────────────────────────────────────┐
│          SQLAlchemy ORM              │
│ models/*.py 映射职业、测评、积分等结构 │
└──────────────────────────────────────┘
             │
    SQLite / PostgreSQL + Redis
```

- **分层策略**：`api` 路由负责协议与校验，`services` 聚焦业务编排，`repositories` 面向持久化操作，`schemas` 统一输入输出模型。
- **依赖注入**：通过 FastAPI `Depends` 提供数据库会话、登录用户与配置，一致性强、便于测试。
- **异步执行**：全链路采用 `AsyncSession`，提升并发处理能力。

## 4. 核心模块

### 4.1 用户与鉴权

- `app/api/auth.py` 暴露注册、登录、登出接口，支持 JWT 令牌签发与黑名单机制。
- `app/services/auth_service.py` 负责密码哈希、令牌生成、刷新机制，并与 Redis 集成管理黑名单。
- 用户角色（`UserRole`）支持 admin/user，便于扩展后台权限。

### 4.2 首页聚合与每日签到

- `HomeService.get_home_summary` 汇聚测评报告、能力分布、每日积分、职业推荐。
- 首次访问触发 `_ensure_daily_sign_in` 自动签到：
  - 检查 `point_transactions` 是否已有当天 `cover` 记录。
  - 若未签到，创建积分账户（`user_points`）并写入 `_SIGN_IN_POINTS` 积分流水。
  - 更新响应中的 `PointEntry(task="每日签到", status="已完成")`。
- 积分统计 `_get_today_points` 计算当日总积分并标记主要任务完成度（签到、职业测评）。
- 推荐逻辑 `_get_recommendations` 优先使用最近测评报告的匹配结果，缺口采用随机推荐补齐。

### 4.3 职业测评系统

- 支持多题型答题流程：场景判断、兴趣偏好、价值排序等（见 `app/schemas/quiz.py`）。
- `quiz_service` 处理会话创建、答题保存、提交评分与报告生成：
  - `QuizRecommendation` 结合职业维度得分推荐职位。
  - 完成后奖励固定积分，并写入职业推荐记录供首页复用。
- Pydantic 架构使用 Discriminator 确保题型与答案格式匹配，防止类型歧义。

### 4.4 职业探索模块

- `career.py` 定义职业、星系、推荐表结构，适配 `assets/careers.yaml` 导入数据。
- `CareerService` 提供分页、筛选、职业星球探索等 API，以星系维度展示职业生态。
- 新增 `cover` 字段用于职业介绍封面图，数据库迁移通过
  - SQL 脚本：`docs/migrations/20250117_add_cover_column_to_careers.sql`。
  - Python 脚本：`scripts/migrate_add_career_cover.py` 自动检测并执行 `ALTER TABLE`。

### 4.5 Cosplay 剧本体验

- `cosplay` 相关模型描述职业模拟场景、会话状态与总结报告。
- `migrate_add_state_payload.py` 迁移脚本新增 `state_payload` 并回填默认模版，确保流程可继续。
- 服务层根据用户选择在 `cosplay_sessions` 中维护剧情进度与历史分支。

### 4.6 社区模块（群组/帖子/附件仓库）

- 领域拆分：`community_groups`（分类、群组、成员、点赞）、`community_posts`（帖子、评论、点赞、附件）、`repository`（资源库聚合视图）。
- 服务层：`PostService` 负责帖子流、附件聚合、URL 标题抓取与附件上传（类型白名单/大小限制/目录分区）。
- 关键约束：
  - 附件类型白名单：{image, document, video, pdf, code}
  - 文件大小：`config.max_upload_size`
  - 存储路径：`static/uploads/YYYY/MM/<uuid>.<ext>`；外链前缀 `config.uploads_url_prefix`
- 仓库视图：基于 `CommunityPostAttachment` 联合 `CommunityPost` 的发布时间构建资源仓库，支持按类型与群组筛选、分页；仅统计可下载类附件（document/video/pdf/code）。
- 网络不确定性隔离：URL 标题抓取 `_fetch_url_title` 依赖外部网络，已用 `# pragma: no cover` 标记排除覆盖率。

### 4.7 职业导师 与 学习伙伴

- 职业导师:
  - 搜索支持关键词 `q` 与技能 `skill` 过滤；
  - 领域（domain）按需自动创建/确保存在（idempotent）；
  - 返回导师基本资料与技能/领域标签。
- 学习伙伴:
  - 支持搜索/分页、绑定与解绑（用户-伙伴关系）；
  - 推荐列表结合基础规则与去重策略；
  - “我的伙伴”返回当前用户已绑定对象。

### 4.8 个人中心

- 汇总：最近测评、推荐、收藏与积分概览。
- Explorations：探索记录 upsert，避免重复；
- Favorites：职业/帖子收藏管理；
- Wrongbook：错题本记录与检索（便于复习与成长跟踪）。

## 5. 数据与存储

- 关系模型集中于 `app/models`：
  - 用户、积分、成就类表保障激励系统。
  - 測评相关表关联报告、推荐、答题记录。
  - 职业生态通过 `career_galaxies` → `careers` → `career_recommendations` 联动。
- 数据导入脚本（`scripts/import_*.py`）从 YAML 初始化职业、测评与 Cosplay 数据。
- Redis 支持会话缓存、黑名单与潜在的排行榜等实时数据诉求。

### 5.1 上传与静态资源

- 配置项：
  - `uploads_dir`：本地写入根目录（默认 `app/static/uploads`）。
  - `uploads_url_prefix`：对外可访问的 URL 前缀（默认 `/static/uploads`）。
  - `max_upload_size`：最大上传大小（字节）。
- 安全性：对扩展名做保留处理但文件名统一使用 UUID；拒绝不在白名单类型中的上传；超过大小返回错误。
- 目录分区：按年/月分桶，降低单目录文件数。

## 6. 配置与运维

- `app/core/config.py` 提供环境变量覆盖能力，按 dev/prod 切换日志级别、CORS 等。
- Docker 化：`Dockerfile` + `docker-compose.yml` 支持一键部署，持久化数据放置于 `app/data`。
- `uv` 辅助命令统一开发、部署脚本执行。
- 迁移策略：
  1. 首选 Alembic（如 FAQ 所述）或使用提供的脚本执行增量变更。
  2. 积分与签到逻辑事务性更新，确保数据一致性。

### 6.1 LLM 配置与降级

- `LLMService` 采用 OpenAI 兼容接口；当未配置或开关关闭时，相关功能自动降级为禁用模式（返回占位或跳过调用），避免对外部依赖的硬性耦合。

### 6.2 背景任务与报告队列

- Holland 报告生成可由后台队列异步处理，避免阻塞请求线程；
- 队列 worker 的生命周期循环、阻塞等待与处理流程标记为 `no-cover`，原因是：
  - 与 I/O、时间调度强相关，单测 ROI 低且易产生异步竞态；
  - 建议以集成/端到端方式验证。

## 7. 质量保障

- 测试框架：`pytest` + `pytest-asyncio`。`tests/database.py` 使用内存 SQLite 初始化 schema。
- 新增测试 `tests/test_home.py` 验证首页聚合：
  - 首次访问触发签到并写入积分流水。
  - 同日重复访问不会重复奖励。
- Pipeline：GitHub Actions 运行 `pytest` 与覆盖率统计（见 README 徽章）。
- 类型与风格：`mypy`、`black`、`isort`、`flake8` 通过 pre-commit 管理。

### 7.1 覆盖率策略与排除项

- 优先覆盖：
  - 业务关键路径（鉴权、测评评分、职业推荐、社区流转、上传校验）。
  - 边界/异常路径（无权限、参数校验失败、空数据、分页越界）。
- 排除（no-cover 合理性）：
  - 依赖外部网络或不稳定源（如 `_fetch_url_title`）。
  - 无限循环/守护线程（队列 worker 生命周期）。
  - 与框架强耦合且回归价值有限的启动管线。
- 原则：排除项须在代码与文档中显式标注，保持最小化与可审计。

## 8. 安全与合规

- JWT 认证，支持访问令牌刷新与黑名单退出。
- 密码存储使用 `bcrypt` 哈希；配置中默认密钥仅供开发，部署需替换。
- CORS 控制通过配置文件灵活调整；生产环境默认禁用 `*`。
- 日志采用 `colorlog`，敏感信息输出前做脱敏处理。

## 9. 性能与扩展性

- 全异步 I/O 保证在高并发下不会阻塞主线程。
- 数据访问集中在 service 层，可针对高频接口加入 Redis 缓存或异步任务处理。
- 积分、推荐等功能抽象成独立服务，易于拆分为微服务或接入消息队列。
- 预留 LLM 配置（`llm_api_*`），可无缝对接 OpenAI 兼容模型优化职业推荐说明。

### 9.1 社区时间线与资源库性能

- 时间线查询采用轻量聚合 + 批量查询作者/附件/评论预览，控制 N+1；
- 资源库基于 Attachment + Post 的连接查询，按创建时间倒序与类型过滤，分页限制避免大响应；
- 附件列表在渲染时做上限保护（如每帖最多显示前 50 个附件）。

## 10. 未来规划

1. **职业星球解锁逻辑**：HomeService 中的 TODO，将根据用户积分或进度解锁新星球。
2. **积分体系扩展**：增加更多任务、限时活动，与前端协作形成任务中心。
3. **个性化推荐增强**：结合 LLM 输出更具说服力的职业理由，并支持多维度过滤。
4. **迁移框架正规化**：引入 Alembic，全量管理迁移历史及回滚策略。
5. **监控与告警**：接入 Prometheus + Grafana 或 APM，实现接口耗时与错误率监控。