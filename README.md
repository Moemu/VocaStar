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
uv run app.main:app --reload
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
| `/api/user/setprofile`    | POST | 设置用户信息     |
| `/api/user/testrecords`   | GET  | 获取用户测评结果 |
| `/api/user/addtestrecord` | POST | 记录测评结果     |

**教务系统相关(由于上游API原因暂不可用)**

| API                | 方法   | 说明                     |
| ------------------ | ------ | ------------------------ |
| `/api/jwxt/info`   | GET    | 获取教务系统中的所有信息 |
| `/api/jwxt/bind`   | POST   | 绑定教务系统             |
| `/api/jwxt/sync`   | POST   | 从教务系统同步数据       |
| `/api/jwxt/unbind` | DELETE | 解绑教务系统账号         |

**🚧 计划中/开发中**


**信息内容相关**

| API               | 方法 | 说明               |
| ----------------- | ---- | ------------------ |
| `/api/job/hot`    | GET  | 获取目前的热门岗位 |
| `/api/job/search` | POST | 搜索岗位           |

**AI相关**

| API                   | 方法      | 说明         |
| --------------------- | --------- | ------------ |
| `/api/ai/completions` | SSE       | 流式调用 LLM |
| `/api/ai/voice-chat`  | WebSocket | 语音交互     |