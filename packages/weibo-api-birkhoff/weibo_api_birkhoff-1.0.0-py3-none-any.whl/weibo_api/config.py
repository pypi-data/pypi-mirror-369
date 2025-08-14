"""
微博 API 配置模块

提供客户端配置管理功能。
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class WeiboConfig:
    """微博客户端配置类

    包含所有客户端运行所需的配置参数，如超时时间、重试次数、速率限制等。
    """

    # 网络请求配置
    timeout: float = 10.0
    max_retries: int = 3
    retry_delay: float = 1.0

    # 速率限制配置
    rate_limit_calls: int = 100
    rate_limit_window: int = 60  # 秒

    # Cookie 管理配置
    cookie_validation_interval: float = 300.0  # Cookie 验证缓存时间（秒），默认5分钟
    max_cookie_generation_failures: int = 3
    cookie_cooldown_duration: float = 300.0  # Cookie生成失败冷却时间（秒）
    heavy_validation_url: str = "https://weibo.com/ajax/profile/info?uid=1"

    # 熔断器配置
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: float = 60.0
    circuit_breaker_half_open_max_calls: int = 3

    # 连接池配置
    connection_pool_size: int = 20
    max_connections: int = 100
    keepalive_expiry: float = 30.0

    # 边界检查配置
    enable_boundary_checks: bool = True
    max_memory_usage_percent: float = 90.0

    # 指标收集配置
    enable_metrics: bool = True
    metrics_max_history: int = 10000

    # 请求头配置
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )

    # API 端点配置
    visitor_url: str = "https://passport.weibo.com/visitor/genvisitor2"
    base_url: str = "https://weibo.com"
    mobile_url: str = "https://m.weibo.cn"

    def __post_init__(self) -> None:
        """配置验证"""
        if self.timeout <= 0:
            raise ValueError("timeout 必须大于 0")
        if self.max_retries < 0:
            raise ValueError("max_retries 必须大于等于 0")
        if self.retry_delay < 0:
            raise ValueError("retry_delay 必须大于等于 0")
        if self.rate_limit_calls <= 0:
            raise ValueError("rate_limit_calls 必须大于 0")
        if self.rate_limit_window <= 0:
            raise ValueError("rate_limit_window 必须大于 0")
        if self.cookie_validation_interval < 0:
            raise ValueError("cookie_validation_interval 必须大于等于 0")
        if self.max_cookie_generation_failures <= 0:
            raise ValueError("max_cookie_generation_failures 必须大于 0")
        if self.cookie_cooldown_duration < 0:
            raise ValueError("cookie_cooldown_duration 必须大于等于 0")
        if self.circuit_breaker_threshold <= 0:
            raise ValueError("circuit_breaker_threshold 必须大于 0")
        if self.circuit_breaker_timeout <= 0:
            raise ValueError("circuit_breaker_timeout 必须大于 0")
        if self.connection_pool_size <= 0:
            raise ValueError("connection_pool_size 必须大于 0")
        if self.max_connections <= 0:
            raise ValueError("max_connections 必须大于 0")
        if not (0 < self.max_memory_usage_percent <= 100):
            raise ValueError("max_memory_usage_percent 必须在 0-100 之间")

    @classmethod
    def create_fast_config(cls) -> "WeiboConfig":
        """创建快速配置（较少重试，较短超时，较短Cookie缓存）"""
        return cls(
            timeout=5.0,
            max_retries=1,
            retry_delay=0.5,
            rate_limit_calls=200,
            rate_limit_window=60,
            cookie_validation_interval=120.0,  # 2分钟
            cookie_cooldown_duration=120.0,  # 2分钟冷却
            circuit_breaker_threshold=3,
            circuit_breaker_timeout=30.0,
            connection_pool_size=10,
            max_connections=50,
        )

    @classmethod
    def create_conservative_config(cls) -> "WeiboConfig":
        """创建保守配置（更多重试，更长超时，更长Cookie缓存）"""
        return cls(
            timeout=15.0,
            max_retries=5,
            retry_delay=2.0,
            rate_limit_calls=50,
            rate_limit_window=60,
            cookie_validation_interval=600.0,  # 10分钟
            cookie_cooldown_duration=600.0,  # 10分钟冷却
            circuit_breaker_threshold=8,
            circuit_breaker_timeout=120.0,
            connection_pool_size=30,
            max_connections=150,
        )
