"""
连接池管理器模块

提供HTTP连接池的统一管理，支持连接复用、统计监控和健康检查。
"""

import asyncio
import logging
import time
import weakref
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx

from .config import WeiboConfig
from .exceptions import ConfigError, ConnectionPoolError, NetworkError


@dataclass
class ConnectionStats:
    """连接池统计信息"""

    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    created_connections: int = 0
    closed_connections: int = 0
    requests_count: int = 0
    failed_requests: int = 0
    successful_requests: int = 0
    last_activity: Optional[float] = None
    last_cleanup: Optional[float] = None
    cleanup_count: int = 0
    recreation_count: int = 0


class ConnectionManager:
    """HTTP连接池管理器

    负责管理HTTP连接池，提供连接复用、统计监控和健康检查功能。
    支持配置化的连接池参数，确保资源的有效利用。
    """

    def __init__(self, config: WeiboConfig, logger: Optional[logging.Logger] = None):
        """初始化连接管理器

        Args:
            config: 微博配置对象
            logger: 可选的日志记录器

        Raises:
            ConfigError: 当配置参数无效时
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)

        # 验证配置参数
        self._validate_config()

        # 连接池相关
        self._client: Optional[httpx.AsyncClient] = None
        self._lock = asyncio.Lock()
        self._closed = False

        # 连接池管理
        self._connection_semaphore = asyncio.Semaphore(config.max_connections)
        self._cleanup_task: Optional[asyncio.Task] = None
        self._cleanup_interval = 60.0  # 清理间隔60秒

        # 统计信息
        self._stats = ConnectionStats()
        self._creation_time = time.time()

        # 清理任务将在第一次获取客户端时启动
        # 避免在初始化时创建任务，因为可能没有事件循环

        self.logger.info(
            f"ConnectionManager初始化完成，连接池大小: {config.connection_pool_size}, "
            f"最大连接数: {config.max_connections}, "
            f"Keep-Alive过期时间: {config.keepalive_expiry}秒"
        )

    def _validate_config(self) -> None:
        """验证配置参数

        Raises:
            ConfigError: 当配置参数无效时
        """
        if self.config.connection_pool_size <= 0:
            raise ConfigError("connection_pool_size必须大于0")

        if self.config.max_connections <= 0:
            raise ConfigError("max_connections必须大于0")

        if self.config.connection_pool_size > self.config.max_connections:
            raise ConfigError("connection_pool_size不能大于max_connections")

        if self.config.keepalive_expiry <= 0:
            raise ConfigError("keepalive_expiry必须大于0")

        if self.config.timeout <= 0:
            raise ConfigError("timeout必须大于0")

    async def get_client(self) -> httpx.AsyncClient:
        """获取HTTP客户端实例

        使用单例模式确保连接池的复用，支持连接数限制。

        Returns:
            httpx.AsyncClient: HTTP客户端实例

        Raises:
            NetworkError: 当连接管理器已关闭时
            ConnectionPoolError: 当连接池资源不足时
        """
        if self._closed:
            raise NetworkError("连接管理器已关闭")

        # 获取连接信号量，限制并发连接数
        try:
            await asyncio.wait_for(
                self._connection_semaphore.acquire(), timeout=self.config.timeout
            )
        except asyncio.TimeoutError:
            raise ConnectionPoolError("获取连接超时，连接池可能已满")

        try:
            if self._client is None:
                async with self._lock:
                    if self._client is None:
                        await self._create_client()
                        # 启动清理任务
                        self._start_cleanup_task()

            # 检查客户端是否仍然有效
            if self._client is not None and self._client.is_closed:
                async with self._lock:
                    await self._recreate_client()

            # 更新统计信息
            self._stats.requests_count += 1
            self._stats.last_activity = time.time()

            if self._client is None:
                raise ConnectionPoolError("客户端创建失败")
            return self._client

        except Exception as e:
            # 释放信号量
            self._connection_semaphore.release()
            raise

    async def _create_client(self) -> None:
        """创建HTTP客户端实例"""
        try:
            # 配置连接池限制
            limits = httpx.Limits(
                max_keepalive_connections=self.config.connection_pool_size,
                max_connections=self.config.max_connections,
                keepalive_expiry=self.config.keepalive_expiry,
            )

            # 配置超时
            timeout = httpx.Timeout(
                connect=self.config.timeout,
                read=self.config.timeout,
                write=self.config.timeout,
                pool=self.config.timeout,
            )

            # 创建客户端
            self._client = httpx.AsyncClient(
                limits=limits,
                timeout=timeout,
                headers=self._get_default_headers(),
                follow_redirects=True,
            )

            # 更新统计信息
            self._stats.created_connections += 1
            self._stats.total_connections = 1

            self.logger.info(
                f"HTTP客户端创建成功 - "
                f"Keep-Alive连接数: {self.config.connection_pool_size}, "
                f"最大连接数: {self.config.max_connections}"
            )

        except Exception as e:
            self.logger.error(f"创建HTTP客户端失败: {e}")
            raise NetworkError(f"无法创建HTTP客户端: {e}")

    async def _recreate_client(self) -> None:
        """重新创建HTTP客户端实例"""
        self.logger.warning("检测到客户端已关闭，正在重新创建...")

        # 关闭旧客户端
        if self._client is not None:
            try:
                await self._client.aclose()
            except Exception as e:
                self.logger.warning(f"关闭旧客户端时出错: {e}")
            finally:
                self._client = None

        # 创建新客户端
        await self._create_client()
        self._stats.recreation_count += 1
        self.logger.info("HTTP客户端重新创建成功")

    def _get_default_headers(self) -> Dict[str, str]:
        """获取默认请求头

        Returns:
            默认请求头字典
        """
        return {
            "User-Agent": self.config.user_agent,
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
        }

    def _start_cleanup_task(self) -> None:
        """启动连接清理任务"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            self.logger.debug("连接清理任务已启动")

    async def _cleanup_loop(self) -> None:
        """连接清理循环任务"""
        while not self._closed:
            try:
                await asyncio.sleep(self._cleanup_interval)
                await self._cleanup_connections()
            except asyncio.CancelledError:
                self.logger.debug("连接清理任务被取消")
                break
            except Exception as e:
                self.logger.error(f"连接清理任务出错: {e}")
                # 继续运行，不因为单次错误而停止清理任务

    async def _cleanup_connections(self) -> None:
        """清理过期连接"""
        if self._client is None or self._closed:
            return

        try:
            # 检查客户端状态
            if self._client.is_closed:
                self.logger.info("检测到客户端已关闭，将在下次请求时重新创建")
                return

            # 检查最后活动时间
            if self._stats.last_activity:
                inactive_time = time.time() - self._stats.last_activity
                # 如果长时间无活动，考虑关闭连接以释放资源
                if inactive_time > self.config.keepalive_expiry * 2:
                    self.logger.info(
                        f"连接池长时间无活动({inactive_time:.1f}秒)，保持当前状态"
                    )

            # 更新清理统计
            self._stats.last_cleanup = time.time()
            self._stats.cleanup_count += 1
            self.logger.debug("连接清理检查完成")

        except Exception as e:
            self.logger.error(f"清理连接时出错: {e}")

    async def close(self) -> None:
        """关闭连接池

        优雅地关闭所有连接并释放资源。
        """
        if self._closed:
            return

        self._closed = True

        # 取消清理任务
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                self.logger.error(f"取消清理任务时出错: {e}")

        # 关闭HTTP客户端
        async with self._lock:
            if self._client is not None:
                try:
                    await self._client.aclose()
                    self._stats.closed_connections += 1
                    self.logger.info("HTTP客户端已关闭")
                except Exception as e:
                    self.logger.error(f"关闭HTTP客户端时出错: {e}")
                finally:
                    self._client = None

            self._stats.total_connections = 0
            self._stats.active_connections = 0
            self._stats.idle_connections = 0

        self.logger.info("ConnectionManager已完全关闭")

    def record_request_success(self) -> None:
        """记录请求成功"""
        self._stats.successful_requests += 1
        self._stats.last_activity = time.time()

    def record_request_failure(self) -> None:
        """记录请求失败"""
        self._stats.failed_requests += 1
        self._stats.last_activity = time.time()

    def get_connection_info(self) -> Dict[str, Any]:
        """获取连接信息摘要

        Returns:
            连接信息摘要字典
        """
        return {
            "pool_size": self.config.connection_pool_size,
            "max_connections": self.config.max_connections,
            "keepalive_expiry": self.config.keepalive_expiry,
            "is_active": not self._closed and self._client is not None,
            "requests_handled": self._stats.requests_count,
            "success_rate": (
                self._stats.successful_requests
                / max(1, self._stats.successful_requests + self._stats.failed_requests)
            ),
        }

    def get_stats(self) -> Dict[str, Any]:
        """获取连接池统计信息

        Returns:
            包含连接池统计信息的字典
        """
        current_time = time.time()
        uptime = current_time - self._creation_time

        # 估算活跃和空闲连接数
        if self._client is not None and not self._closed:
            # 基于最近活动时间估算连接状态
            if self._stats.last_activity:
                time_since_activity = current_time - self._stats.last_activity
                if time_since_activity < 30:  # 30秒内有活动认为有活跃连接
                    estimated_active = 1
                    estimated_idle = max(0, self.config.connection_pool_size - 1)
                else:
                    estimated_active = 0
                    estimated_idle = self.config.connection_pool_size
            else:
                estimated_active = 0
                estimated_idle = self.config.connection_pool_size
        else:
            estimated_active = 0
            estimated_idle = 0

        self._stats.active_connections = estimated_active
        self._stats.idle_connections = estimated_idle

        # 计算成功率
        total_requests = self._stats.successful_requests + self._stats.failed_requests
        success_rate = (
            self._stats.successful_requests / total_requests
            if total_requests > 0
            else 0.0
        )

        return {
            # 连接统计
            "total_connections": self._stats.total_connections,
            "active_connections": self._stats.active_connections,
            "idle_connections": self._stats.idle_connections,
            "created_connections": self._stats.created_connections,
            "closed_connections": self._stats.closed_connections,
            "recreation_count": self._stats.recreation_count,
            # 请求统计
            "requests_count": self._stats.requests_count,
            "successful_requests": self._stats.successful_requests,
            "failed_requests": self._stats.failed_requests,
            "success_rate": success_rate,
            # 配置信息
            "pool_size": self.config.connection_pool_size,
            "max_connections": self.config.max_connections,
            "keepalive_expiry": self.config.keepalive_expiry,
            # 时间统计
            "uptime_seconds": uptime,
            "last_activity": self._stats.last_activity,
            "last_cleanup": self._stats.last_cleanup,
            "cleanup_count": self._stats.cleanup_count,
            # 状态信息
            "is_closed": self._closed,
            "client_is_closed": self._client.is_closed if self._client else True,
            "semaphore_value": self._connection_semaphore._value,
        }

    async def health_check(self) -> Dict[str, Any]:
        """执行健康检查

        验证连接池是否正常工作，返回详细的健康状态信息。

        Returns:
            Dict[str, Any]: 包含健康检查结果的字典
        """
        health_status: Dict[str, Any] = {
            "healthy": False,
            "timestamp": time.time(),
            "checks": {},
            "errors": [],
            "stats": {},
        }

        try:
            # 检查1: 连接管理器状态
            if self._closed:
                health_status["checks"]["manager_status"] = False
                health_status["errors"].append("连接管理器已关闭")
            else:
                health_status["checks"]["manager_status"] = True

            # 检查2: HTTP客户端状态
            if self._client is None:
                health_status["checks"]["client_exists"] = False
                health_status["errors"].append("HTTP客户端未创建")
            else:
                health_status["checks"]["client_exists"] = True

                # 检查客户端是否已关闭
                if self._client.is_closed:
                    health_status["checks"]["client_active"] = False
                    health_status["errors"].append("HTTP客户端已关闭")
                else:
                    health_status["checks"]["client_active"] = True

            # 检查3: 信号量状态
            semaphore_available = self._connection_semaphore._value
            if semaphore_available <= 0:
                health_status["checks"]["semaphore_available"] = False
                health_status["errors"].append("连接信号量已耗尽")
            else:
                health_status["checks"]["semaphore_available"] = True

            # 检查4: 清理任务状态
            if self._cleanup_task is None or self._cleanup_task.done():
                if not self._closed:  # 只有在未关闭时才认为这是问题
                    health_status["checks"]["cleanup_task"] = False
                    health_status["errors"].append("清理任务未运行")
                else:
                    health_status["checks"]["cleanup_task"] = True
            else:
                health_status["checks"]["cleanup_task"] = True

            # 检查5: 最近活动检查
            if self._stats.last_activity:
                inactive_time = time.time() - self._stats.last_activity
                if inactive_time > 300:  # 5分钟无活动
                    health_status["checks"]["recent_activity"] = False
                    health_status["errors"].append(
                        f"长时间无活动: {inactive_time:.1f}秒"
                    )
                else:
                    health_status["checks"]["recent_activity"] = True
            else:
                health_status["checks"]["recent_activity"] = True  # 初始状态

            # 综合健康状态
            all_checks_passed = all(health_status["checks"].values())
            health_status["healthy"] = all_checks_passed and not health_status["errors"]

            # 添加统计信息
            health_status["stats"] = self.get_stats()

            if health_status["healthy"]:
                self.logger.debug("连接池健康检查通过")
            else:
                self.logger.warning(f"连接池健康检查失败: {health_status['errors']}")

            return health_status

        except Exception as e:
            health_status["checks"]["health_check_execution"] = False
            health_status["errors"].append(f"健康检查执行失败: {e}")
            self.logger.error(f"健康检查执行失败: {e}")
            return health_status

    async def __aenter__(self) -> "ConnectionManager":
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """异步上下文管理器出口"""
        await self.close()

    def __repr__(self) -> str:
        """返回对象的字符串表示"""
        return (
            f"ConnectionManager("
            f"pool_size={self.config.connection_pool_size}, "
            f"max_connections={self.config.max_connections}, "
            f"closed={self._closed})"
        )
