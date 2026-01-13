# Changelog

所有重要的变更都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [1.0.0] - 2025-01-09

### 新增 (Added)

#### 核心功能
- 🤖 基于 LangGraph 的 ReAct Agent 架构
- 💬 流式对话接口，实时展示 Agent 思考过程
- 📊 11 个专业工具用于开源项目分析
- 🔍 多维度健康度评估算法

#### 分析功能
- 单项目健康度分析
- 多项目对比分析 (支持 2-5 个项目)
- 分析报告导出 (Markdown/JSON)
- 历史分析记录 (本地存储)

#### 数据可视化
- 健康度雷达图 (ECharts)
- 活跃度趋势图
- 对比柱状图
- 评分仪表盘

#### 系统功能
- 智能缓存系统 (内存 + Redis)
- 健康检查 API
- Docker Compose 部署支持

### 技术栈

#### 后端
- Python 3.11+
- FastAPI 0.109.0
- LangGraph 0.0.55
- LangChain 0.1.20

#### 前端
- Vue 3.4+
- TypeScript
- Vite
- TailwindCSS
- ECharts

#### 集成
- OpenDigger API (开源指标数据)
- GitHub REST API
- MaxKB 知识库 (可选)
- DataEase 可视化 (可选)

### 已知问题 (Known Issues)

- 部分项目的 OpenDigger 数据可能不完整
- MaxKB 集成需要额外配置
- 大量并发请求时可能触发 API 限流

---

## [未来计划] - Roadmap

### v1.1.0

- [ ] 批量项目监控功能
- [ ] 自定义评估权重
- [ ] 更多可视化图表类型
- [ ] 邮件/Webhook 告警

### v1.2.0

- [ ] 用户系统
- [ ] 项目收藏功能
- [ ] 定期报告生成
- [ ] API 认证

### v2.0.0

- [ ] 多租户支持
- [ ] 自定义 Agent 工具
- [ ] 插件系统
- [ ] 国际化 (i18n)

---

## 贡献者

感谢所有贡献者的付出！

<!-- 贡献者列表将在项目发展过程中更新 -->

---

## 链接

- [项目主页](https://github.com/your-username/opensource-copilot)
- [问题反馈](https://github.com/your-username/opensource-copilot/issues)
- [OpenSODA 2025](https://atomgit.com/x-lab/OpenSODA2025)

