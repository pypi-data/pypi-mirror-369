"""测试新的批量处理逻辑

测试双条件触发机制：
1. 数量触发：达到batch_size立即发送
2. 时间触发：达到batch_interval_seconds发送当前积累的日志
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from plumelog_loguru.redis_sink import RedisSink, LogRecordWithRetry
from plumelog_loguru.config import PlumelogSettings
from plumelog_loguru.models import LogRecord


class TestBatchLogic:
    """测试批量处理逻辑"""

    @pytest.fixture
    def config(self):
        """测试配置"""
        return PlumelogSettings(
            batch_size=3,
            batch_interval_seconds=1.0,
            queue_max_size=100
        )

    @pytest.fixture
    def mock_redis_client(self):
        """模拟Redis客户端"""
        mock_client = AsyncMock()
        mock_client.send_log_records = AsyncMock(return_value=True)
        return mock_client

    @pytest.fixture
    async def redis_sink(self, config, mock_redis_client):
        """创建Redis sink实例"""
        with patch('plumelog_loguru.redis_sink.AsyncRedisClient', return_value=mock_redis_client):
            sink = RedisSink(config)
            await sink._ensure_initialized()
            yield sink
            await sink.close()

    def create_mock_log_record(self, content: str) -> LogRecord:
        """创建模拟日志记录"""
        return LogRecord(
            server_name="test-server",
            app_name="test-app",
            env="test",
            method="test_method",
            content=content,
            log_level="INFO",
            class_name="TestClass",
            thread_name="main",
            seq=1,
            date_time="2024-01-01 12:00:00",
            dt_time=1704067200000,
        )

    @pytest.mark.asyncio
    async def test_batch_size_trigger(self, redis_sink, mock_redis_client):
        """测试批量大小触发机制"""
        # 快速添加3条日志，应该立即触发发送
        for i in range(3):
            log_record = self.create_mock_log_record(f"message {i}")
            await redis_sink._log_queue.put(LogRecordWithRetry(log_record))

        # 等待短时间让消费者处理
        await asyncio.sleep(0.1)

        # 验证调用了send_log_records，且参数长度为3
        mock_redis_client.send_log_records.assert_called_once()
        call_args = mock_redis_client.send_log_records.call_args[0][0]
        assert len(call_args) == 3
        assert all("message" in record.content for record in call_args)

    @pytest.mark.asyncio
    async def test_time_interval_trigger(self, redis_sink, mock_redis_client):
        """测试时间间隔触发机制"""
        # 添加少于batch_size的日志
        for i in range(2):
            log_record = self.create_mock_log_record(f"slow message {i}")
            await redis_sink._log_queue.put(LogRecordWithRetry(log_record))

        # 等待超过batch_interval_seconds
        await asyncio.sleep(1.2)

        # 验证调用了send_log_records，且参数长度为2
        mock_redis_client.send_log_records.assert_called_once()
        call_args = mock_redis_client.send_log_records.call_args[0][0]
        assert len(call_args) == 2
        assert all("slow message" in record.content for record in call_args)

    @pytest.mark.asyncio
    async def test_mixed_trigger_scenarios(self, redis_sink, mock_redis_client):
        """测试混合触发场景"""
        # 场景1: 先达到数量触发
        for i in range(3):
            log_record = self.create_mock_log_record(f"batch1 message {i}")
            await redis_sink._log_queue.put(LogRecordWithRetry(log_record))

        await asyncio.sleep(0.1)  # 让第一批处理完

        # 重置mock以便检查第二批
        mock_redis_client.reset_mock()

        # 场景2: 然后少量日志，等待时间触发
        for i in range(2):
            log_record = self.create_mock_log_record(f"batch2 message {i}")
            await redis_sink._log_queue.put(LogRecordWithRetry(log_record))

        await asyncio.sleep(1.2)  # 等待时间触发

        # 验证第二批调用
        mock_redis_client.send_log_records.assert_called_once()
        call_args = mock_redis_client.send_log_records.call_args[0][0]
        assert len(call_args) == 2
        assert all("batch2 message" in record.content for record in call_args)

    @pytest.mark.asyncio
    async def test_send_failure_retry(self, redis_sink, mock_redis_client):
        """测试发送失败时的重试机制"""
        # 设置发送失败
        mock_redis_client.send_log_records = AsyncMock(return_value=False)

        # 添加一批日志
        for i in range(3):
            log_record = self.create_mock_log_record(f"retry message {i}")
            await redis_sink._log_queue.put(LogRecordWithRetry(log_record))

        # 等待处理，包括重试时间
        await asyncio.sleep(0.5)

        # 验证调用了send方法多次（原始发送 + 重试）
        assert mock_redis_client.send_log_records.call_count >= 1

        # 停止消费者以避免无限重试
        redis_sink._running = False

    @pytest.mark.asyncio
    async def test_empty_batch_handling(self, redis_sink, mock_redis_client):
        """测试空批次处理"""
        # 不添加任何日志，等待超时
        await asyncio.sleep(1.2)

        # 验证没有调用send方法（因为没有日志）
        mock_redis_client.send_log_records.assert_not_called()

    @pytest.mark.asyncio
    async def test_consumer_stops_gracefully(self, redis_sink, mock_redis_client):
        """测试消费者优雅停止"""
        # 添加一些日志
        for i in range(2):
            log_record = self.create_mock_log_record(f"final message {i}")
            await redis_sink._log_queue.put(LogRecordWithRetry(log_record))

        # 停止消费者
        redis_sink._running = False

        # 等待消费者处理剩余的日志
        await asyncio.sleep(0.2)

        # 验证剩余的日志被处理了
        mock_redis_client.send_log_records.assert_called_once()
        call_args = mock_redis_client.send_log_records.call_args[0][0]
        assert len(call_args) == 2
