"""
微博 API Facade 客户端模块

提供高级的异步微博客户端，采用Facade Pattern封装底层API调用。
使用Pydantic模型进行数据验证和类型安全，提供更好的开发体验。
"""

import logging
import time
from functools import wraps
from typing import Any, List, Optional

from pydantic import ValidationError

from .async_client import AsyncWeiboRawClient
from .config import WeiboConfig
from .exceptions import (
    AuthenticationError,
    CircuitBreakerOpenError,
    CookieGenerationError,
    DependencyError,
    NetworkError,
    ParseError,
    RateLimitError,
    ResourceError,
)
from .mapper import WeiboDataMapper
from .metrics_collector import MetricsCollector, create_metrics_collector
from .models import (
    UserProfileRawDTO,
    UserTimelineRawDTO,
    WeiboComment,
    WeiboCommentsRawDTO,
    WeiboDetailRawDTO,
    WeiboPost,
    WeiboUser,
)
from .utils import setup_logger


class AsyncWeiboClient:
    """异步微博客户端 (Facade层)

    提供高级的异步微博数据获取功能，采用Facade Pattern封装底层API调用。
    返回强类型的Pydantic模型，提供数据验证和类型安全。

    特性：
    - 类型安全：所有API返回强类型的Pydantic模型
    - 数据验证：自动验证API响应数据的完整性
    - 防腐层：隔离外部API变化对业务逻辑的影响
    - 易于使用：简化的API接口，隐藏底层复杂性
    """

    def __init__(
        self,
        cookies: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        config: Optional[WeiboConfig] = None,
        raw_client: Optional[AsyncWeiboRawClient] = None,
        mapper: Optional[WeiboDataMapper] = None,
        metrics_collector: Optional[MetricsCollector] = None,
    ) -> None:
        """
        初始化异步微博客户端

        Args:
            cookies: 可选的 Cookie 字符串
            logger: 可选的日志记录器
            config: 可选的配置对象
            raw_client: 可选的原始客户端实例（用于依赖注入）
            mapper: 可选的数据映射器实例（用于依赖注入）
            metrics_collector: 可选的指标收集器实例（用于依赖注入）

        Raises:
            DependencyError: 当注入的依赖项无效时
        """
        self.config = config or WeiboConfig()
        self.logger = logger or setup_logger(f"{__name__}.{self.__class__.__name__}")

        # 验证和初始化底层客户端
        if raw_client is not None:
            self._validate_raw_client(raw_client)
            self._raw_client = raw_client
            self.logger.debug("使用注入的raw_client")
        else:
            self._raw_client = AsyncWeiboRawClient(
                cookies=cookies, logger=self.logger, config=self.config
            )
            self.logger.debug("使用默认raw_client")

        # 验证和初始化数据映射器
        if mapper is not None:
            self._validate_mapper(mapper)
            self._mapper = mapper
            self.logger.debug("使用注入的mapper")
        else:
            self._mapper = WeiboDataMapper(logger=self.logger)
            self.logger.debug("使用默认mapper")

        # 初始化指标收集器
        if metrics_collector is not None:
            self._metrics_collector = metrics_collector
            self.logger.debug("使用注入的metrics_collector")
        else:
            self._metrics_collector = create_metrics_collector(
                enabled=self.config.enable_metrics,
                max_history=self.config.metrics_max_history,
            )
            self.logger.debug(
                f"使用默认metrics_collector (enabled={self.config.enable_metrics})"
            )

    async def _record_api_call(self, endpoint: str, func: Any, *args: Any, **kwargs: Any) -> Any:
        """记录API调用指标的辅助方法"""
        start_time = time.time()
        success = False
        error_type = None

        try:
            result = await func(*args, **kwargs)
            success = True
            return result
        except Exception as e:
            error_type = type(e).__name__
            raise
        finally:
            duration = time.time() - start_time
            self._metrics_collector.record_request(
                endpoint, duration, success, error_type
            )

    def _record_cache_hit(self, hit: bool) -> None:
        """记录缓存命中情况

        Args:
            hit: 是否命中缓存
        """
        self._metrics_collector.record_cache_hit(hit)

    async def get_user_profile(self, user_id: str) -> WeiboUser:
        """获取用户信息

        Args:
            user_id: 用户 ID

        Returns:
            WeiboUser: 用户信息模型

        Raises:
            ParseError: 当数据解析失败时
            NetworkError: 当网络请求失败时
            AuthenticationError: 当认证失败时
            RateLimitError: 当请求过于频繁时
            CircuitBreakerOpenError: 当服务熔断时
            ResourceError: 当资源不足时
        """

        async def _get_user_profile_impl() -> WeiboUser:
            try:
                self.logger.info(f"正在获取用户 {user_id} 的信息...")

                # 调用底层客户端获取原始数据
                raw_data = await self._raw_client.get_user_profile(user_id)

                # 解析为DTO模型
                raw_dto = UserProfileRawDTO(**raw_data)

                # 通过映射器转换为业务模型
                user = self._mapper.map_user_profile(raw_dto)

                self.logger.info(f"✅ 成功获取用户 {user.screen_name} 的信息")
                return user

            except ValidationError as e:
                # Pydantic验证错误转换
                self.logger.error(f"用户数据验证失败: {e}")
                raise ParseError(f"用户数据格式错误: {e}")

            except (
                NetworkError,
                AuthenticationError,
                RateLimitError,
                ParseError,
                CircuitBreakerOpenError,
                ResourceError,
                CookieGenerationError,
                DependencyError,
            ):
                # 已知业务异常直接传播
                raise

            except Exception as e:
                # 未知异常转换为业务异常
                self.logger.error(f"获取用户信息时发生未知错误: {e}")
                raise NetworkError(f"服务暂时不可用: {type(e).__name__}")

        result = await self._record_api_call("get_user_profile", _get_user_profile_impl)
        return result  # type: ignore

    async def get_user_timeline(self, user_id: str, page: int = 1) -> List[WeiboPost]:
        """获取用户时间线

        Args:
            user_id: 用户 ID
            page: 页码，默认为 1

        Returns:
            List[WeiboPost]: 微博列表

        Raises:
            ParseError: 当数据解析失败时
            NetworkError: 当网络请求失败时
            AuthenticationError: 当认证失败时
            RateLimitError: 当请求过于频繁时
            CircuitBreakerOpenError: 当服务熔断时
            ResourceError: 当资源不足时
        """

        async def _get_user_timeline_impl() -> list[WeiboPost]:
            try:
                self.logger.info(f"正在获取用户 {user_id} 的第 {page} 页时间线...")

                # 调用底层客户端获取原始数据
                raw_data = await self._raw_client.get_user_timeline(user_id, page)

                # 解析为DTO模型
                raw_dto = UserTimelineRawDTO(**raw_data)

                # 通过映射器转换为业务模型
                posts = self._mapper.map_user_timeline(raw_dto)

                self.logger.info(f"✅ 成功获取 {len(posts)} 条微博")
                return posts

            except ValidationError as e:
                self.logger.error(f"时间线数据验证失败: {e}")
                raise ParseError(f"时间线数据格式错误: {e}")

            except (
                NetworkError,
                AuthenticationError,
                RateLimitError,
                ParseError,
                CircuitBreakerOpenError,
                ResourceError,
                CookieGenerationError,
                DependencyError,
            ):
                raise

            except Exception as e:
                self.logger.error(f"获取用户时间线时发生未知错误: {e}")
                raise NetworkError(f"服务暂时不可用: {type(e).__name__}")

        result = await self._record_api_call("get_user_timeline", _get_user_timeline_impl)
        return result  # type: ignore

    async def get_weibo_detail(self, weibo_id: str) -> WeiboPost:
        """获取微博详情

        Args:
            weibo_id: 微博 ID

        Returns:
            WeiboPost: 微博详情模型

        Raises:
            ParseError: 当数据解析失败时
            NetworkError: 当网络请求失败时
            AuthenticationError: 当认证失败时
            RateLimitError: 当请求过于频繁时
            CircuitBreakerOpenError: 当服务熔断时
            ResourceError: 当资源不足时
        """

        async def _get_weibo_detail_impl() -> WeiboPost:
            try:
                self.logger.info(f"正在获取微博 {weibo_id} 的详情...")

                # 调用底层客户端获取原始数据
                raw_data = await self._raw_client.get_weibo_detail(weibo_id)

                # 解析为DTO模型
                raw_dto = WeiboDetailRawDTO(**raw_data)

                # 通过映射器转换为业务模型
                post = self._mapper.map_weibo_detail(raw_dto)

                self.logger.info(f"✅ 成功获取微博详情")
                return post

            except ValidationError as e:
                self.logger.error(f"微博详情数据验证失败: {e}")
                raise ParseError(f"微博详情数据格式错误: {e}")

            except (
                NetworkError,
                AuthenticationError,
                RateLimitError,
                ParseError,
                CircuitBreakerOpenError,
                ResourceError,
                CookieGenerationError,
                DependencyError,
            ):
                raise

            except Exception as e:
                self.logger.error(f"获取微博详情时发生未知错误: {e}")
                raise NetworkError(f"服务暂时不可用: {type(e).__name__}")

        result = await self._record_api_call("get_weibo_detail", _get_weibo_detail_impl)
        return result  # type: ignore

    async def get_weibo_comments(self, weibo_id: str) -> List[WeiboComment]:
        """获取微博评论

        Args:
            weibo_id: 微博 ID

        Returns:
            List[WeiboComment]: 评论列表

        Raises:
            ParseError: 当数据解析失败时
            NetworkError: 当网络请求失败时
            AuthenticationError: 当认证失败时
            RateLimitError: 当请求过于频繁时
            CircuitBreakerOpenError: 当服务熔断时
            ResourceError: 当资源不足时
        """

        async def _get_weibo_comments_impl() -> list[WeiboComment]:
            try:
                self.logger.info(f"正在获取微博 {weibo_id} 的评论...")

                # 调用底层客户端获取原始数据
                raw_data = await self._raw_client.get_weibo_comments(weibo_id)

                # 解析为DTO模型
                raw_dto = WeiboCommentsRawDTO(**raw_data)

                # 通过映射器转换为业务模型
                comments = self._mapper.map_weibo_comments(raw_dto)

                self.logger.info(f"✅ 成功获取 {len(comments)} 条评论")
                return comments

            except ValidationError as e:
                self.logger.error(f"评论数据验证失败: {e}")
                raise ParseError(f"评论数据格式错误: {e}")

            except (
                NetworkError,
                AuthenticationError,
                RateLimitError,
                ParseError,
                CircuitBreakerOpenError,
                ResourceError,
                CookieGenerationError,
                DependencyError,
            ):
                raise

            except Exception as e:
                self.logger.error(f"获取微博评论时发生未知错误: {e}")
                raise NetworkError(f"服务暂时不可用: {type(e).__name__}")

        result = await self._record_api_call(
            "get_weibo_comments", _get_weibo_comments_impl
        )
        return result  # type: ignore

    def _validate_raw_client(self, raw_client: AsyncWeiboRawClient) -> None:
        """验证注入的raw_client依赖

        Args:
            raw_client: 要验证的raw_client实例

        Raises:
            DependencyError: 当raw_client无效时
        """
        if not isinstance(raw_client, AsyncWeiboRawClient):
            raise DependencyError(
                f"注入的raw_client必须是AsyncWeiboRawClient实例，"
                f"实际类型: {type(raw_client).__name__}"
            )

        # 验证必要的方法是否存在且可调用
        required_methods = [
            "get_user_profile",
            "get_user_timeline",
            "get_weibo_detail",
            "get_weibo_comments",
        ]

        for method_name in required_methods:
            if not hasattr(raw_client, method_name):
                raise DependencyError(f"注入的raw_client缺少必要的方法: {method_name}")

            method = getattr(raw_client, method_name)
            if not callable(method):
                raise DependencyError(f"注入的raw_client的{method_name}不是可调用对象")

            # 额外检查：确保方法不是抽象方法或未实现的方法
            try:
                # 检查方法是否有实际实现（不是抽象方法）
                import inspect

                if inspect.isabstract(raw_client.__class__):
                    raise DependencyError(f"注入的raw_client是抽象类，无法使用")
            except Exception:
                # 如果检查失败，继续执行（兼容性考虑）
                pass

    def _validate_mapper(self, mapper: WeiboDataMapper) -> None:
        """验证注入的mapper依赖

        Args:
            mapper: 要验证的mapper实例

        Raises:
            DependencyError: 当mapper无效时
        """
        if not isinstance(mapper, WeiboDataMapper):
            raise DependencyError(
                f"注入的mapper必须是WeiboDataMapper实例，"
                f"实际类型: {type(mapper).__name__}"
            )

        # 验证必要的方法是否存在且可调用
        required_methods = [
            "map_user_profile",
            "map_user_timeline",
            "map_weibo_detail",
            "map_weibo_comments",
        ]

        for method_name in required_methods:
            if not hasattr(mapper, method_name):
                raise DependencyError(f"注入的mapper缺少必要的方法: {method_name}")

            method = getattr(mapper, method_name)
            if not callable(method):
                raise DependencyError(f"注入的mapper的{method_name}不是可调用对象")

            # 额外检查：确保方法不是抽象方法或未实现的方法
            try:
                # 检查方法是否有实际实现（不是抽象方法）
                import inspect

                if inspect.isabstract(mapper.__class__):
                    raise DependencyError(f"注入的mapper是抽象类，无法使用")
            except Exception:
                # 如果检查失败，继续执行（兼容性考虑）
                pass

    @property
    def raw_client(self) -> AsyncWeiboRawClient:
        """获取底层原始客户端

        用于需要直接访问底层API的高级用例。
        一般情况下不建议直接使用。

        Returns:
            AsyncWeiboRawClient: 底层原始客户端
        """
        return self._raw_client

    @property
    def mapper(self) -> WeiboDataMapper:
        """获取数据映射器

        用于需要直接访问数据映射功能的高级用例。
        一般情况下不建议直接使用。

        Returns:
            WeiboDataMapper: 数据映射器
        """
        return self._mapper

    def get_metrics_stats(self) -> dict:
        """获取性能指标统计信息

        Returns:
            dict: 包含所有性能指标的字典
        """
        return self._metrics_collector.get_stats()

    def reset_metrics_stats(self) -> None:
        """重置性能指标统计信息"""
        self._metrics_collector.reset_stats()

    def is_metrics_enabled(self) -> bool:
        """检查指标收集是否启用

        Returns:
            bool: 是否启用指标收集
        """
        return self._metrics_collector.is_enabled()

    async def __aenter__(self) -> "AsyncWeiboClient":
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """异步上下文管理器出口"""
        # 清理底层客户端资源
        if hasattr(self._raw_client, "__aexit__"):
            await self._raw_client.__aexit__(exc_type, exc_val, exc_tb)
