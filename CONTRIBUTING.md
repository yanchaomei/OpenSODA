# 贡献指南

感谢您对 OpenSource Copilot 项目的关注！我们欢迎各种形式的贡献。

## 🤝 如何贡献

### 报告问题

如果您发现了 Bug 或有功能建议，请通过 Issues 提交：

1. 先搜索是否已存在相关 Issue
2. 使用提供的 Issue 模板
3. 提供尽可能详细的信息

### 提交代码

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### Commit 规范

我们遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

Type 类型：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

示例：
```
feat(agent): add new diagnosis rules for community health
fix(api): fix streaming response encoding issue
docs(readme): update installation instructions
```

## 🛠️ 开发环境设置

### 后端开发

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖

# 运行测试
pytest

# 代码格式化
black .
isort .

# 类型检查
mypy .
```

### 前端开发

```bash
cd frontend
npm install

# 开发模式
npm run dev

# 代码检查
npm run lint

# 类型检查
npm run type-check
```

## 📋 代码规范

### Python

- 使用 Black 格式化代码
- 使用 isort 排序 imports
- 遵循 PEP 8 规范
- 添加类型注解
- 编写 docstring

### TypeScript/Vue

- 使用 ESLint + Prettier
- 使用 Composition API
- 组件使用 `<script setup>` 语法
- Props 和 Emits 需要类型定义

## 📝 文档

- 更新代码时同步更新相关文档
- API 变更需更新 API 文档
- 新功能需在 README 中说明

## ⚖️ 行为准则

请阅读并遵守我们的 [行为准则](CODE_OF_CONDUCT.md)。

## 📄 许可证

提交贡献即表示您同意将您的代码按照 Apache 2.0 许可证开源。

---

如有任何问题，请随时联系维护者。再次感谢您的贡献！

