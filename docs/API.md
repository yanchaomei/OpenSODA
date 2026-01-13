# API 文档

OpenSource Copilot 提供 RESTful API 接口，支持流式输出和批量操作。

## 基础信息

- **Base URL**: `http://localhost:8001/api`
- **协议**: HTTP/HTTPS
- **数据格式**: JSON
- **认证**: 无需认证（本地部署）

## 接口列表

### 1. 聊天接口

#### POST /chat/stream

流式对话接口，使用 Server-Sent Events (SSE) 返回 Agent 的思考过程和回复。

**请求体**:

```json
{
  "message": "分析 apache/dubbo 的健康状况",
  "repo": "apache/dubbo",  // 可选，指定上下文仓库
  "history": []  // 可选，对话历史
}
```

**响应** (SSE 流):

```
data: {"type": "status", "step": "thinking", "message": "🤔 正在思考..."}

data: {"type": "tool_start", "tool": "analyze_repo_health", "tool_display": "📊 分析仓库健康度", "input": {"repo": "apache/dubbo"}}

data: {"type": "tool_end", "tool": "analyze_repo_health", "output": "健康度报告..."}

data: {"type": "text", "content": "## 📊 apache/dubbo 健康度分析报告\n\n..."}

data: {"type": "status", "step": "complete", "message": "✨ 处理完成"}
```

**事件类型**:

| type | 说明 |
|------|------|
| `status` | 状态更新 |
| `tool_start` | 开始调用工具 |
| `tool_end` | 工具调用完成 |
| `text` | 文本输出（流式） |
| `error` | 错误信息 |

---

### 2. 分析接口

#### GET /analysis/repo/{owner}/{repo}

分析单个仓库的健康度。

**路径参数**:

- `owner`: 仓库所有者
- `repo`: 仓库名称

**响应**:

```json
{
  "repo": "apache/dubbo",
  "health_score": {
    "overall": 72.5,
    "activity": 78.0,
    "community": 75.0,
    "maintenance": 68.0,
    "growth": 65.0,
    "summary": "项目整体健康度良好...",
    "highlights": ["OpenRank 值较高，影响力强"],
    "concerns": ["增长趋势放缓"]
  },
  "openrank": 45.23,
  "activity": 12.8,
  "attention": 234.5,
  "metrics": {
    "openrank": 45.23,
    "activity": 12.8,
    "participants": 156,
    "bus_factor": 15,
    "new_contributors": 8
  },
  "trends": {
    "openrank": [42.1, 43.5, 44.2, 45.23],
    "activity": [10.2, 11.5, 12.1, 12.8],
    "months": ["2024-07", "2024-08", "2024-09", "2024-10"]
  },
  "analyzed_at": "2025-01-09T10:30:00Z"
}
```

#### POST /analysis/compare

对比多个仓库。

**请求体**:

```json
{
  "repos": ["apache/dubbo", "vuejs/vue", "facebook/react"]
}
```

**响应**:

```json
{
  "comparisons": [
    {
      "repo": "apache/dubbo",
      "health_score": {...},
      "metrics": {...},
      "rank": 2
    },
    {
      "repo": "vuejs/vue",
      "health_score": {...},
      "metrics": {...},
      "rank": 1
    }
  ],
  "summary": {
    "total_repos": 2,
    "valid_repos": 2,
    "average_score": 75.5,
    "best_overall": {"repo": "vuejs/vue", "score": 82.3},
    "best_activity": {"repo": "vuejs/vue", "score": 85.0},
    "best_community": {"repo": "apache/dubbo", "score": 78.0},
    "best_maintenance": {"repo": "vuejs/vue", "score": 80.0},
    "best_growth": {"repo": "apache/dubbo", "score": 72.0}
  },
  "winner": "vuejs/vue",
  "compared_at": "2025-01-09T10:30:00Z"
}
```

---

### 3. 导出接口

#### POST /analysis/export/markdown

导出分析报告为 Markdown 格式。

**请求体**:

```json
{
  "repos": ["apache/dubbo"]
}
```

**响应**: Markdown 文件下载

#### POST /analysis/export/json

导出分析报告为 JSON 格式。

**请求体**:

```json
{
  "repos": ["apache/dubbo"]
}
```

**响应**: JSON 文件下载

---

### 4. 趋势接口

#### GET /analysis/trending

获取热门开源项目列表。

**查询参数**:

- `language` (可选): 编程语言筛选
- `period` (可选): 时间周期，默认 "weekly"

**响应**:

```json
{
  "period": "weekly",
  "language": null,
  "repos": [
    {"repo": "kubernetes/kubernetes", "openrank": 892.5, "category": "云原生"},
    {"repo": "tensorflow/tensorflow", "openrank": 567.3, "category": "AI/ML"}
  ],
  "updated_at": "2025-01-09T10:30:00Z"
}
```

---

### 5. 健康检查接口

#### GET /health/

系统健康检查。

**响应**:

```json
{
  "status": "healthy",
  "services": {
    "opendigger": {"name": "opendigger", "status": "healthy", "latency_ms": 234.5},
    "openai": {"name": "openai", "status": "healthy", "latency_ms": 456.2},
    "database": {"name": "database", "status": "unknown", "latency_ms": 0}
  }
}
```

#### GET /health/cache

缓存统计信息。

**响应**:

```json
{
  "status": "ok",
  "cache": {
    "memory": {
      "type": "memory",
      "size": 45,
      "max_size": 500,
      "default_ttl": 1800
    },
    "redis": null,
    "performance": {
      "hits": 156,
      "misses": 23,
      "sets": 179,
      "hit_rate": 0.87
    }
  }
}
```

#### POST /health/cache/clear

清空缓存。

**响应**:

```json
{
  "status": "ok",
  "message": "Cache cleared successfully"
}
```

---

## 错误处理

所有接口在出错时返回标准错误格式：

```json
{
  "detail": "错误描述信息"
}
```

**HTTP 状态码**:

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 使用示例

### cURL

```bash
# 分析仓库
curl -X GET "http://localhost:8001/api/analysis/repo/apache/dubbo"

# 对比仓库
curl -X POST "http://localhost:8001/api/analysis/compare" \
  -H "Content-Type: application/json" \
  -d '{"repos": ["apache/dubbo", "vuejs/vue"]}'

# 流式对话
curl -X POST "http://localhost:8001/api/chat/stream" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"message": "分析 apache/dubbo"}'
```

### Python

```python
import requests

# 分析仓库
response = requests.get("http://localhost:8001/api/analysis/repo/apache/dubbo")
data = response.json()
print(f"健康度: {data['health_score']['overall']}")

# 流式对话
import sseclient

def stream_chat(message):
    response = requests.post(
        "http://localhost:8001/api/chat/stream",
        json={"message": message},
        stream=True
    )
    client = sseclient.SSEClient(response)
    for event in client.events():
        print(event.data)

stream_chat("分析 apache/dubbo")
```

### JavaScript

```javascript
// 分析仓库
const response = await fetch('http://localhost:8001/api/analysis/repo/apache/dubbo');
const data = await response.json();
console.log(`健康度: ${data.health_score.overall}`);

// 流式对话
const eventSource = new EventSource('http://localhost:8001/api/chat/stream', {
  method: 'POST',
  body: JSON.stringify({ message: '分析 apache/dubbo' })
});

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

---

## Swagger UI

完整的交互式 API 文档可通过访问以下地址查看：

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **OpenAPI JSON**: http://localhost:8001/openapi.json

