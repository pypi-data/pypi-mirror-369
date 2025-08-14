"""
微博 API 异常定义模块

定义了所有微博 API 相关的异常类型，提供统一的错误处理机制。
"""

from enum import Enum
from typing import Optional


class RequestStatus(Enum):
    """请求状态枚举"""

    SUCCESS = "success"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"
    AUTH_ERROR = "auth_error"


class WeiboError(Exception):
    """微博 API 基础异常"""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(WeiboError):
    """认证错误 - 当 Cookie 无效或认证失败时抛出"""

    pass


class RateLimitError(WeiboError):
    """速率限制错误 - 当请求过于频繁时抛出"""

    def __init__(self, message: str, retry_after: Optional[float] = None):
        super().__init__(message)
        self.retry_after = retry_after


class NetworkError(WeiboError):
    """网络错误 - 当网络请求失败时抛出"""

    pass


class ParseError(WeiboError):
    """解析错误 - 当响应数据解析失败时抛出"""

    pass


class ConfigError(WeiboError):
    """配置错误 - 当配置参数无效时抛出"""

    pass


class CircuitBreakerOpenError(WeiboError):
    """熔断器开启异常"""

    pass


class ResourceError(WeiboError):
    """资源不足异常"""

    pass


class CookieGenerationError(WeiboError):
    """Cookie生成异常"""

    pass


class ConnectionPoolError(WeiboError):
    """连接池相关错误"""

    pass


class DependencyError(WeiboError):
    """依赖注入相关错误"""

    pass
