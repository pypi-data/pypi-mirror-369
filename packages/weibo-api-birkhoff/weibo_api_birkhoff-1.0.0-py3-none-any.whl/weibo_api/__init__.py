"""
微博 API 客户端模块

提供同步和异步的微博数据获取功能，包括：
- 用户信息获取
- 微博时间线获取
- 微博详情获取
- 微博评论获取

主要类：
- WeiboClient: 同步客户端
- AsyncWeiboClient: 异步客户端（Facade层，推荐使用）
- AsyncWeiboRawClient: 异步原始客户端（底层API）
- WeiboDataMapper: 数据映射器（防腐层）
- WeiboConfig: 配置类

主要异常：
- WeiboError: 基础异常
- AuthenticationError: 认证错误
- RateLimitError: 速率限制错误
- NetworkError: 网络错误
- ParseError: 解析错误

数据模型：
- WeiboUser: 用户模型
- WeiboPost: 微博模型
- WeiboComment: 评论模型
- WeiboImage: 图片模型
- WeiboVideo: 视频模型

工具类：
- RateLimiter: 速率限制器
- retry_on_failure: 重试装饰器
"""

from .async_client import AsyncWeiboRawClient

# 导入客户端
from .client import WeiboClient

# 导入配置
from .config import WeiboConfig

# 导入连接管理器
from .connection_manager import ConnectionManager

# 导入依赖注入容器
from .dependency_container import DependencyContainer

# 导入异常
from .exceptions import (
    AuthenticationError,
    ConfigError,
    ConnectionPoolError,
    DependencyError,
    NetworkError,
    ParseError,
    RateLimitError,
    RequestStatus,
    WeiboError,
)
from .facade_client import AsyncWeiboClient

# 导入映射器
from .mapper import WeiboDataMapper

# 导入指标收集器
from .metrics_collector import MetricsCollector, create_metrics_collector

# 导入数据模型
from .models import (  # 核心模型; 辅助模型; 响应模型
    ApiResponse,
    BaseContent,
    ImageInfo,
    PostCommentsResponse,
    PostDetailResponse,
    UserDetailResponse,
    UserTimelineResponse,
    VideoPlaybackInfo,
    WeiboComment,
    WeiboImage,
    WeiboPost,
    WeiboUser,
    WeiboVideo,
)

# 导入重试管理器
from .retry_manager import RetryManager, create_retry_manager

# 导入工具类
from .utils import (
    RateLimiter,
    clean_text,
    ensure_cookie_is_valid,
    format_count,
    is_valid_cookie,
    retry_on_failure,
    setup_logger,
    validate_user_id,
    validate_weibo_id,
)

__version__ = "1.0.0"
__author__ = "Weibo API Team"
__description__ = "高性能微博 API 客户端，支持同步和异步调用"

__all__ = [
    # 客户端
    "WeiboClient",
    "AsyncWeiboClient",
    "AsyncWeiboRawClient",
    # 映射器
    "WeiboDataMapper",
    # 配置
    "WeiboConfig",
    # 异常
    "WeiboError",
    "AuthenticationError",
    "RateLimitError",
    "NetworkError",
    "ParseError",
    "RequestStatus",
    "ConfigError",
    "ConnectionPoolError",
    "DependencyError",
    # 核心数据模型
    "WeiboUser",
    "WeiboPost",
    "WeiboComment",
    "WeiboImage",
    "WeiboVideo",
    # 辅助模型
    "ImageInfo",
    "VideoPlaybackInfo",
    "BaseContent",
    # 响应模型
    "UserTimelineResponse",
    "PostDetailResponse",
    "UserDetailResponse",
    "PostCommentsResponse",
    "ApiResponse",
    # 工具类
    "RateLimiter",
    "retry_on_failure",
    "ensure_cookie_is_valid",
    "setup_logger",
    "validate_user_id",
    "validate_weibo_id",
    "clean_text",
    "format_count",
    "is_valid_cookie",
    # 连接管理器
    "ConnectionManager",
    # 依赖注入容器
    "DependencyContainer",
    # 重试管理器
    "RetryManager",
    "create_retry_manager",
    # 指标收集器
    "MetricsCollector",
    "create_metrics_collector",
]
