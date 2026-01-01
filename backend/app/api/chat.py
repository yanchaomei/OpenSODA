"""
Chat API - 对话接口
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import json

router = APIRouter()


class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str  # user, assistant, system
    content: str


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str
    repo: Optional[str] = None  # 可选的仓库地址，如 "apache/dubbo"
    history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    """聊天响应模型"""
    message: str
    metrics: Optional[dict] = None
    charts: Optional[List[dict]] = None
    recommendations: Optional[List[str]] = None


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    普通聊天接口
    """
    from app.agents.orchestrator import run_agent
    
    result = await run_agent(
        message=request.message,
        repo=request.repo,
        history=request.history
    )
    
    return ChatResponse(
        message=result.get("response", ""),
        metrics=result.get("metrics"),
        charts=result.get("charts"),
        recommendations=result.get("recommendations")
    )


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    流式聊天接口
    """
    from app.agents.orchestrator import run_agent_stream
    
    async def generate():
        async for chunk in run_agent_stream(
            message=request.message,
            repo=request.repo,
            history=request.history
        ):
            yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.websocket("/ws")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket聊天接口 - 支持实时双向通信
    """
    await websocket.accept()
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_json()
            message = data.get("message", "")
            repo = data.get("repo")
            history = data.get("history", [])
            
            # 发送处理中状态
            await websocket.send_json({
                "type": "status",
                "status": "processing"
            })
            
            # 调用Agent处理
            from app.agents.orchestrator import run_agent_stream
            
            async for chunk in run_agent_stream(
                message=message,
                repo=repo,
                history=history
            ):
                await websocket.send_json({
                    "type": "chunk",
                    "data": chunk
                })
            
            # 发送完成状态
            await websocket.send_json({
                "type": "status",
                "status": "completed"
            })
            
    except WebSocketDisconnect:
        print("WebSocket disconnected")

