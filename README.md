# FinancialCareerCommunity Backend

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Black CodeStyle](https://img.shields.io/badge/Code%20Style-Black-121110.svg)
![wakatime](https://wakatime.com/badge/user/637d5886-8b47-4b82-9264-3b3b9d6add67/project/d6391b48-7f4e-46ad-94f1-34221f72a2ed.svg)
[![Test and Coverage](https://github.com/Moemu/FinancialCareerCommunity/actions/workflows/pytest.yaml/badge.svg)](https://github.com/Moemu/FinancialCareerCommunity/actions/workflows/pytest.yaml)
![coverage](./src/coverage.svg)

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

**运行**

```shell
uv run python -m app.main
```

或者

```shell
python -m app.main
```

## API 文档

默认本地 FastAPI 文档: <http://127.0.0.1:8080/docs>

APIFox 文档: <https://2v5c0iiid5.apifox.cn/>

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

| API                     | 方法 | 说明                                 |
| ----------------------- | ---- | ------------------------------------ |
| `/api/career`           | GET  | 分页获取职业列表，支持维度与关键词筛选 |
| `/api/career/featured`  | GET  | 获取推荐职业列表，可按维度过滤         |
| `/api/career/{careerId}`| GET  | 获取指定职业的详细信息                 |



**🚧 计划中/开发中**

...

## 导入数据

测评题库数据与职业信息分别存放于 `assets\quizzes.yaml`、`assets\careers.yaml`，可根据需要修改。

运行以下脚本以导入对应数据：

```shell
uv run scripts\import_quiz_from_yaml.py
uv run scripts\import_careers_from_yaml.py
```

## 数据库重置

删除项目根目录下的 `database.db` 即可。

## 在容器中构建

在项目根目录中创建 `app/data` 目录，用于容器存储数据库数据

在项目根目录中创建 `.env` 文件

`.env` 的写法可参考: [config.py](https://github.com/Moemu/FinancialCareerCommunity/blob/main/app/core/config.py)

添加一个可持久化的 SQLite 数据库配置:

```env
DATABASE_URL="sqlite+aiosqlite:///app/data/database.db"
```

构建容器:

```shell
docker volume create financial-career-data
docker build -t fcc .
```

启动容器:

```shell
docker run -d --name fcc-app \
  -p 8080:8080 \
  --env-file ./.env \
  -v financial-career-data:/app/data \
  fcc
```