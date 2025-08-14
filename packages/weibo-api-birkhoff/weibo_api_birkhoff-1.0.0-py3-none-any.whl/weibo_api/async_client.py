"""
微博 API 异步客户端模块

提供异步版本的微博 API 客户端，支持高并发的微博数据获取。
包括用户信息获取、微博时间线获取、微博详情获取、微博评论获取等功能。
"""

import asyncio
import json
import logging
import re
import time
import traceback
from functools import wraps
from typing import Any, Callable, Dict, Optional, Union

import httpx
from pydantic import ValidationError

from .config import WeiboConfig
from .connection_manager import ConnectionManager
from .exceptions import (
    AuthenticationError,
    CircuitBreakerOpenError,
    CookieGenerationError,
    NetworkError,
    ParseError,
    RateLimitError,
    ResourceError,
)
from .retry_manager import RetryManager
from .utils import (
    BoundaryChecker,
    CircuitBreaker,
    CookieState,
    ErrorHandler,
    RateLimiter,
    RetryContext,
    setup_logger,
    simple_retry,
)


class AsyncCookieManager:
    """异步Cookie管理器

    负责Cookie的生成、验证和管理，实现职责分离。
    """

    def __init__(self, config: WeiboConfig, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.cookies: Optional[str] = None
        self._cookie_lock = asyncio.Lock()
        self._last_validation: Optional[float] = None
        self._validation_interval: float = config.cookie_validation_interval

        # 状态管理
        self._state = CookieState.INVALID
        self._generation_failures = 0
        self._max_generation_failures = config.max_cookie_generation_failures
        self._cooldown_duration = config.cookie_cooldown_duration
        self._last_generation_attempt: Optional[float] = None
        self._heavy_validation_url = config.heavy_validation_url
        self._generation_event: Optional[asyncio.Event] = None

        # 使用RetryManager进行重试管理
        self._retry_manager = RetryManager(config, logger)

    def _is_in_cooldown(self) -> bool:
        """检查是否在冷却期"""
        if self._last_generation_attempt is None:
            return False
        return time.time() - self._last_generation_attempt < self._cooldown_duration

    async def _wait_for_generation_complete(self, timeout: float = 30.0) -> None:
        """等待Cookie生成完成"""
        if self._generation_event:
            try:
                await asyncio.wait_for(self._generation_event.wait(), timeout=timeout)
            except asyncio.TimeoutError:
                self.logger.warning("等待Cookie生成超时")
                self._state = CookieState.FAILED

    async def is_valid(self) -> bool:
        """异步检查Cookie是否有效，带缓存机制（轻量级检查）"""
        # 检查缓存是否有效
        now = time.time()
        if (
            self._last_validation
            and now - self._last_validation < self._validation_interval
            and self.cookies
            and self._state == CookieState.VALID
        ):
            return True

        # 执行实际验证
        if not self.cookies:
            self._last_validation = None
            self._state = CookieState.INVALID
            return False

        # 基本格式检查
        if "SUB" not in self.cookies or "SUBP" not in self.cookies:
            self._last_validation = None
            self._state = CookieState.INVALID
            return False

        self.logger.info("✅ Cookie 格式验证通过")
        self._last_validation = now
        self._state = CookieState.VALID
        return True

    async def _heavy_validation(self) -> bool:
        """重量级Cookie验证 - 实际发送API请求"""
        if not self.cookies:
            return False

        try:
            headers = {
                "Cookie": self.cookies,
                "User-Agent": self.config.user_agent,
                "Referer": "https://weibo.com/",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self._heavy_validation_url, headers=headers, timeout=5.0
                )

                # 检查响应状态和内容
                if response.status_code == 200:
                    try:
                        data = response.json()
                        # 如果返回正常数据结构，说明Cookie有效
                        is_valid = "data" in data and data.get("ok") == 1
                        if is_valid:
                            self._state = CookieState.VALID
                            self._last_validation = time.time()
                        else:
                            self._state = CookieState.INVALID
                        return is_valid
                    except json.JSONDecodeError:
                        self._state = CookieState.INVALID
                        return False
                elif response.status_code == 401:
                    self._state = CookieState.INVALID
                    return False
                else:
                    # 其他错误不确定Cookie状态，保守返回False
                    self._state = CookieState.INVALID
                    return False

        except Exception as e:
            self.logger.warning(f"重量级Cookie验证失败: {e}")
            self._state = CookieState.INVALID
            return False

    async def _generate_with_state_management(self) -> None:
        """带状态管理的Cookie生成"""
        async with self._cookie_lock:
            # 检查是否已经在生成中
            if self._state == CookieState.GENERATING:
                return

            self._state = CookieState.GENERATING
            self._generation_event = asyncio.Event()
            self._last_generation_attempt = time.time()

            try:
                # 使用RetryManager执行Cookie生成
                await self._retry_manager.execute_with_retry(
                    self._do_generate_cookies, max_attempts=3
                )
                self._generation_failures = 0
                self._state = CookieState.VALID
                self.logger.info("✅ Cookie生成成功")
            except Exception as e:
                self._generation_failures += 1
                self.logger.error(
                    f"❌ Cookie生成失败 (第{self._generation_failures}次): {e}"
                )

                if self._generation_failures >= self._max_generation_failures:
                    self._state = CookieState.COOLDOWN
                    self.logger.warning(
                        f"Cookie生成失败次数过多，进入冷却期 {self._cooldown_duration} 秒"
                    )
                else:
                    self._state = CookieState.FAILED
                raise CookieGenerationError(f"Cookie生成失败: {e}")
            finally:
                if self._generation_event:
                    self._generation_event.set()
                    self._generation_event = None

    async def _do_generate_cookies(self) -> None:
        """实际执行Cookie生成的方法"""
        url = self.config.visitor_url
        data = {
            "cb": "visitor_gray_callback",
            "tid": "",
            "from": "weibo",
            "webdriver": "false",
        }
        headers = {
            "User-Agent": self.config.user_agent,
            "Referer": "https://passport.weibo.com/visitor/visitor",
        }

        self.logger.info("🚀 正在异步获取匿名访客 Cookie...")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url, headers=headers, data=data, timeout=self.config.timeout
                )
                response.raise_for_status()

                # 尝试从响应头获取 Cookie
                sub, subp = response.cookies.get("SUB"), response.cookies.get("SUBP")
                if sub and subp:
                    self.cookies = f"SUB={sub}; SUBP={subp}"
                    self.logger.info("✅ 成功获取匿名 Cookie")
                    return

                # 尝试从响应体解析
                match = re.search(r"\((.*)\)", response.text)
                if match:
                    json_data = json.loads(match.group(1))
                    if json_data.get("retcode") == 20000000 and "data" in json_data:
                        data = json_data["data"]
                        if data.get("sub") and data.get("subp"):
                            self.cookies = f"SUB={data['sub']}; SUBP={data['subp']}"
                            self.logger.info("✅ 成功从响应体解析 Cookie")
                            return

                raise ParseError("无法解析有效的 Cookie 信息")

            except httpx.RequestError as e:
                raise NetworkError(f"网络请求失败: {e}")
            except json.JSONDecodeError as e:
                raise ParseError(f"JSON 解析失败: {e}")

    async def ensure_valid(self, force_heavy_check: bool = False) -> None:
        """确保有可用的有效Cookie，带状态管理和冷却机制"""

        # 检查是否在冷却期
        if self._state == CookieState.COOLDOWN:
            if self._is_in_cooldown():
                raise CookieGenerationError("Cookie生成失败过多，处于冷却期")
            else:
                self._state = CookieState.INVALID

        # 检查是否正在生成中
        if self._state == CookieState.GENERATING:
            # 等待生成完成或超时
            await self._wait_for_generation_complete()
            return

        # 轻量级检查
        if not force_heavy_check and await self.is_valid():
            return

        # 重量级检查（在重试时使用）
        if force_heavy_check and await self._heavy_validation():
            return

        # 需要生成新Cookie
        await self._generate_with_state_management()

    def get_cookies(self) -> Optional[str]:
        """获取当前Cookie"""
        return self.cookies

    def set_cookies(self, cookies: str) -> None:
        """设置Cookie"""
        self.cookies = cookies

    async def generate_anonymous_cookies(self) -> None:
        """生成匿名访客Cookie

        为了兼容测试，直接调用内部的_generate_with_state_management方法
        """
        await self._generate_with_state_management()


class ApiCallHandler:
    """API调用处理器，负责统一处理API调用的各个环节"""

    def __init__(self, client_instance: Any) -> None:
        self.client = client_instance
        self.logger = client_instance.logger
        self.config = client_instance.config

    async def validate_input_parameters(
        self, func: Callable, args: tuple, kwargs: dict
    ) -> None:
        """验证输入参数"""
        if not (
            hasattr(self.config, "enable_boundary_checks")
            and self.config.enable_boundary_checks
        ):
            return

        user_id = None
        weibo_id = None

        if "user" in func.__name__:
            # 用户相关API，第一个参数是user_id
            user_id = kwargs.get("user_id") or (args[0] if args else None)
        elif "weibo" in func.__name__:
            # 微博相关API，第一个参数是weibo_id
            weibo_id = kwargs.get("weibo_id") or (args[0] if args else None)

        try:
            BoundaryChecker.validate_input_parameters(
                user_id=user_id, weibo_id=weibo_id
            )
        except ValueError as e:
            raise ParseError(str(e))

    async def ensure_cookie_valid(
        self, ctx: RetryContext, requires_cookies: bool
    ) -> None:
        """确保Cookie有效"""
        if requires_cookies:
            await self.client.cookie_manager.ensure_valid(
                force_heavy_check=False  # 移除重试相关的逻辑
            )

    async def handle_api_call_with_retry(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict,
        ctx: RetryContext,
        wrapper_func: Callable,
    ) -> Any:
        """处理API调用（不再包含重试逻辑，重试由RetryManager统一处理）"""
        try:
            return await func(self.client, *args, **kwargs)
        except Exception as e:
            # 添加详细的错误上下文信息和traceback
            tb_str = traceback.format_exc()
            error_context = {
                "function": func.__name__,
                "args_count": len(args),
                "kwargs_keys": list(kwargs.keys()),
                "traceback": tb_str,
            }
            self.logger.error(
                f"API调用失败 [{func.__name__}]: {e}\n"
                f"错误上下文: {error_context}\n"
                f"完整traceback:\n{tb_str}"
            )
            # 重新抛出原始异常，让RetryManager处理重试逻辑
            raise


def async_api_handler(
    requires_cookies: bool = True, handle_errors: bool = True, enable_retry: bool = True
) -> Callable:
    """异步API调用装饰器，统一处理错误和Cookie验证

    Args:
        requires_cookies: 是否需要Cookie验证
        handle_errors: 是否统一处理错误（转换为NetworkError）
        enable_retry: 是否启用重试机制（现在由RetryManager统一处理）
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            # 定义实际的API调用函数
            async def api_call() -> Any:
                handler = ApiCallHandler(self)

                # 输入参数验证
                await handler.validate_input_parameters(func, args, kwargs)

                # Cookie验证
                await handler.ensure_cookie_valid(RetryContext(), requires_cookies)

                if handle_errors:
                    return await handler.handle_api_call_with_retry(
                        func, args, kwargs, RetryContext(), wrapper
                    )
                else:
                    return await func(self, *args, **kwargs)

            # 如果启用重试，使用RetryManager执行
            if enable_retry:
                # 记录API调用开始（用于重试统计）
                self.logger.debug(f"开始执行API调用: {func.__name__}")
                try:
                    result = await self.retry_manager.execute_with_retry(api_call)
                    self.logger.debug(f"API调用成功完成: {func.__name__}")
                    return result
                except Exception as e:
                    self.logger.error(f"API调用最终失败: {func.__name__} - {e}")
                    raise
            else:
                return await api_call()

        return wrapper

    return decorator


class AsyncWeiboRawClient:
    """异步版本的微博原始客户端

    提供底层的异步微博API调用功能，返回原始JSON数据。
    支持并发请求和自动速率控制，适用于需要直接访问原始API数据的场景。

    注意：这是底层客户端，建议使用AsyncWeiboClient（Facade层）获得更好的开发体验。
    """

    def __init__(
        self,
        cookies: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        config: Optional[WeiboConfig] = None,
    ) -> None:
        """
        初始化异步微博客户端

        Args:
            cookies: 可选的 Cookie 字符串
            logger: 可选的日志记录器
            config: 可选的配置对象
        """
        self.config: WeiboConfig = config or WeiboConfig()
        self.logger: logging.Logger = logger or setup_logger(
            f"{__name__}.{self.__class__.__name__}"
        )

        # 使用独立的Cookie管理器
        self.cookie_manager: AsyncCookieManager = AsyncCookieManager(
            self.config, self.logger
        )
        if cookies:
            self.cookie_manager.set_cookies(cookies)

        self.rate_limiter: RateLimiter = RateLimiter(
            self.config.rate_limit_calls, self.config.rate_limit_window
        )

        # 新增组件
        self.circuit_breaker: CircuitBreaker = CircuitBreaker(
            failure_threshold=self.config.circuit_breaker_threshold,
            recovery_timeout=self.config.circuit_breaker_timeout,
            half_open_max_calls=getattr(
                self.config, "circuit_breaker_half_open_max_calls", 3
            ),
        )
        self.error_handler: ErrorHandler = ErrorHandler(self.circuit_breaker)
        self.connection_manager: ConnectionManager = ConnectionManager(
            self.config, self.logger
        )
        self.retry_manager: RetryManager = RetryManager(self.config, self.logger)

        self.base_headers: Dict[str, str] = {
            "User-Agent": self.config.user_agent,
            "Referer": "https://weibo.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }

    async def _pre_request_checks(self) -> None:
        """请求前的边界检查"""
        if self.config.enable_boundary_checks:
            if not BoundaryChecker.validate_network_connectivity():
                raise NetworkError("网络连接不可用")

            if not BoundaryChecker.validate_memory_usage(
                self.config.max_memory_usage_percent
            ):
                raise ResourceError("系统内存不足")

        if self.circuit_breaker.is_open():
            raise CircuitBreakerOpenError("服务熔断中，请稍后重试")

    async def _check_rate_limit(self) -> None:
        """检查速率限制"""
        if not self.rate_limiter.can_make_request():
            wait_time = self.rate_limiter.time_until_next_request()
            await asyncio.sleep(wait_time)

    async def _request(
        self,
        method: str,
        url: str,
        with_cookies: bool = True,
        custom_headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """异步请求方法，使用连接池和熔断器"""
        await self._pre_request_checks()
        await self._check_rate_limit()

        # 构建请求头
        headers: Dict[str, str] = self.base_headers.copy()
        if isinstance(custom_headers, dict) and len(custom_headers) == 0:
            headers = {}
        elif custom_headers:
            headers.update(custom_headers)
        if with_cookies:
            cookies = self.cookie_manager.get_cookies()
            if cookies:
                headers["Cookie"] = cookies

        client = await self.connection_manager.get_client()

        # 通过熔断器执行请求
        async def do_request() -> httpx.Response:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    timeout=self.config.timeout,
                    **kwargs,
                )
                response.raise_for_status()

                # 记录成功请求
                self.connection_manager.record_request_success()
                return response

            except httpx.HTTPStatusError as e:
                # 记录失败请求
                self.connection_manager.record_request_failure()

                self.logger.error(f"❌ HTTP 错误: {e.response.status_code} - {url}")
                if e.response.status_code == 401:
                    raise AuthenticationError("认证失败")
                elif e.response.status_code == 429:
                    raise RateLimitError("请求过于频繁")
                else:
                    raise NetworkError(f"HTTP 错误 {e.response.status_code}")
            except httpx.RequestError as e:
                # 记录失败请求
                self.connection_manager.record_request_failure()

                self.logger.error(f"❌ 请求失败: {e} - {url}")
                raise NetworkError(f"请求错误: {e}")

        result = await self.circuit_breaker.call(do_request)
        return result  # type: ignore

    async def __aenter__(self) -> "AsyncWeiboRawClient":
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """异步上下文管理器出口"""
        try:
            await self.connection_manager.close()
        except Exception as e:
            self.logger.error(f"关闭连接管理器时出错: {e}")

    async def _get_json(
        self,
        url: str,
        with_cookies: bool = True,
        custom_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """异步获取 JSON 响应"""
        response = await self._request(
            "GET", url, with_cookies=with_cookies, custom_headers=custom_headers
        )
        try:
            result = response.json()
            return result  # type: ignore
        except json.JSONDecodeError as e:
            self.logger.error(
                f"❌ JSON 解析失败 - {url} - 响应内容: {response.text[:200]}..."
            )
            raise ParseError(f"JSON 解析失败: {e}")

    async def _get_text(
        self,
        url: str,
        with_cookies: bool = True,
        custom_headers: Optional[Dict[str, str]] = None,
    ) -> str:
        """异步获取文本响应"""
        response = await self._request(
            "GET", url, with_cookies=with_cookies, custom_headers=custom_headers
        )
        return response.text

    # --- 异步公共 API 方法 ---

    @async_api_handler(requires_cookies=False, handle_errors=True)
    async def get_weibo_detail(self, weibo_id: str) -> Dict[str, Any]:
        """异步获取微博详情

        Args:
            weibo_id: 微博 ID

        Returns:
            微博详情数据字典

        Raises:
            ParseError: 当无法解析响应数据时
            NetworkError: 当网络请求失败时
        """
        self.logger.info(f"正在异步获取微博 {weibo_id} 的详情页...")
        url = f"{self.config.mobile_url}/detail/{weibo_id}"

        html_content = await self._get_text(url, with_cookies=False, custom_headers={})

        json_pattern = r"\$render_data\s*=\s*\[(.*?)\]\[0\]\s*\|\|\s*\{\}"
        match = re.search(json_pattern, html_content, re.DOTALL)

        if not match:
            raise ParseError("无法在响应中找到渲染数据")

        try:
            data = json.loads(match.group(1))
            return data  # type: ignore
        except json.JSONDecodeError as e:
            raise ParseError(f"JSON 解析失败: {e}")

    @async_api_handler(requires_cookies=True, handle_errors=True)
    async def get_user_timeline(self, user_id: str, page: int = 1) -> Dict[str, Any]:
        """异步获取用户时间线

        Args:
            user_id: 用户 ID
            page: 页码，默认为 1

        Returns:
            用户时间线数据字典

        Raises:
            AuthenticationError: 当认证失败时
            NetworkError: 当网络请求失败时
            ParseError: 当响应解析失败时
        """
        self.logger.info(f"正在异步获取用户 {user_id} 的第 {page} 页微博...")
        url = f"{self.config.base_url}/ajax/statuses/mymblog?uid={user_id}&page={page}"
        return await self._get_json(url)

    @async_api_handler(requires_cookies=True, handle_errors=True)
    async def get_weibo_comments(self, weibo_id: str) -> Dict[str, Any]:
        """异步获取微博评论

        Args:
            weibo_id: 微博 ID

        Returns:
            微博评论数据字典

        Raises:
            AuthenticationError: 当认证失败时
            NetworkError: 当网络请求失败时
            ParseError: 当响应解析失败时
        """
        self.logger.info(f"正在异步获取微博 {weibo_id} 的评论...")
        url = f"{self.config.mobile_url}/comments/hotflow?mid={weibo_id}"
        return await self._get_json(url)

    @async_api_handler(requires_cookies=True, handle_errors=True)
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """异步获取用户信息

        Args:
            user_id: 用户 ID

        Returns:
            用户信息数据字典

        Raises:
            AuthenticationError: 当认证失败时
            NetworkError: 当网络请求失败时
            ParseError: 当响应解析失败时
        """
        self.logger.info(f"正在异步获取用户 {user_id} 的个人信息...")
        url = f"{self.config.base_url}/ajax/profile/info?uid={user_id}"
        return await self._get_json(url)

    # --- 连接池管理方法 ---

    def get_connection_stats(self) -> Dict[str, Any]:
        """获取连接池统计信息

        Returns:
            连接池统计信息字典
        """
        return self.connection_manager.get_stats()

    async def get_connection_health(self) -> Dict[str, Any]:
        """获取连接池健康状态

        Returns:
            连接池健康状态字典
        """
        return await self.connection_manager.health_check()

    def get_connection_info(self) -> Dict[str, Any]:
        """获取连接信息摘要

        Returns:
            连接信息摘要字典
        """
        return self.connection_manager.get_connection_info()

    # --- 重试管理方法 ---

    def get_retry_stats(self) -> Dict[str, Any]:
        """获取重试统计信息

        Returns:
            重试统计信息字典，包含：
            - total_attempts: 总尝试次数
            - successful_retries: 成功重试次数
            - failed_retries: 失败重试次数
            - no_retry_decisions: 不重试决策次数
            - retry_success_rate: 重试成功率
            - strategy_type: 重试策略类型
        """
        return self.retry_manager.get_retry_stats()

    def reset_retry_stats(self) -> None:
        """重置重试统计信息

        清空所有重试统计数据，用于重新开始统计或定期重置。
        """
        self.retry_manager.reset_stats()
        self.logger.info("重试统计信息已重置")

    def get_retry_info(self) -> Dict[str, Any]:
        """获取重试管理器信息摘要

        Returns:
            重试管理器信息摘要字典
        """
        stats = self.get_retry_stats()
        return {
            "retry_enabled": True,
            "max_retries": self.config.max_retries,
            "retry_delay": self.config.retry_delay,
            "strategy_type": stats.get("strategy_type", "Unknown"),
            "current_stats": stats,
        }
