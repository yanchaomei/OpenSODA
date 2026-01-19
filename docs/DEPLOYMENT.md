# 🚀 部署指南

本文档介绍如何将 OpenSource Copilot 部署到云平台。

## 部署架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户浏览器                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│        Vercel (前端)     │        Railway (后端)              │
│   ┌─────────────────┐   │   ┌─────────────────────────┐     │
│   │   Vue 3 App     │───┼──▶│   FastAPI + LangGraph   │     │
│   │   (Static)      │   │   │   (Python)              │     │
│   └─────────────────┘   │   └─────────────────────────┘     │
│                         │                                    │
│   https://xxx.vercel.app│   https://xxx.railway.app         │
└─────────────────────────┴───────────────────────────────────┘
```

---

## 一、前端部署 (Vercel)

### 1.1 一键部署

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/YOUR_USERNAME/OpenSODA&root-directory=frontend)

### 1.2 手动部署

1. **注册/登录 Vercel**
   - 访问 https://vercel.com
   - 使用 GitHub 账号登录

2. **导入项目**
   ```bash
   # 安装 Vercel CLI
   npm i -g vercel
   
   # 在 frontend 目录执行
   cd frontend
   vercel
   ```

3. **配置环境变量**
   - `VITE_API_BASE_URL`: 后端 API 地址

4. **配置 Rewrites**

   在 `vercel.json` 中配置 API 代理：
   ```json
   {
     "rewrites": [
       {
         "source": "/api/:path*",
         "destination": "https://your-backend.railway.app/api/:path*"
       }
     ]
   }
   ```

---

## 二、后端部署 (Railway)

### 2.1 一键部署

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/YOUR_USERNAME/OpenSODA&root-directory=backend)

### 2.2 手动部署

1. **注册/登录 Railway**
   - 访问 https://railway.app
   - 使用 GitHub 账号登录

2. **创建项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择 OpenSODA 仓库

3. **配置环境变量**
   ```
   OPENAI_API_KEY=sk-xxx
   OPENAI_BASE_URL=https://api.openai.com/v1
   OPENAI_MODEL=gpt-4o
   CORS_ORIGINS=https://your-frontend.vercel.app
   ```

4. **配置启动命令**
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

---

## 三、环境变量配置

### 后端必需变量

| 变量名 | 描述 | 示例 |
|--------|------|------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | `sk-xxx` |
| `OPENAI_BASE_URL` | API 基础 URL | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | 使用的模型 | `gpt-4o` |
| `CORS_ORIGINS` | 允许的前端域名 | `https://xxx.vercel.app` |

### 后端可选变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `GITHUB_TOKEN` | GitHub API Token | - |
| `REDIS_URL` | Redis 连接 URL | - |
| `LOG_LEVEL` | 日志级别 | `INFO` |

---

## 四、本地 Docker 部署

### 4.1 使用 Docker Compose

```bash
# 1. 复制环境变量
cp .env.example .env

# 2. 编辑 .env 文件
vim .env

# 3. 启动服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f
```

### 4.2 访问地址

- 前端: http://localhost:3000
- 后端: http://localhost:8001
- API 文档: http://localhost:8001/docs

---

## 五、常见问题

### Q1: CORS 错误

**问题**: 前端请求后端时出现 CORS 错误

**解决**: 确保后端的 `CORS_ORIGINS` 环境变量包含前端域名

```
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:5173
```

### Q2: API 请求超时

**问题**: LLM 调用超时

**解决**: 
1. 增加前端的请求超时时间
2. 确保 Railway 实例配置足够的资源

### Q3: Railway 冷启动慢

**问题**: 首次访问响应很慢

**解决**: 
1. 使用 Railway 的 "Always On" 功能
2. 或定期发送心跳请求保持活跃

---

## 六、部署检查清单

- [ ] 后端环境变量已配置
- [ ] 前端 API 代理已配置
- [ ] CORS 已正确设置
- [ ] 健康检查端点正常
- [ ] 缓存服务可用 (可选)
- [ ] 日志收集已配置 (可选)

---

## 七、监控与日志

### Railway 日志查看

```bash
# 使用 Railway CLI
railway logs
```

### Vercel 日志查看

在 Vercel Dashboard 中查看 Functions 日志

---

**部署遇到问题？** 请提交 Issue 或联系维护者。

