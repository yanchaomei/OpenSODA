# OpenRank 指标详解

## 什么是 OpenRank？

OpenRank 是由 X-lab 开放实验室提出的开源项目影响力评估算法，基于 PageRank 思想，综合考虑开源协作网络中的多种因素。

## 算法原理

### 核心思想

1. **网络方法**: 将开源协作建模为网络图
2. **影响力传播**: 贡献者之间的影响力可以传递
3. **时间衰减**: 近期活动权重更高
4. **多维贡献**: 综合 Issue、PR、Review、Commit

### 计算要素

```
OpenRank = f(贡献者网络, 贡献类型, 时间权重, 协作关系)
```

**贡献类型及权重**:
- Issue 创建/评论
- PR 提交/Review
- Commit
- 代码 Review

## 数值解读

| 范围 | 级别 | 典型项目 |
|------|------|----------|
| > 200 | 超级 | Linux Kernel |
| 100-200 | 顶级 | Kubernetes, TensorFlow |
| 50-100 | 知名 | Vue, React Native |
| 20-50 | 活跃 | 活跃的中型项目 |
| 5-20 | 成长 | 有潜力的项目 |
| < 5 | 新兴 | 新项目或小型项目 |

## 如何提升 OpenRank

### 1. 增加活跃贡献者

- 吸引更多开发者参与
- 鼓励现有用户贡献
- 建立贡献者社区

### 2. 提高贡献质量

- 规范的 PR 流程
- 详细的 Code Review
- 有价值的 Issue 讨论

### 3. 保持持续活跃

- 定期发布版本
- 及时响应社区
- 持续迭代改进

### 4. 建立协作网络

- 与其他项目合作
- 参与上下游生态
- 建立开发者关系

## 与其他指标的关系

### vs Star 数

- Star 反映项目知名度
- OpenRank 反映项目影响力
- Star 可能虚高，OpenRank 更真实

### vs 贡献者数

- 贡献者数是数量指标
- OpenRank 考虑贡献质量
- OpenRank 更能反映社区健康

### vs Activity

- Activity 是活跃度指标
- OpenRank 是影响力指标
- 两者相关但侧重不同

## 数据来源

OpenRank 数据可通过 OpenDigger 获取：

```
https://oss.x-lab.info/open_digger/github/{owner}/{repo}/openrank.json
```

返回按月份索引的时序数据。

## 参考资源

- [OpenDigger 项目](https://github.com/X-lab2017/open-digger)
- [OpenRank 论文](https://arxiv.org/abs/xxxx.xxxxx)
- [X-lab 官网](https://x-lab.info)

