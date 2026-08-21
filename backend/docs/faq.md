# VocaStar FAQ

## 1. 架构定位与业务流程
- **整体链路**：前端通过 `/api/auth/login` 提交凭证，FastAPI 服务使用 `authenticate_user` 校验密码并签发 JWT。客户端在后续请求中附带 Bearer Token，例如访问 `/api/quiz/start` 初始化测评会话。测评过程中 `/api/quiz/questions` 拉取题目、`/api/quiz/answer` 持久化作答，完成后 `/api/quiz/submit` 聚合答案生成报告并写入 `quiz_reports`，同时挑选匹配的职业推荐返回给前端。
- **模块边界**：`app/api` 暴露路由，`services` 封装业务流程（用户、测评、职业、Cosplay、LLM 等），`repositories` 负责数据库读写，`schemas` 负责请求响应模型。模块间通过显式依赖注入互通，彼此耦合度低，方便后续拆分。
- **扩展策略**：当前为单体 FastAPI 应用，但已经将核心域拆成独立 service/repository。若需要服务化，可将测评、职业、用户等服务拆为独立进程，共享身份认证中心与消息总线，同时通过 API Gateway 或服务网格实现统一入口与流量治理。

## 2. 数据库与模型设计
- **核心表关系**：`users` 一对一 `user_profiles`，一对多 `quiz_submissions` 和 `cosplay_sessions`；`quizzes` 一对多 `questions`，后者再关联 `options`；`quiz_submissions` 关联 `quiz_answers` 与唯一的 `quiz_reports`；`quiz_reports` 与 `career_recommendations` 多对一；`careers` 归属 `career_galaxies`。Cosplay 侧由 `cosplay_scripts` 与 `cosplay_sessions`、`cosplay_reports` 组成闭环。
- **链路建模**：测评答案存储在 `quiz_answers`，支持单选、多选、打分、滑块等多种类型，`extra_payload` JSON 字段承载扩展数据（例如滑块题分布）。报告生成时会统计维度得分并写入 `quiz_reports.result_json`，属于合理冗余，避免重复计算。
- **索引与优化**：模型层对用户名、邮箱、题目顺序、提交时间等关键字段建有索引。若并发增长，可考虑将会话与答案表做时间分区或基于用户做分片，读写分离可以通过 AsyncSQLAlchemy + 读写路由器实现。
- **迁移策略**：目前通过脚本初始化 SQLite，生产建议采用 Alembic 维护迁移脚本，遵循“先兼容写入、再清理旧字段”的两步法，保证线上数据安全演进。

## 3. 性能与扩展性
- **异步能力**：全链路使用 `AsyncSession` 与 async SQLAlchemy 驱动，配合 FastAPI 的异步路由处理，能够高效处理 IO 密集型场景。
- **潜在瓶颈**：热点集中在测评提交和报告生成，若同步生成耗时，建议将报告计算挪至后台队列（Celery、RQ 或 FastAPI BackgroundTask），前端轮询或通过 WebSocket 推送结果。
- **缓存与 Redis**：现阶段 Redis 主要用于 JWT 黑名单。可以进一步缓存职业/题库数据、排行榜等热点，或用作 Session/限流计数器，降低数据库压力。
- **容错与限流**：LLM 服务调用封装了超时与配置检查，可在外层增加重试与熔断。全局层面可结合 API Gateway、令牌桶限流以及任务排队策略保障高峰期稳定。
- **水平扩展**：应用无状态，可通过容器编排横向扩容，前置负载均衡（NGINX、ALB 等）。数据库可采用云托管或主从架构，Redis 升级为哨兵或集群提升可用性。

## 4. 安全与权限
- **JWT 策略**：使用 HS256 签名，默认过期 720 分钟，可通过配置缩短；`add_token_to_blacklist` 在登出或密码重置时将 JTI 写入 Redis 阻断复用。
- **防护措施**：密码存储采用 bcrypt 哈希，上传头像限定 Content-Type、扩展名与 2MB 大小，并在写盘时校验路径防止遍历。日志使用定制 logger，避免输出明文密码或 token。
- **权限设计**：目前区分普通用户与管理员角色（`UserRole`），后续可基于角色扩展更细粒度的 RBAC。接口层依赖装饰器 `get_current_user` / `get_current_user_optional` 实现访问控制。
- **通用安全**：所有输入通过 Pydantic 验证，ORM 查询绑定参数预防 SQL 注入，可在 API Gateway 或 WAF 配置 CSRF/XSS/滥用防护策略。

## 5. 异常处理与监控
- **错误兜底**：服务端对常见业务错误返回标准 HTTP 状态（401/403/404/422 等），意外错误会被 FastAPI 全局异常处理捕获并记录。
- **监控计划**：当前主要依赖日志与 GitHub Actions 报告，生产建议引入 Prometheus + Grafana 或 Sentry/ELK 采集接口耗时、错误率与资源指标，实现阈值告警。
- **可用性**：支持通过容器健康检查发现异常实例并自动重启。对于外部依赖（数据库、Redis、LLM）应增加心跳检测与降级策略，例如 Redis 不可用时跳过黑名单校验并追加警报。

## 6. 接口设计与文档
- **REST 风格**：路由遵循资源 + 动词组合（`/api/career`, `/api/quiz/submit`），使用相应 HTTP 方法，响应体采用 Pydantic schema，错误返回 JSON 含 detail 字段。
- **文档体系**：FastAPI 原生提供 Swagger UI 与 ReDoc，仓库中还托管了 APIFox 文档，便于对接方查看。可通过 CI 自动导出 OpenAPI JSON 供前端或第三方使用。
- **版本管理**：目前统一在 `/api` 前缀下，后续升级可采用 `/api/v1`、`/api/v2` 并行策略或使用 Header 协商，逐步迁移客户端。

## 7. 测试与质量保障
- **测试覆盖**：`tests/` 中包含测评、职业、Cosplay 等模块的单测，GitHub Actions 执行 pytest + coverage，`coverage.svg` 提供可视化指标。
- **静态检查**：项目启用 black、isort、flake8、mypy 与 pre-commit，CI 自动校验风格与类型，保障提交质量。
- **扩展策略**：新增功能时应同步补充单测/集成测试，重点覆盖测评评分边界、职业推荐算法、Cosplay 状态流转等关键路径；可考虑引入 API contract 测试或 E2E 测试确保端到端稳定。

## 8. 部署与运维
- **部署方式**：提供 Dockerfile 与 docker-compose，构建阶段分层安装依赖，运行阶段使用非 root 用户并挂载数据卷。可扩展至 K8s，通过 ConfigMap/Secret 注入环境变量。
- **多环境管理**：`Config` 支持读取 `.env`，区分 dev/prod；未来可在 `pyproject` 或 CI 中注入环境变量，结合密钥管理服务托管敏感信息。
- **运维要点**：滚动升级可借助容器编排完成蓝绿或金丝雀发布；日志可输出到 STDOUT，再由集中式日志系统采集；建议为数据库和 Redis 配置主从、定期备份与灾备脚本。

## 9. 扩展方向与瓶颈
- **潜在功能**：社交互动、排行榜、多租户、国际化都可基于当前模块化架构扩展。题库与职业数据可替换为后台 CMS 驱动，提供版本审核。
- **AI 能力**：`LLMService` 已封装 OpenAI 兼容接口，可继续扩展为智能报告或对话助手，需关注速率限制、提示注入与成本控制。
- **技术债**：当前缺乏后台任务队列、分布式缓存策略、细粒度权限控制与完善监控。首要优化方向是引入任务队列处理报告、完善缓存层、搭建监控告警链路，并补齐迁移与配置管理流程。

## 10. 快速回答要点速查表
| 常见问题 | 核心回答要点 |
| --- | --- |
| 为什么选 FastAPI 异步架构？ | IO 密集型场景吞吐高、类型提示友好、内置 OpenAPI，结合 AsyncSession 有助于提升并发能力。 |
| 题库/职业数据如何维护？ | 现阶段通过 YAML + 导入脚本，计划引入后台 CMS 或直接转数据库管理并加审批流程。 |
| 报告生成耗时怎么办？ | 引入异步任务队列后台生成，配合轮询或推送通知；对常见报告使用缓存或预计算。 |
| Redis 扮演什么角色？ | 目前用于 JWT 黑名单，后续可扩展缓存、限流、排行榜、会话存储等用途。 |
| 如何防止恶意刷测评？ | 在网关侧做限流、验证码、人机验证；后端对敏感接口增加速率限制与行为监控。 |
| JWT 如何刷新与失效？ | 设置较短访问令牌 + 刷新令牌，登出与重置时写入黑名单，并支持周期性轮换密钥。 |
| API 如何演进版本？ | 采用 URI 版本号或 Header 协商，保证旧版本稳定一段时间，逐步迁移客户端。 |
| 监控与日志方案？ | 使用结构化日志结合集中收集，推荐接入 Prometheus/Grafana 或 Sentry/ELK 追踪异常。 |
| 数据库/Redis 故障如何降级？ | 建议部署主从集群，代码层做超时重试与降级逻辑，必要时只提供核心读操作。 |
| 下一步优化重点？ | 引入后台任务队列、完善缓存、建设监控告警与权限体系，补齐运维与大规模部署能力。 |

## 11. 新增功能与常见问题补充（社区 / 上传 / 导师 / 个人中心）

| 问题 | 说明 |
| --- | --- |
| 社区附件上传 413 是什么含义？ | 请求体大小超过 `config.max_upload_size`（字节）限制，被服务器拒绝；应在前端做预检并提示用户压缩或拆分。 |
| 为什么收到 422（附件类型错误）？ | 上传的 `type` 不在白名单 {image, document, video, pdf, code}，或缺失必须字段；需修正后重试。 |
| URL 附件标题如何获取？ | 发布帖子时如果附件类型为 `url` 且未提供标题，服务尝试抓取页面 `<title>`，失败则留空；该网络调用标记 `no-cover`。 |
| Mentors 域（domain）是如何创建的？ | 搜索或绑定过程中如果域名不存在会自动 ensure（幂等创建），避免手动同步。 |
| 学习伙伴推荐列表如何生成？ | 基于基础筛选 + 去重逻辑，优先展示与用户技能或历史交互相关项，其余使用回填保证列表长度。 |
| 个人中心的 Wrongbook 有何作用？ | 记录用户测评或练习中的错题，供复习与能力跟踪；未来可用于自适应题库推荐。 |
| 个人中心的 Favorites 如何维护？ | 收藏与取消操作写入独立关联表，查询时聚合返回职业/帖子收藏集合。 |
| LLM 功能未配置会怎样？ | `LLMService` 检测缺失 API Key 或禁用开关时自动降级：跳过调用，返回占位描述或空增强字段，不影响主流程。 |
| 为什么部分函数标记 `# pragma: no cover`？ | 包含外部网络请求（不稳定）、无限循环或守护线程（队列 worker）、价值有限的启动流程；减少测试脆弱点。 |
| Holland 报告队列为何不做单元测试？ | 其生命周期涉及长时间阻塞与并发调度，单测 ROI 低；建议以集成/E2E 验证最终一致性与可靠性。 |
| 上传目录为何按年/月分桶？ | 降低单目录文件数，便于备份与清理；路径结构为 `static/uploads/YYYY/MM/<uuid>.<ext>`。 |
| 如何避免重复探索记录？ | 个人中心使用 upsert（存在则更新）策略，防止重复插入同一探索对象。 |


# 后端技术说明文档

## 1. 总览

- **项目定位**：面向高校学生的职业探索与测评服务，提供职业推荐、能力分析、每日积分激励以及 Cosplay 式职业体验。
- **核心目标**：以数据驱动的方式帮助用户了解自身优势，建立成长路径，并通过游戏化机制提升平台活跃度。
- **实现概况**：基于 FastAPI 的异步服务，结合 SQLAlchemy ORM、Redis 缓存、Pydantic 模型与 JWT 鉴权，形成可扩展的业务分层架构。

## 2. 技术栈与基础设施

| 层级       | 选型                    | 说明                                     |
| ---------- | ----------------------- | ---------------------------------------- |
| Web 框架   | FastAPI                 | 提供异步 REST API，内置 OpenAPI 文档生成 |
| ORM        | SQLAlchemy 2.0 (Async)  | 统一数据模型定义，支持 SQLite/PostgreSQL |
| 配置       | pydantic-settings       | 环境变量驱动配置，便于部署差异化         |
| 鉴权       | JWT (PyJWT)             | 登录认证、权限校验、过期控制             |
| 缓存/队列  | Redis                   | 存放会话、临时数据，预留扩展空间         |
| 前后端通信 | JSON + REST             | 所有响应使用 Pydantic 模型序列化         |
| 静态部署   | Docker / docker-compose | 提供容器化部署脚本                       |
| 开发工具   | uv                      | 快速创建隔离的 Python 环境               |

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
