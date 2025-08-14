"""
重试管理器模块

提供统一的重试管理功能，支持指数退避算法和基于异常类型的重试策略。
避免重试叠加问题，提供智能的重试决策机制。
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, Optional, Type, Union

import httpx

from .config import WeiboConfig
from .exceptions import (
    AuthenticationError,
    CircuitBreakerOpenError,
    CookieGenerationError,
    NetworkError,
    ParseError,
    RateLimitError,
    ResourceError,
    WeiboError,
)


class RetryDecision(Enum):
    """重试决策枚举"""

    RETRY = "retry"
    NO_RETRY = "no_retry"
    RETRY_WITH_DELAY = "retry_with_delay"


@dataclass
class RetryAttempt:
    """重试尝试信息"""

    attempt_number: int
    total_attempts: int
    last_error: Optional[Exception]
    elapsed_time: float
    next_delay: float


class RetryStrategy:
    """重试策略基类"""

    def should_retry(self, error: Exception, attempt: RetryAttempt) -> RetryDecision:
        """判断是否应该重试"""
        raise NotImplementedError

    def calculate_delay(self, attempt: RetryAttempt) -> float:
        """计算重试延迟时间"""
        raise NotImplementedError


class ExponentialBackoffStrategy(RetryStrategy):
    """指数退避重试策略"""

    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
    ):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter

    def should_retry(self, error: Exception, attempt: RetryAttempt) -> RetryDecision:
        """基于异常类型决定是否重试"""
        # 认证错误 - 只重试一次（可能是Cookie过期）
        # 注意：这里判断的是当前尝试次数，如果是第1次遇到认证错误就重试
        if isinstance(error, AuthenticationError):
            return (
                RetryDecision.RETRY
                if attempt.attempt_number <= 2
                else RetryDecision.NO_RETRY
            )

        # 速率限制错误 - 重试但需要延迟
        if isinstance(error, RateLimitError):
            return (
                RetryDecision.RETRY_WITH_DELAY
                if attempt.attempt_number <= 2
                else RetryDecision.NO_RETRY
            )

        # 网络错误 - 可以重试
        if isinstance(error, NetworkError):
            return RetryDecision.RETRY

        # HTTP状态错误
        if isinstance(error, httpx.HTTPStatusError):
            status_code = error.response.status_code

            # 5xx服务器错误 - 可以重试
            if 500 <= status_code < 600:
                return RetryDecision.RETRY

            # 429速率限制 - 重试但需要延迟
            if status_code == 429:
                return (
                    RetryDecision.RETRY_WITH_DELAY
                    if attempt.attempt_number <= 2
                    else RetryDecision.NO_RETRY
                )

            # 401认证错误 - 前2次重试
            if status_code == 401:
                return (
                    RetryDecision.RETRY
                    if attempt.attempt_number <= 2
                    else RetryDecision.NO_RETRY
                )

            # 其他4xx错误 - 不重试
            if 400 <= status_code < 500:
                return RetryDecision.NO_RETRY

        # HTTP请求错误（网络问题）- 可以重试
        if isinstance(error, httpx.RequestError):
            return RetryDecision.RETRY

        # 熔断器开启 - 不重试
        if isinstance(error, CircuitBreakerOpenError):
            return RetryDecision.NO_RETRY

        # 资源不足 - 不重试
        if isinstance(error, ResourceError):
            return RetryDecision.NO_RETRY

        # Cookie生成错误 - 重试一次
        if isinstance(error, CookieGenerationError):
            return (
                RetryDecision.RETRY
                if attempt.attempt_number == 1
                else RetryDecision.NO_RETRY
            )

        # 解析错误 - 不重试
        if isinstance(error, ParseError):
            return RetryDecision.NO_RETRY

        # 其他未知错误 - 不重试
        return RetryDecision.NO_RETRY

    def calculate_delay(self, attempt: RetryAttempt) -> float:
        """计算指数退避延迟时间"""
        # 基础延迟 * 退避因子^(尝试次数-1)
        delay = self.base_delay * (self.backoff_factor ** (attempt.attempt_number - 1))

        # 限制最大延迟
        delay = min(delay, self.max_delay)

        # 添加抖动以避免雷群效应
        if self.jitter:
            import random

            delay = delay * (0.5 + random.random() * 0.5)

        return delay


class RetryManager:
    """统一的重试管理器

    提供统一的重试逻辑，支持指数退避算法和基于异常类型的重试策略。
    避免重试叠加问题，确保每个API调用只有一层重试逻辑。
    """

    def __init__(
        self,
        config: WeiboConfig,
        logger: Optional[logging.Logger] = None,
        strategy: Optional[RetryStrategy] = None,
    ):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.strategy = strategy or ExponentialBackoffStrategy(
            base_delay=config.retry_delay,
            max_delay=60.0,
            backoff_factor=2.0,
            jitter=True,
        )

        # 重试统计
        self._retry_stats: Dict[str, int] = {
            "total_attempts": 0,
            "successful_retries": 0,
            "failed_retries": 0,
            "no_retry_decisions": 0,
        }

    async def execute_with_retry(
        self, func: Callable, *args: Any, max_attempts: Optional[int] = None, **kwargs: Any
    ) -> Any:
        """执行函数并在失败时进行重试

        Args:
            func: 要执行的函数
            *args: 函数参数
            max_attempts: 最大尝试次数，默认使用配置中的值
            **kwargs: 函数关键字参数

        Returns:
            函数执行结果

        Raises:
            最后一次执行的异常
        """
        max_attempts = (
            max_attempts or self.config.max_retries + 1
        )  # +1 因为包含初始尝试
        start_time = time.time()
        last_error = None

        for attempt_number in range(1, max_attempts + 1):
            try:
                self._retry_stats["total_attempts"] += 1

                # 记录重试尝试
                if attempt_number > 1:
                    self.logger.info(
                        f"重试执行 {func.__name__} (第 {attempt_number}/{max_attempts} 次尝试)"
                    )

                # 执行函数
                result = await self._execute_function(func, *args, **kwargs)

                # 成功执行
                if attempt_number > 1:
                    self._retry_stats["successful_retries"] += 1
                    self.logger.info(
                        f"重试成功: {func.__name__} 在第 {attempt_number} 次尝试后成功"
                    )

                return result

            except Exception as error:
                last_error = error
                elapsed_time = time.time() - start_time

                # 创建重试尝试信息
                retry_attempt = RetryAttempt(
                    attempt_number=attempt_number,
                    total_attempts=max_attempts,
                    last_error=error,
                    elapsed_time=elapsed_time,
                    next_delay=0.0,
                )

                # 如果是最后一次尝试，直接抛出异常
                if attempt_number >= max_attempts:
                    self._retry_stats["failed_retries"] += 1
                    self.logger.error(
                        f"重试失败: {func.__name__} 在 {max_attempts} 次尝试后仍然失败，"
                        f"最后错误: {error}"
                    )
                    raise error

                # 判断是否应该重试
                retry_decision = self.should_retry(error, retry_attempt)

                if retry_decision == RetryDecision.NO_RETRY:
                    self._retry_stats["no_retry_decisions"] += 1
                    self.logger.warning(
                        f"不重试: {func.__name__} 遇到不可重试的错误: {error}"
                    )
                    raise error

                # 计算延迟时间
                delay = self.calculate_delay(retry_attempt)
                retry_attempt.next_delay = delay

                # 记录重试决策
                self.logger.warning(
                    f"重试决策: {func.__name__} 遇到错误 {type(error).__name__}: {error}, "
                    f"将在 {delay:.2f} 秒后进行第 {attempt_number + 1} 次尝试"
                )

                # 等待延迟时间
                if delay > 0:
                    await asyncio.sleep(delay)

        # 理论上不应该到达这里
        if last_error:
            raise last_error
        else:
            raise RuntimeError("重试逻辑异常：未知错误")

    async def _execute_function(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """执行函数，支持同步和异步函数"""
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    def should_retry(self, error: Exception, attempt: RetryAttempt) -> RetryDecision:
        """判断是否应该重试

        Args:
            error: 发生的异常
            attempt: 重试尝试信息

        Returns:
            重试决策
        """
        return self.strategy.should_retry(error, attempt)

    def calculate_delay(self, attempt: RetryAttempt) -> float:
        """计算重试延迟时间

        Args:
            attempt: 重试尝试信息

        Returns:
            延迟时间（秒）
        """
        return self.strategy.calculate_delay(attempt)

    def get_retry_stats(self) -> Dict[str, Any]:
        """获取重试统计信息

        Returns:
            重试统计信息字典
        """
        total_attempts = self._retry_stats["total_attempts"]
        successful_retries = self._retry_stats["successful_retries"]

        return {
            "total_attempts": total_attempts,
            "successful_retries": successful_retries,
            "failed_retries": self._retry_stats["failed_retries"],
            "no_retry_decisions": self._retry_stats["no_retry_decisions"],
            "retry_success_rate": (
                successful_retries / max(total_attempts - successful_retries, 1) * 100
                if total_attempts > successful_retries
                else 0.0
            ),
            "strategy_type": type(self.strategy).__name__,
        }

    def reset_stats(self) -> None:
        """重置重试统计信息"""
        self._retry_stats = {
            "total_attempts": 0,
            "successful_retries": 0,
            "failed_retries": 0,
            "no_retry_decisions": 0,
        }
        self.logger.info("重试统计信息已重置")


# 便利函数，用于快速创建RetryManager实例
def create_retry_manager(
    config: Optional[WeiboConfig] = None,
    logger: Optional[logging.Logger] = None,
    **strategy_kwargs: Any,
) -> RetryManager:
    """创建RetryManager实例的便利函数

    Args:
        config: 微博配置对象
        logger: 日志记录器
        **strategy_kwargs: 重试策略参数

    Returns:
        RetryManager实例
    """
    config = config or WeiboConfig()
    strategy = (
        ExponentialBackoffStrategy(**strategy_kwargs) if strategy_kwargs else None
    )
    return RetryManager(config, logger, strategy)
