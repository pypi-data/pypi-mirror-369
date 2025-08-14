"""
微博 API 工具模块

提供可复用的工具类和函数，包括速率限制器、重试装饰器、Cookie 验证等。
"""

import asyncio
import functools
import logging
import socket
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional, Tuple, TypeVar

import httpx

from .exceptions import NetworkError, RateLimitError

# 类型别名
F = TypeVar("F", bound=Callable[..., Any])


class CookieState(Enum):
    """Cookie状态枚举"""

    VALID = "valid"
    INVALID = "invalid"
    GENERATING = "generating"
    FAILED = "failed"
    COOLDOWN = "cooldown"


@dataclass
class RetryContext:
    """重试上下文"""

    attempt_count: int = 0
    max_attempts: int = 3
    is_retry: bool = False
    last_error: Optional[Exception] = None

    def next_attempt(self) -> "RetryContext":
        return RetryContext(
            attempt_count=self.attempt_count + 1,
            max_attempts=self.max_attempts,
            is_retry=True,
            last_error=self.last_error,
        )


class CircuitBreakerOpenError(Exception):
    """熔断器开启异常"""

    pass


class ResourceError(Exception):
    """资源不足异常"""

    pass


class CircuitBreaker:
    """熔断器实现"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 3,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self._half_open_calls = 0
        self._lock = asyncio.Lock()

    def is_open(self) -> bool:
        """检查熔断器是否开启"""
        return self._state == "OPEN"

    def _should_attempt_reset(self) -> bool:
        """检查是否应该尝试重置熔断器"""
        if self._last_failure_time is None:
            return False
        return time.time() - self._last_failure_time >= self.recovery_timeout

    async def call(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """通过熔断器执行函数调用"""
        # 分离状态检查和状态修改，减少锁的持有时间
        should_execute, error_message = await self._check_and_prepare_execution()

        if not should_execute:
            raise CircuitBreakerOpenError(error_message)

        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure()
            raise

    async def _check_and_prepare_execution(self) -> Tuple[bool, str]:
        """检查是否可以执行并准备执行状态，返回(是否可执行, 错误消息)"""
        async with self._lock:
            if self._state == "OPEN":
                if self._should_attempt_reset():
                    self._state = "HALF_OPEN"
                    self._half_open_calls = 0
                else:
                    return False, "熔断器开启，服务暂时不可用"

            if self._state == "HALF_OPEN":
                if self._half_open_calls >= self.half_open_max_calls:
                    return False, "熔断器半开状态，已达到最大尝试次数"
                self._half_open_calls += 1

            return True, ""

    async def _on_success(self) -> None:
        """成功时的处理"""
        async with self._lock:
            self._failure_count = 0
            if self._state == "HALF_OPEN":
                self._state = "CLOSED"

    async def _on_failure(self) -> None:
        """失败时的处理"""
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()

            if self._failure_count >= self.failure_threshold:
                self._state = "OPEN"
            elif self._state == "HALF_OPEN":
                self._state = "OPEN"

    def record_failure(self) -> None:
        """记录失败（同步版本）"""
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._failure_count >= self.failure_threshold:
            self._state = "OPEN"


class BoundaryChecker:
    """边界条件检查器"""

    @staticmethod
    def validate_network_connectivity() -> bool:
        """检查网络连通性"""
        try:
            # 简单的连通性检查
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False

    @staticmethod
    def validate_memory_usage(max_percent: float = 90.0) -> bool:
        """检查内存使用情况"""
        try:
            import psutil

            memory_percent = psutil.virtual_memory().percent
            return bool(memory_percent < max_percent)
        except ImportError:
            # 如果psutil不可用，跳过内存检查
            return True

    @staticmethod
    def validate_input_parameters(user_id: Optional[str] = None, weibo_id: Optional[str] = None) -> None:
        """验证输入参数"""
        if user_id is not None:
            # 转换为字符串进行验证
            user_id_str = str(user_id)
            if not validate_user_id(user_id_str):
                raise ValueError(f"无效的用户ID: {user_id}")
        if weibo_id is not None:
            # 转换为字符串进行验证
            weibo_id_str = str(weibo_id)
            if not validate_weibo_id(weibo_id_str):
                raise ValueError(f"无效的微博ID: {weibo_id}")


# 为了向后兼容性，保留旧的ConnectionManager类
# 新代码应该使用 weibo_api.connection_manager.ConnectionManager
class ConnectionManager:
    """连接池管理器（已弃用，请使用 weibo_api.connection_manager.ConnectionManager）"""

    def __init__(self, config: Any) -> None:
        import warnings

        warnings.warn(
            "utils.ConnectionManager已弃用，请使用connection_manager.ConnectionManager",
            DeprecationWarning,
            stacklevel=2,
        )

        self.config = config
        self._client: Optional[httpx.AsyncClient] = None
        self._lock = asyncio.Lock()

    async def get_client(self) -> httpx.AsyncClient:
        """获取复用的HTTP客户端"""
        if self._client is None:
            async with self._lock:
                if self._client is None:
                    self._client = httpx.AsyncClient(
                        limits=httpx.Limits(
                            max_keepalive_connections=getattr(
                                self.config, "connection_pool_size", 20
                            ),
                            max_connections=getattr(
                                self.config, "max_connections", 100
                            ),
                            keepalive_expiry=getattr(
                                self.config, "keepalive_expiry", 30.0
                            ),
                        ),
                        timeout=httpx.Timeout(self.config.timeout),
                        headers=self._get_default_headers(),
                    )
        return self._client

    def _get_default_headers(self) -> dict[str, str]:
        """获取默认请求头"""
        return {
            "User-Agent": self.config.user_agent,
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }

    async def close(self) -> None:
        """关闭连接池"""
        if self._client:
            await self._client.aclose()
            self._client = None


class RateLimiter:
    """简单的速率限制器

    用于控制 API 请求频率，防止触发服务器的速率限制。
    """

    def __init__(self, calls: int, window: int) -> None:
        """
        初始化速率限制器

        Args:
            calls: 时间窗口内允许的最大请求次数
            window: 时间窗口大小（秒）
        """
        self.calls = calls
        self.window = window
        self.requests: list[float] = []

    def can_make_request(self) -> bool:
        """检查是否可以发起请求"""
        now = time.time()
        # 清理过期的请求记录
        self.requests = [
            req_time for req_time in self.requests if now - req_time < self.window
        ]

        if len(self.requests) >= self.calls:
            return False

        self.requests.append(now)
        return True

    def time_until_next_request(self) -> float:
        """计算下次可以请求的时间"""
        if len(self.requests) < self.calls:
            return 0.0

        oldest_request = min(self.requests)
        return self.window - (time.time() - oldest_request)


class ErrorHandler:
    """错误处理器"""

    def __init__(self, circuit_breaker: CircuitBreaker) -> None:
        self.circuit_breaker = circuit_breaker

    async def handle_api_error(self, error: Exception, context: RetryContext) -> bool:
        """处理API错误，返回是否应该重试"""

        if isinstance(error, httpx.HTTPStatusError):
            status_code = error.response.status_code

            if status_code == 401:
                # 认证错误 - 标记Cookie无效，允许重试一次
                return context.attempt_count == 0

            elif status_code == 429:
                # 速率限制 - 使用指数退避，但限制重试次数
                await self._handle_rate_limit(error.response)
                return context.attempt_count < 2

            elif 500 <= status_code < 600:
                # 服务器错误 - 触发熔断器
                self.circuit_breaker.record_failure()
                return not self.circuit_breaker.is_open()

            else:
                # 其他HTTP错误 - 不重试
                return False

        elif isinstance(error, httpx.RequestError):
            # 网络错误 - 允许重试
            return context.attempt_count < context.max_attempts

        else:
            # 未知错误 - 不重试
            return False

    async def _handle_rate_limit(self, response: httpx.Response) -> None:
        """处理速率限制"""
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                wait_time = float(retry_after)
                await asyncio.sleep(min(wait_time, 60))  # 最多等待60秒
            except ValueError:
                await asyncio.sleep(5)  # 默认等待5秒
        else:
            await asyncio.sleep(5)

    async def _handle_auth_error(self) -> None:
        """处理认证错误"""
        # 这里可以添加Cookie失效的处理逻辑
        pass


def simple_retry(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0) -> Callable:
    """简化的重试装饰器 - 仅用于非API调用的函数"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except (
                    httpx.RequestError,
                    httpx.HTTPStatusError,
                    ConnectionError,
                ) as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait_time = delay * (backoff**attempt)
                        await asyncio.sleep(wait_time)
                    else:
                        raise NetworkError(f"请求失败，已重试 {max_retries} 次: {e}")
                except Exception as e:
                    raise e
            if last_exception:
                raise last_exception
            else:
                raise RuntimeError("未知错误")

        return async_wrapper if asyncio.iscoroutinefunction(func) else func

    return decorator


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0) -> Callable:
    """简单的重试装饰器 - 已弃用，请使用RetryManager

    此装饰器已被弃用，为了避免重试叠加问题，请使用统一的RetryManager。
    """
    import warnings

    warnings.warn(
        "retry_on_failure装饰器已弃用，请使用RetryManager统一处理重试逻辑",
        DeprecationWarning,
        stacklevel=2,
    )

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (
                    httpx.RequestError,
                    httpx.HTTPStatusError,
                    ConnectionError,
                ) as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait_time = delay * (backoff**attempt)
                        time.sleep(wait_time)
                    else:
                        raise NetworkError(f"请求失败，已重试 {max_retries} 次: {e}")
                except Exception as e:
                    raise e
            if last_exception:
                raise last_exception
            else:
                raise RuntimeError("未知错误")

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except (
                    httpx.RequestError,
                    httpx.HTTPStatusError,
                    ConnectionError,
                ) as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait_time = delay * (backoff**attempt)
                        await asyncio.sleep(wait_time)
                    else:
                        raise NetworkError(f"请求失败，已重试 {max_retries} 次: {e}")
                except Exception as e:
                    raise e
            if last_exception:
                raise last_exception
            else:
                raise RuntimeError("未知错误")

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


def ensure_cookie_is_valid(func: F) -> F:
    """Cookie 验证装饰器

    确保在执行 API 调用前 Cookie 是有效的。
    """

    @functools.wraps(func)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        if not self._check_cookie_validity():
            self.logger.error("Cookie 校验失败或已过期，请求被中断。")
            return {"error": "Cookie 校验失败，请检查或重新生成。"}
        return func(self, *args, **kwargs)

    return wrapper  # type: ignore


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """设置日志记录器

    Args:
        name: 日志记录器名称
        level: 日志级别

    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def validate_user_id(user_id: str) -> bool:
    """验证用户 ID 格式

    Args:
        user_id: 用户 ID 字符串

    Returns:
        是否为有效的用户 ID
    """
    if not user_id or not isinstance(user_id, str):
        return False

    # 用户 ID 应该是数字字符串
    return user_id.isdigit() and len(user_id) > 0


def validate_weibo_id(weibo_id: str) -> bool:
    """验证微博 ID 格式

    Args:
        weibo_id: 微博 ID 字符串

    Returns:
        是否为有效的微博 ID
    """
    if not weibo_id or not isinstance(weibo_id, str):
        return False

    # 微博 ID 应该是数字字符串
    return weibo_id.isdigit() and len(weibo_id) > 0


def clean_text(text: str) -> str:
    """清理文本内容

    移除多余的空白字符和特殊字符。

    Args:
        text: 原始文本

    Returns:
        清理后的文本
    """
    if not text:
        return ""

    # 移除多余的空白字符
    text = " ".join(text.split())

    # 移除特殊的 Unicode 字符
    text = text.replace("\u200b", "")  # 零宽空格
    text = text.replace("\ufeff", "")  # BOM 字符

    return text.strip()


def format_count(count: int) -> str:
    """格式化数字显示

    将大数字格式化为易读的形式（如 1.2万、3.5亿）。

    Args:
        count: 数字

    Returns:
        格式化后的字符串
    """
    if count < 10000:
        return str(count)
    elif count < 100000000:
        return f"{count / 10000:.1f}万"
    else:
        return f"{count / 100000000:.1f}亿"


def is_valid_cookie(cookie: str) -> bool:
    """检查 Cookie 格式是否有效

    Args:
        cookie: Cookie 字符串

    Returns:
        Cookie 是否有效
    """
    if not cookie or not isinstance(cookie, str):
        return False

    # 检查是否包含必要的字段
    return "SUB=" in cookie and "SUBP=" in cookie
