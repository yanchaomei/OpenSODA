# 🤖 OpenSource Copilot

> 基于 ReAct Agent 架构的开源社区智能运营助手

<p align="center">
  <img src="https://img.shields.io/badge/🏆_OpenRank_Cup-OpenSODA_2025-8b5cf6?style=for-the-badge" alt="OpenSODA 2025"/>
</p>

| 🎯 赛题 | 📦 基于开源工具 | 🏷️ 赛道 |
|:------:|:-------------:|:------:|
| **赛题三：大模型应用开发** | **OpenDigger + MaxKB + DataEase** | 开放创新 |

---

[![OpenSODA 2025](https://img.shields.io/badge/OpenSODA-2025-purple)](https://atomgit.com/x-lab/OpenSODA2025)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-green)](https://python.org)
[![Vue](https://img.shields.io/badge/Vue-3.4+-brightgreen)](https://vuejs.org)

## 📖 项目简介

OpenSource Copilot 是一个基于 **ReAct (Reasoning + Acting) Agent 架构**的开源社区智能运营助手。它能够像人类专家一样**思考问题、调用工具、分析数据**，帮助项目维护者进行：

- 🏥 **社区健康度诊断** - 基于 OpenRank 等多维度指标全面评估项目健康状况
- 🔍 **问题识别与预警** - 智能发现社区运营中的问题和潜在风险
- 💡 **运营建议生成** - 提供专业、可执行的改进建议
- 💬 **自然语言交互** - 通过对话方式获取分析结果和指导

### 🎯 适用人群

- 开源项目维护者 (Maintainer)
- 企业 OSPO (开源项目办公室)
- 开源社区运营人员
- 开源爱好者和研究者

## ✨ 核心功能

### 1. ReAct Agent 工作流程

```
用户: "分析 apache/dubbo 的健康状况"
              │
              ▼
    ┌─────────────────┐
    │   🤔 思考       │  → 理解用户意图，决定调用哪个工具
    │   (Thought)     │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │   🔧 行动       │  → 调用 analyze_repo_health 工具
    │   (Action)      │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │   👁️ 观察       │  → 获取健康度报告数据
    │   (Observation) │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │   💬 回复       │  → 生成分析报告给用户
    │   (Response)    │
    └─────────────────┘
```

### 2. Agent 工具集

| 工具 | 功能 | 数据来源 |
|------|------|----------|
| `analyze_repo_health` | 全面健康度分析 | OpenDigger |
| `diagnose_repo_issues` | 问题诊断 | OpenDigger |
| `get_improvement_suggestions` | 改进建议 | LLM + 知识库 |
| `get_repo_openrank` | OpenRank 查询 | OpenDigger |
| `get_repo_activity_trend` | 活跃度趋势 | OpenDigger |
| `get_github_repo_info` | GitHub 信息 | GitHub API |
| `find_good_first_issues` | 新手 Issue | GitHub API |
| `search_opensource_knowledge` | 知识检索 | MaxKB |

### 2. 健康度评估维度

| 维度 | 说明 | 数据来源 |
|------|------|----------|
| 活跃度 | OpenRank、Activity 指标 | OpenDigger |
| 社区健康度 | 贡献者数量、巴士因子 | OpenDigger |
| 维护响应度 | Issue 响应时间、PR 合并率 | OpenDigger |
| 增长趋势 | Star/Fork 增长、新贡献者 | GitHub API |

### 3. 可视化报告

- 📊 健康度雷达图
- 📈 趋势分析图表
- 🏆 贡献者排行榜
- 📋 诊断报告卡片

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | Vue 3 + TypeScript + Vite + TailwindCSS + ECharts |
| **后端** | FastAPI + Python 3.11 + WebSocket |
| **Agent** | LangGraph + LangChain + OpenAI GPT-4o |
| **数据源** | OpenDigger API + GitHub REST API |
| **知识库** | MaxKB (可选) |
| **可视化** | DataEase + ECharts |
| **部署** | Docker Compose |

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (可选)

### 方式一：Docker 部署 (推荐)

```bash
# 1. 克隆项目
git clone https://github.com/your-username/opensource-copilot.git
cd opensource-copilot

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 OpenAI API Key 等配置

# 3. 启动服务
docker-compose up -d

# 4. 访问应用
# 前端: http://localhost:3000
# 后端 API: http://localhost:8000
```

### 方式二：本地开发

```bash
# 后端
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # 配置环境变量
uvicorn main:app --reload

# 前端 (新终端)
cd frontend
npm install
npm run dev
```

### 配置说明

创建 `.env` 文件并配置以下环境变量：

```env
# OpenAI 配置 (必需)
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o
OPENAI_BASE_URL=https://api.gptsapi.net/v1

# GitHub Token (可选，用于提高 API 限额)
GITHUB_TOKEN=your_github_token

# 数据库 (本地开发可选)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/opensource_copilot
REDIS_URL=redis://localhost:6379/0
```

## 📸 功能截图

### 首页
![首页](docs/images/home.png)

### 智能对话
![对话](docs/images/chat.png)

### 项目分析
![分析](docs/images/analysis.png)

### 数据仪表盘
![仪表盘](docs/images/dashboard.png)

## 📁 项目结构

```
OpenSODA/
├── frontend/                 # Vue 3 前端
│   ├── src/
│   │   ├── components/       # 通用组件
│   │   ├── views/            # 页面视图
│   │   ├── stores/           # Pinia 状态管理
│   │   ├── api/              # API 调用
│   │   └── utils/            # 工具函数
│   └── package.json
│
├── backend/                  # FastAPI 后端
│   ├── app/
│   │   ├── api/              # API 路由
│   │   ├── agents/           # LangGraph Agent 定义
│   │   │   ├── orchestrator.py
│   │   │   ├── analysis.py
│   │   │   ├── diagnosis.py
│   │   │   └── advisor.py
│   │   ├── tools/            # Agent 工具
│   │   │   ├── opendigger.py
│   │   │   ├── github.py
│   │   │   ├── maxkb.py
│   │   │   └── dataease.py
│   │   ├── services/         # 业务逻辑
│   │   ├── models/           # 数据模型
│   │   └── core/             # 配置/依赖
│   └── requirements.txt
│
├── knowledge/                # 知识库内容
├── docker-compose.yml        # Docker 编排
└── README.md
```

## 🔌 API 文档

启动后端服务后，访问 `http://localhost:8000/docs` 查看 Swagger API 文档。

### 主要接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/chat/` | POST | 普通对话 |
| `/api/chat/stream` | POST | 流式对话 |
| `/api/chat/ws` | WebSocket | 实时对话 |
| `/api/analysis/repo/{owner}/{repo}` | GET | 分析仓库 |
| `/api/analysis/compare` | POST | 对比多个仓库 |
| `/api/health/` | GET | 系统健康检查 |

## 🤝 使用的开源项目

本项目使用了以下 OpenSODA 指定的开源工具：

- **[OpenDigger](https://github.com/X-lab2017/open-digger)** - 开源项目数据分析工具，提供 OpenRank 等指标数据
- **[MaxKB](https://github.com/1Panel-dev/MaxKB)** - 知识库系统，存储开源运营最佳实践
- **[DataEase](https://github.com/dataease/dataease)** - 数据可视化平台

## 📊 OpenRank 指标说明

OpenRank 是 X-lab 提出的开源项目影响力评估算法，本项目深度集成了 OpenRank 指标：

| OpenRank 值 | 级别 | 说明 |
|-------------|------|------|
| > 100 | 顶级 | Linux、Kubernetes 等 |
| 50-100 | 知名 | 活跃的知名项目 |
| 20-50 | 活跃 | 有一定影响力 |
| 5-20 | 成长 | 正在发展中 |
| < 5 | 新兴 | 小型或新项目 |

## 🏆 参赛信息

- **赛项**: "OpenRank杯"开源数字生态分析与应用创新赛
- **主题**: 开源治理与运营
- **参考资料**: [OpenSODA 2025](https://atomgit.com/x-lab/OpenSODA2025)

## 📄 开源协议

本项目采用 [Apache License 2.0](LICENSE) 开源协议。

## 👥 团队成员

| 成员 | 角色 | 贡献 |
|------|------|------|
| - | 开发者 | 全栈开发 |

## 🙏 致谢

- [X-lab](https://github.com/X-lab2017) - OpenDigger 项目
- [1Panel](https://github.com/1Panel-dev) - MaxKB 项目
- [DataEase](https://github.com/dataease) - DataEase 项目
- [LangChain](https://github.com/langchain-ai) - LangGraph 框架

---

<p align="center">
  Made with ❤️ for OpenSODA 2025
</p>

