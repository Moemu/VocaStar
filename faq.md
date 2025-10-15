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
