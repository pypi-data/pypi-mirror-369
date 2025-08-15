import asyncio
import json
import time
from typing import Dict, Any, AsyncGenerator
from aiforge import WebProgressIndicator
from aiforge import ProgressIndicatorRegistry
from aiforge import UITypeRecommender


class StreamingExecutionManager:
    """流式执行管理器 - 为 Web 界面提供实时进度反馈"""

    def __init__(self, components: Dict[str, Any]):
        self.components = components

    async def execute_with_streaming(
        self, instruction: str, ui_type: str = "web", context_data: Dict[str, Any] = None
    ) -> AsyncGenerator[str, None]:
        """流式执行指令并返回进度 - 支持进度级别控制"""

        # 获取进度级别设置，默认为详细模式
        progress_level = (
            context_data.get("progress_level", "detailed") if context_data else "detailed"
        )

        progress_queue = asyncio.Queue()
        execution_complete = asyncio.Event()
        execution_result = None
        execution_error = None

        async def progress_callback(message_data: Dict[str, Any]):
            """进度回调函数 - 根据进度级别过滤消息"""
            try:
                message_type = message_data.get("type", "progress")
                progress_type = message_data.get("progress_type", "info")

                # 根据进度级别决定是否发送消息
                should_send = False

                if progress_level == "none":
                    # 只发送结果、错误和完成消息
                    should_send = message_type in ["result", "error", "complete"]
                elif progress_level == "minimal":
                    # 只发送关键节点消息
                    should_send = message_type in [
                        "result",
                        "error",
                        "complete",
                    ] or progress_type in [
                        "task_start",
                        "task_complete",
                    ]
                else:  # detailed
                    # 发送所有消息
                    should_send = True

                if should_send:
                    await progress_queue.put(message_data)
            except Exception:
                pass

        # 替换进度指示器为 Web 流式版本
        original_progress = self.components.get("progress_indicator")
        web_progress = WebProgressIndicator(self.components, progress_callback)
        self.components["progress_indicator"] = web_progress
        ProgressIndicatorRegistry.set_current(web_progress)  # 注册到全局

        try:
            # 发送开始消息（根据进度级别决定是否发送）
            await progress_callback(
                {
                    "type": "progress",
                    "message": "🚀 开始执行指令...",
                    "progress_type": "task_start",
                    "timestamp": time.time(),
                }
            )

            # 后台执行任务
            async def execute_task():
                nonlocal execution_result, execution_error
                try:
                    # 准备输入数据（与同步端点保持一致）
                    raw_input = {
                        "instruction": instruction,
                        "method": "POST",
                        "user_agent": "AIForge-Web",
                        "ip_address": "127.0.0.1",
                        "request_id": context_data.get("session_id") if context_data else None,
                    }

                    # 使用全局 forge 实例执行（避免重复初始化）
                    from aiforge_web.main import forge

                    result = await asyncio.to_thread(
                        forge.run_with_input_adaptation, raw_input, "web", context_data or {}
                    )

                    if result:
                        # 从结果的 metadata 中获取任务类型，回退到 context_data
                        task_type = result.get("metadata", {}).get("task_type") or context_data.get(
                            "task_type"
                        )

                        if task_type == "content_generation":
                            # 内容生成任务直接使用 web_editor，跳过 AI 适配以节省 token
                            ui_result = await asyncio.to_thread(
                                forge.adapt_result_for_ui, result, "web_editor", "web"
                            )
                        else:
                            # 其他任务类型使用 UITypeRecommender 智能选择
                            ui_recommender = UITypeRecommender()
                            recommendations = ui_recommender.recommend_ui_types(
                                result, task_type or "general", "web"
                            )
                            ui_type = recommendations[0][0] if recommendations else "web_card"

                            ui_result = await asyncio.to_thread(
                                forge.adapt_result_for_ui, result, ui_type, "web"
                            )

                        execution_result = {
                            "success": True,
                            "result": ui_result,
                            "metadata": {"source": "web", "processed_at": time.time()},
                        }
                    else:
                        execution_error = "执行失败：未获得结果"

                except Exception as e:
                    execution_error = f"执行错误: {str(e)}"
                    # 发送错误进度消息
                    await progress_callback(
                        {
                            "type": "progress",
                            "message": f"❌ 执行失败: {str(e)}",
                            "progress_type": "error",
                            "timestamp": time.time(),
                        }
                    )
                finally:
                    execution_complete.set()

            # 启动执行任务
            task = asyncio.create_task(execute_task())

            try:
                # 流式返回进度消息
                while not execution_complete.is_set():
                    try:
                        # 检查客户端是否断开连接
                        if hasattr(self, "_client_disconnected") and self._client_disconnected:
                            # 取消后台任务
                            task.cancel()
                            yield f"data: {json.dumps({'type': 'cancelled', 'message': '执行已被用户停止'})}\n\n"  # noqa 501
                            break

                        # 等待进度消息
                        message = await asyncio.wait_for(progress_queue.get(), timeout=0.5)
                        yield f"data: {json.dumps(message, ensure_ascii=False)}\n\n"
                    except asyncio.TimeoutError:
                        # 发送心跳保持连接
                        yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': time.time()})}\n\n"  # noqa 501
            except GeneratorExit:
                # 客户端断开连接时触发
                self._client_disconnected = True
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

            # 等待执行完成
            await task

            # 处理剩余进度消息
            while not progress_queue.empty():
                try:
                    message = progress_queue.get_nowait()
                    yield f"data: {json.dumps(message, ensure_ascii=False)}\n\n"
                except asyncio.QueueEmpty:
                    break

            # 发送最终结果
            if execution_result:
                yield f"data: {json.dumps({'type': 'result', 'data': execution_result}, ensure_ascii=False)}\n\n"  # noqa 501
            elif execution_error:
                yield f"data: {json.dumps({'type': 'error', 'message': execution_error}, ensure_ascii=False)}\n\n"  # noqa 501

            # 发送完成信号
            yield f"data: {json.dumps({'type': 'complete', 'timestamp': time.time()})}\n\n"

        except Exception as e:
            # 发送错误信息
            error_message = f"流式执行错误: {str(e)}"
            yield f"data: {json.dumps({'type': 'error', 'message': error_message}, ensure_ascii=False)}\n\n"  # noqa 501

        finally:
            # 恢复原始进度指示器
            if original_progress:
                self.components["progress_indicator"] = original_progress
