# VocaStar 贡献指南

## 报告问题

VocaStar 目前仍然处于早期开发状态，暂未有提交正式版的想法，因此部分功能可能存在问题并导致服务不稳定。如果你在使用过程中发现问题并确信是由 VocaStar 运行框架引起的，请务必提交 Issue

## 提议新功能

VocaStar 还未进入正式版，欢迎在 Issue 中提议要加入哪些新功能， Maintainer 将会尽力满足大家的需求

## Commit 规范

VocaStar 使用 [gitmoji](https://gitmoji.dev/) 作为主 commit 规范

> 📝 更新 Commit 规范

当然，我们也欢迎 [Angular 规范](https://github.com/angular/angular/blob/main/contributing-docs/commit-message-guidelines.md)

> docs: 更新 Commit 规范

无论使用何种 Commit 规范，请确保每一个 Commit 只代表**一个**意图，并清晰地描述其目的。

包含诸如 `fixed`、`update`、`change` 等无法清晰表达修改意图的 commit 信息的合并请求将被拒绝。

## Pull Request

VocaStar 使用 pre-commit 进行代码规范管理，因此在提交代码前，我们推荐安装 pre-commit 并通过代码检查：

```shell
pip install .[test]

pre-commit install
```

目前代码检查的工具有：flake8 PEP风格检查、mypy 类型检查、black 风格检查，使用 isort 和 trailing-whitespace 优化代码

在本地运行 pre-commit 不是必须的，尤其是在环境包过大的情况下，但我们还是推荐您这么做

代码提交后请静待工作流运行结果，若 pre-commit 出现问题请尽量先自行解决后再次提交

## 强制类型注解

提交的代码必须含有清晰的类型注解并通过类型检查器检查。对于类型不清晰的提交，维护者可能不予合并。
