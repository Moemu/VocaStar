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
| `/api/user/profile`       | POST | 设置用户信息     |
| `/api/user/avatar`        | POST | 上传用户头像     |

**测评（Quiz）相关**

| API                  | 方法 | 说明                         |
| -------------------- | ---- | ---------------------------- |
| `/api/quiz/start`    | POST | 创建/获取测评会话            |
| `/api/quiz/questions`| GET  | 获取题目与当前作答状态       |
| `/api/quiz/answer`   | POST | 保存作答                     |
| `/api/quiz/submit`   | POST | 提交测评并生成报告           |
| `/api/quiz/report`   | GET  | 查看已生成的测评报告与推荐   |

## 职业推荐数据准备

测评报告会依据数据库中的职业数据实时生成推荐，请在运行前确保以下表已填充：

### `careers`

- **必填字段**：
	- `name`：职业名称，例如“数据分析师”。
	- `code`：唯一编码，方便运营/导入，例如 `I001`。
	- `holland_dimensions`：JSON 数组，声明职业适配的霍兰德维度，如 `["I", "C"]`。
- **建议补充**：`description`、`work_content`、`career_outlook`、`development_path` 等，可提升推荐理由质量。
- 可通过手工录入或编写脚本导入，示例 SQL：

	```sql
	INSERT INTO careers (name, code, holland_dimensions, description)
	VALUES (
		'数据分析师',
		'I001',
		'["I", "C"]',
		'通过数据洞察支持业务决策。'
	);
	```

### `career_tags` 与 `career_tag_relations`

- 若需要在前端展示职业标签，可预先创建标签（如“热门”“科技行业”），并在关联表中关联到对应职业。
- 当前推荐逻辑未直接使用标签，但完善后能支持更多筛选维度。

### 自动生成的数据

- `quiz_reports`：在用户完成测评并提交后自动写入，无需手动准备。
- `career_recommendations`：测评提交时会基于上述职业数据生成并落库，用于后续查询报告。

填充完职业数据后，可运行一次完整测评流程，确认返回的推荐列表与 `career_recommendations` 表中的记录一致。

**🚧 计划中/开发中**

...