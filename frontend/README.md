# CareerVoyage

CareerVoyage 是职业规划与测评平台 [VocaStar](../README.md) 的 Web 前端，基于 Vue 3 + Vite 构建的单页应用（SPA），提供职业探索、个性化测评、Cosplay 剧本体验、学习社区等功能界面。

## ✨ 技术栈

- **框架**：Vue 3.5 + Vue Router 4
- **构建**：Vite 7
- **UI 组件**：Element Plus 2.11（unplugin 自动按需导入）+ @element-plus/icons-vue
- **图表**：ECharts 6
- **状态管理**：Pinia 3 + pinia-plugin-persistedstate（持久化）
- **网络请求**：Axios
- **样式**：Tailwind CSS 4 + Sass

## 📋 环境要求

- Node.js `^20.19.0 || >=22.12.0`
- [pnpm](https://pnpm.io/)（推荐通过 `corepack enable` 启用，或 `npm i -g pnpm`）
- 运行中的 VocaStar 后端服务（见[仓库根 README](../README.md)，默认 `http://127.0.0.1:8080`）

## 🚀 快速开始

```shell
# 1. 安装依赖
pnpm install

# 2. 配置环境变量（默认留空即可，走同源相对路径）
cp .env.example .env

# 3. 启动开发服务器
pnpm dev
```

打开 <http://localhost:5173> 即可访问。

> 💡 开发模式下，`/api` 与 `/static` 请求由 Vite dev server 自动代理到 `http://127.0.0.1:8080`，前端代码全部使用相对路径，无需修改后端地址。请确保后端已启动并完成数据导入。

### 构建与预览

```shell
# 生产构建（产物输出到 dist/）
pnpm build

# 本地预览构建产物
pnpm preview
```

## ⚙️ 环境变量

| 变量 | 默认值 | 说明 |
| ---- | ------ | ---- |
| `VITE_API_BASE_URL` | 空（同源） | 后端 API 根地址。本地开发留空即可；生产部署前后端不同域时必填 |

## 📁 目录结构

```
frontend/
├── public/              # 静态资源（favicon 等）
├── src/
│   ├── apis/            # API 请求模块（user/quiz/career/cosplay/community...）
│   ├── assets/          # 样式与图片资源
│   ├── components/      # 通用组件
│   ├── router/          # 路由配置
│   ├── stores/          # Pinia 状态仓库
│   ├── utils/           # 工具函数（axios 实例等）
│   ├── views/           # 页面视图（Home/Login/Evaluation/Career/Comunity/Cosplay...）
│   ├── App.vue          # 根组件
│   └── main.js          # 应用入口
├── index.html           # HTML 模板
├── vite.config.js       # Vite 配置（代理、自动导入、别名）
└── package.json
```

## 🧩 推荐 IDE

[VS Code](https://code.visualstudio.com/) + [Vue (Official)](https://marketplace.visualstudio.com/items?itemName=Vue.volar) 扩展（请禁用 Vetur）。
