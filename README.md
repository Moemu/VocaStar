# FinancialCareerCommunity Backend

别急，还没开始写.

## 快速开始

要求:

- [uv](https://docs.astral.sh/uv/)
- `Python > 3.11`

**安装依赖:**

```shell
uv sync
```

或者：

```shell
pip install .
```

<!-- ## 文件树结构 -->

<!-- ```
FinancialCareerCommunity/
├── app/                                # 主要的应用代码目录
│   ├── __init__.py
│   ├── main.py                         # FastAPI 应用入口文件
│   │
│   ├── api/                            # API 路由层
│   │   ├── __init__.py
│   │   └── v1/                         # API 版本 v1
│   │       ├── __init__.py
│   │       ├── api.py                  # 聚合所有 v1 版本的路由
│   │       └── endpoints/              # 各功能模块的路由文件
│   │           ├── __init__.py
│   │           ├── users.py            # 用户系统 (注册, 登录, 个人主页)
│   │           ├── assessments.py      # 职业测评系统
│   │           ├── careers.py          # 职业地图 (行业图谱, 岗位)
│   │           ├── plans.py            # 路径规划
│   │           ├── information.py      # 信息聚合 (招聘, 实习)
│   │           ├── community.py        # 社区与互动 (论坛, 内推)
│   │           └── services.py         # 工具与服务 (简历, 面试题库)
│   │
│   ├── core/                           # 核心配置与功能
│   │   ├── __init__.py
│   │   ├── config.py                   # 应用配置 (环境变量, 密钥等)
│   │   └── security.py                 # 安全相关 (密码哈希, JWT令牌)
│   │
│   ├── crud/                           # CRUD (Create, Read, Update, Delete) 数据库操作
│   │   ├── __init__.py
│   │   ├── base.py                     # CRUD 基类
│   │   ├── crud_user.py                # 用户的 CRUD 操作
│   │   ├── crud_assessment.py          # 测评的 CRUD 操作
│   │   └── ...                         # 其他模型的 CRUD 文件
│   │
│   ├── db/                             # 数据库相关
│   │   ├── __init__.py
│   │   ├── base.py                     # ORM 模型基类 (DeclarativeBase)
│   │   └── session.py                  # 数据库会话管理
│   │
│   ├── models/                         # ORM 数据模型 (对应数据库表)
│   │   ├── __init__.py
│   │   ├── user.py                     # 用户模型
│   │   ├── assessment.py               # 测评结果模型
│   │   ├── career_path.py              # 职业路径模型
│   │   ├── post.py                     # 社区帖子模型
│   │   └── ...                         # 其他数据模型
│   │
│   ├── schemas/                        # Pydantic 数据校验模型 (用于 API 请求和响应)
│   │   ├── __init__.py
│   │   ├── user.py                     # 用户相关的 Schema
│   │   ├── token.py                    # Token Schema
│   │   ├── assessment.py               # 测评相关的 Schema
│   │   └── ...                         # 其他功能模块的 Schema
│   │
│   └── services/                       # 业务逻辑层
│       ├── __init__.py
│       ├── authentication_service.py   # 用户认证服务
│       ├── assessment_service.py       # 测评业务逻辑
│       └── web_scraper_service.py      # 网页爬虫服务 (用于信息聚合)
│
├── tests/                              # 测试目录
│   ├── __init__.py
│   ├── conftest.py                     # Pytest 配置文件
│   └── test_api/                       # API 测试
│       └── v1/
│           └── test_users.py           # 用户相关的 API 测试
│
├── .env                                # 环境变量文件 (示例)
├── .gitignore                          # Git 忽略文件
├── alembic.ini                         # Alembic 数据库迁移工具配置
├── alembic/                            # Alembic 迁移脚本目录
├── prestart.sh                         # (可选) 启动前运行的脚本, 如执行数据库迁移
└── requirements.txt                    # Python 依赖包列表
``` -->