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

## 5. 数据与存储

- 关系模型集中于 `app/models`：
  - 用户、积分、成就类表保障激励系统。
  - 測评相关表关联报告、推荐、答题记录。
  - 职业生态通过 `career_galaxies` → `careers` → `career_recommendations` 联动。
- 数据导入脚本（`scripts/import_*.py`）从 YAML 初始化职业、测评与 Cosplay 数据。
- Redis 支持会话缓存、黑名单与潜在的排行榜等实时数据诉求。

## 6. 配置与运维

- `app/core/config.py` 提供环境变量覆盖能力，按 dev/prod 切换日志级别、CORS 等。
- Docker 化：`Dockerfile` + `docker-compose.yml` 支持一键部署，持久化数据放置于 `app/data`。
- `uv` 辅助命令统一开发、部署脚本执行。
- 迁移策略：
  1. 首选 Alembic（如 FAQ 所述）或使用提供的脚本执行增量变更。
  2. 积分与签到逻辑事务性更新，确保数据一致性。

## 7. 质量保障

- 测试框架：`pytest` + `pytest-asyncio`。`tests/database.py` 使用内存 SQLite 初始化 schema。
- 新增测试 `tests/test_home.py` 验证首页聚合：
  - 首次访问触发签到并写入积分流水。
  - 同日重复访问不会重复奖励。
- Pipeline：GitHub Actions 运行 `pytest` 与覆盖率统计（见 README 徽章）。
- 类型与风格：`mypy`、`black`、`isort`、`flake8` 通过 pre-commit 管理。

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

## 10. 未来规划

1. **职业星球解锁逻辑**：HomeService 中的 TODO，将根据用户积分或进度解锁新星球。
2. **积分体系扩展**：增加更多任务、限时活动，与前端协作形成任务中心。
3. **个性化推荐增强**：结合 LLM 输出更具说服力的职业理由，并支持多维度过滤。
4. **迁移框架正规化**：引入 Alembic，全量管理迁移历史及回滚策略。
5. **监控与告警**：接入 Prometheus + Grafana 或 APM，实现接口耗时与错误率监控。