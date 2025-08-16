"""Loguru Redis Sink实现

提供Loguru的自定义sink，负责接收日志记录，转换为Plumelog格式，
并异步发送到Redis。支持异步操作、批量处理和错误处理。
"""

import asyncio
from typing import Any, Callable, TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from loguru import Record
else:
    Record = Any


class LogSink(Protocol):
    """Loguru sink协议定义"""
    def __call__(self, message: Record) -> None:
        """处理日志消息"""
        ...


from .config import PlumelogSettings
from .extractor import FieldExtractor
from .models import LogRecord
from .redis_client import AsyncRedisClient


class LogRecordWithRetry:
    """带重试信息的日志记录包装类"""
    def __init__(self, log_record: LogRecord, retry_count: int = 0):
        self.log_record = log_record
        self.retry_count = retry_count


class RedisSink:
    """Loguru Redis Sink

    作为Loguru的自定义sink，负责接收日志记录，转换为Plumelog格式，
    并异步发送到Redis。通过内部队列和后台任务实现解耦，避免阻塞主线程。
    """

    def __init__(self, config: PlumelogSettings | None = None) -> None:
        """初始化Redis Sink

        Args:
            config: Plumelog配置对象，如果为None则使用默认配置
        """
        self.config = config or PlumelogSettings()
        self.field_extractor = FieldExtractor()
        self.redis_client = AsyncRedisClient(self.config)

        # 异步组件相关属性
        self._log_queue: asyncio.Queue[LogRecordWithRetry] | None = None
        self._consumer_task: asyncio.Task[None] | None = None
        self._running = False
        self._initialized = False

        # 临时缓存队列，用于存储初始化前的日志
        self._temp_buffer: list[LogRecord] = []
        self._temp_buffer_lock = asyncio.Lock() if self._has_event_loop() else None

    def _has_event_loop(self) -> bool:
        """检查是否有运行中的事件循环"""
        try:
            asyncio.get_running_loop()
            return True
        except RuntimeError:
            return False

    async def _ensure_initialized(self) -> None:
        """确保异步组件已初始化"""
        if self._initialized:
            return

        try:
            # 检查是否有运行中的事件循环
            loop = asyncio.get_running_loop()
            if loop and not self._initialized:
                # 创建内存队列作为缓冲区
                self._log_queue = asyncio.Queue(maxsize=self.config.queue_max_size)

                # 将临时缓存的日志转移到正式队列
                await self._transfer_temp_buffer_to_queue()

                # 创建后台消费者任务
                self._consumer_task = asyncio.create_task(self._log_consumer())
                self._running = True
                self._initialized = True

                print("[RedisSink] 异步组件初始化完成")

        except RuntimeError:
            # 没有运行中的事件循环，保持未初始化状态
            pass

    def __call__(self, message: Record) -> None:
        """Loguru sink调用接口（同步入口）

        这是Loguru调用的主要接口，需要处理同步到异步的转换。

        Args:
            message: Loguru日志消息对象
        """
        try:
            # 转换为LogRecord对象
            log_record = self._convert_to_log_record(message)

            # 检查是否有事件循环
            if self._has_event_loop():
                # 如果有事件循环，创建异步任务
                asyncio.create_task(self._async_handle_log(log_record))
            else:
                # 如果没有事件循环，存储到临时缓存
                self._store_to_temp_buffer(log_record)

        except Exception as e:
            print(f"[RedisSink] 处理日志时发生错误: {e}")
            # 降级处理：直接打印日志
            try:
                message_text = str(getattr(message, 'record', {}).get('message', message))
                print(f"[RedisSink] 降级输出: {message_text}")
            except Exception:
                print(f"[RedisSink] 降级输出: {str(message)}")

    async def _async_handle_log(self, log_record: LogRecord) -> None:
        """异步处理日志记录

        Args:
            log_record: 日志记录对象
        """
        try:
            # 确保异步组件已初始化
            await self._ensure_initialized()

            if not self._initialized or self._log_queue is None:
                # 如果无法初始化异步组件，存储到临时缓存
                self._store_to_temp_buffer(log_record)
                return

            # 将日志放入队列
            await self._log_queue.put(LogRecordWithRetry(log_record))

        except Exception as e:
            print(f"[RedisSink] 异步处理日志失败: {e}")

    def _store_to_temp_buffer(self, log_record: LogRecord) -> None:
        """将日志存储到临时缓存

        Args:
            log_record: 日志记录对象
        """
        if len(self._temp_buffer) >= self.config.temp_buffer_max_size:
            # 缓存已满，移除最老的日志
            self._temp_buffer.pop(0)
            print(f"[RedisSink] 临时缓存已满，移除最老的日志")

        self._temp_buffer.append(log_record)

    async def _transfer_temp_buffer_to_queue(self) -> None:
        """将临时缓存的日志转移到正式队列"""
        if not self._temp_buffer or self._log_queue is None:
            return

        transferred_count = 0
        remaining_logs = []

        for log_record in self._temp_buffer:
            try:
                self._log_queue.put_nowait(LogRecordWithRetry(log_record))
                transferred_count += 1
            except asyncio.QueueFull:
                # 如果队列满了，保留剩余的日志
                remaining_logs.append(log_record)

        # 更新临时缓存，保留未能转移的日志
        self._temp_buffer = remaining_logs

        if transferred_count > 0:
            print(f"[RedisSink] 已将 {transferred_count} 条临时缓存日志转移到正式队列")

        if remaining_logs:
            print(
                f"[RedisSink] 队列已满，{len(remaining_logs)} 条日志仍在临时缓存中"
            )

    async def _log_consumer(self) -> None:
        """后台消费者任务，持续从队列中获取日志并发送到Redis
        
        使用双条件触发机制：
        1. 达到批量大小立即发送
        2. 达到时间间隔发送当前积累的日志
        """
        assert self._log_queue is not None, "队列未初始化"

        batch = []
        last_send_time = asyncio.get_event_loop().time()

        # or 条件，满足任何 1 个就运行
        while self._running or not self._log_queue.empty():
            try:
                current_time = asyncio.get_event_loop().time()
                time_since_last_send = current_time - last_send_time
                
                # 计算剩余等待时间
                remaining_wait_time = max(0, self.config.batch_interval_seconds - time_since_last_send)
                
                # 如果已有数据且超时，立即发送
                if batch and time_since_last_send >= self.config.batch_interval_seconds:
                    await self._send_batch(batch)
                    batch = []
                    last_send_time = current_time
                    continue
                
                # 尝试从队列获取日志
                try:
                    log_record_with_retry = await asyncio.wait_for(
                        self._log_queue.get(), 
                        timeout=remaining_wait_time if batch else self.config.batch_interval_seconds
                    )
                    batch.append(log_record_with_retry)
                    
                    # 快速收集更多日志（非阻塞）
                    while len(batch) < self.config.batch_size and not self._log_queue.empty():
                        try:
                            batch.append(self._log_queue.get_nowait())
                        except asyncio.QueueEmpty:
                            break
                    
                    # 检查是否达到批量大小，立即发送
                    if len(batch) >= self.config.batch_size:
                        await self._send_batch(batch)
                        batch = []
                        last_send_time = asyncio.get_event_loop().time()
                    
                except asyncio.TimeoutError:
                    # 超时触发：如果有积累的日志，发送它们
                    if batch:
                        await self._send_batch(batch)
                        batch = []
                        last_send_time = asyncio.get_event_loop().time()
                    elif not self._running:
                        break  # 如果已停止运行且没有待处理的日志，则退出

            except Exception as e:
                print(f"[RedisSink] 消费者任务异常: {e}")
                # 发生异常时，等待一段时间再继续，避免CPU空转
                await asyncio.sleep(5)
        
        # 处理剩余的批次
        if batch:
            await self._send_batch(batch)

    async def _send_batch(self, batch: list[LogRecordWithRetry]) -> None:
        """发送批量日志到Redis
        
        Args:
            batch: 待发送的日志记录列表（带重试信息）
        """
        if not batch:
            return
        
        # 提取实际的日志记录
        log_records = [item.log_record for item in batch]
            
        try:
            success = await self.redis_client.send_log_records(log_records)
            
            if success:
                # 标记任务完成
                for _ in batch:
                    if self._log_queue:
                        self._log_queue.task_done()
            else:
                # 发送失败，先标记任务完成，避免无限等待
                for _ in batch:
                    if self._log_queue:
                        self._log_queue.task_done()
                
                # 然后处理重试逻辑
                await self._handle_send_failure(batch)
                
        except Exception as e:
            print(f"[RedisSink] 发送批量日志失败: {e}")
            # 先标记任务完成
            for _ in batch:
                if self._log_queue:
                    self._log_queue.task_done()
            
            # 然后处理重试逻辑
            await self._handle_send_failure(batch)

    async def _handle_send_failure(self, batch: list[LogRecordWithRetry]) -> None:
        """处理发送失败的批量日志
        
        Args:
            batch: 发送失败的日志记录列表
        """
        if not self._log_queue:
            return
            
        for item in reversed(batch):
            # 检查重试次数
            if item.retry_count >= self.config.retry_count:
                print(f"[RedisSink] 日志重试次数达到上限 ({self.config.retry_count})，丢弃日志: {item.log_record.content[:50]}...")
                continue
            
            # 增加重试次数
            item.retry_count += 1
            
            try:
                # 重新排队，有延迟
                await asyncio.sleep(0.1 * item.retry_count)  # 递增延迟
                await self._log_queue.put(item)
            except asyncio.QueueFull:
                print("[RedisSink] 队列已满，丢弃失败的日志")
                break

    def _convert_to_log_record(self, message: Record) -> LogRecord:
        """转换Loguru消息为LogRecord对象

        Args:
            message: Loguru日志消息对象

        Returns:
            LogRecord对象
        """
        # 获取调用者信息
        caller_info = self.field_extractor.get_caller_info(depth=3)

        # 获取系统信息
        system_info = self.field_extractor.get_system_info()

        # 获取时间信息
        import datetime
        record_dict = getattr(message, 'record', {})
        log_time = record_dict.get('time')
        
        # 如果 log_time 为 None，使用当前时间
        if log_time is None:
            log_time = datetime.datetime.now()

        # 构建LogRecord对象
        return LogRecord(
            server_name=system_info.server_name,
            app_name=self.config.app_name,
            env=self.config.env,
            method=caller_info.method_name_safe,
            content=str(record_dict.get('message', '')),
            log_level=getattr(record_dict.get('level', {}), 'name', 'INFO'),
            class_name=caller_info.class_name_safe,
            thread_name=system_info.thread_name,
            seq=self.field_extractor.get_next_seq(),
            date_time=self.field_extractor.format_datetime(log_time),
            dt_time=self.field_extractor.get_timestamp_ms(log_time),
        )

    async def close(self) -> None:
        """关闭Redis Sink，停止后台任务并清理资源"""
        print("[RedisSink] 正在关闭...")
        self._running = False

        # 等待消费者任务完成（如果已初始化）
        if self._consumer_task and not self._consumer_task.done():
            try:
                await asyncio.wait_for(self._consumer_task, timeout=10.0)
            except asyncio.TimeoutError:
                print("[RedisSink] 消费者任务超时，强制取消")
                self._consumer_task.cancel()
                try:
                    await self._consumer_task
                except asyncio.CancelledError:
                    pass

        # 处理剩余的队列中的日志
        if self._log_queue and not self._log_queue.empty():
            remaining_logs = []
            while not self._log_queue.empty():
                try:
                    item = self._log_queue.get_nowait()
                    remaining_logs.append(item.log_record)
                except asyncio.QueueEmpty:
                    break

            if remaining_logs:
                print(f"[RedisSink] 发送剩余的 {len(remaining_logs)} 条日志...")
                await self.redis_client.send_log_records(remaining_logs)

        # 关闭Redis连接
        if self._initialized:
            await self.redis_client.disconnect()

        # 重置状态
        self._initialized = False
        self._log_queue = None
        self._consumer_task = None

        print("[RedisSink] 已成功关闭")

    async def __aenter__(self) -> "RedisSink":  # type: ignore
        """异步上下文管理器入口"""
        await self._ensure_initialized()
        return self

    async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: Any | None
    ) -> None:
        """异步上下文管理器出口"""
        await self.close()


def create_redis_sink(config: PlumelogSettings | None = None) -> Callable[[Record], None]:
    """创建Redis Sink函数

    提供便捷的工厂函数来创建Redis Sink实例。

    Args:
        config: Plumelog配置对象

    Returns:
        可用于Loguru的sink函数
    """
    return RedisSink(config)
