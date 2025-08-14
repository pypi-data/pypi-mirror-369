"""
微博 API 同步客户端模块

提供同步版本的微博 API 客户端，支持用户信息获取、微博时间线获取、
微博详情获取、微博评论获取等功能。
"""

import json
import logging
import re
from typing import Any, Dict, Optional

import httpx

from .config import WeiboConfig
from .exceptions import AuthenticationError, NetworkError, ParseError, RateLimitError
from .retry_manager import RetryManager
from .utils import RateLimiter, ensure_cookie_is_valid, setup_logger


class WeiboClient:
    """同步版本的微博 API 客户端

    提供完整的微博数据获取功能，包括用户信息、时间线、微博详情、评论等。
    支持自动 Cookie 管理、速率限制、重试机制等功能。
    """

    def __init__(
        self,
        cookies: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        config: Optional[WeiboConfig] = None,
    ):
        """
        初始化微博客户端

        Args:
            cookies: 可选的 Cookie 字符串
            logger: 可选的日志记录器
            config: 可选的配置对象
        """
        self.config = config or WeiboConfig()
        self.logger = logger or setup_logger(f"{__name__}.{self.__class__.__name__}")
        self.cookies = cookies
        self.rate_limiter = RateLimiter(
            self.config.rate_limit_calls, self.config.rate_limit_window
        )
        self.retry_manager = RetryManager(self.config, self.logger)

        # 基础请求头
        self.base_headers = {
            "User-Agent": self.config.user_agent,
            "Referer": "https://weibo.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }

        # 初始化 Cookie
        if not self.cookies:
            self._generate_anonymous_cookies()

    def _execute_with_retry_sync(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        """同步版本的重试执行方法"""
        import asyncio

        # 包装同步函数为异步函数
        async def async_wrapper() -> Any:
            return func(*args, **kwargs)

        # 使用重试管理器执行
        try:
            # 尝试获取当前事件循环
            loop = asyncio.get_running_loop()
            # 如果已经在事件循环中，创建新任务
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run, self.retry_manager.execute_with_retry(async_wrapper)
                )
                return future.result()
        except RuntimeError:
            # 没有运行中的事件循环，直接运行
            return asyncio.run(self.retry_manager.execute_with_retry(async_wrapper))

    def _check_rate_limit(self) -> None:
        """检查速率限制"""
        if not self.rate_limiter.can_make_request():
            wait_time = self.rate_limiter.time_until_next_request()
            raise RateLimitError(f"速率限制: 请等待 {wait_time:.1f} 秒后重试")

    def _check_cookie_validity(self) -> bool:
        """检查当前客户端存储的 Cookie 是否有效"""
        self.logger.info("⚙️ 正在执行 Cookie 有效性检查...")
        if self.cookies and "SUB" in self.cookies and "SUBP" in self.cookies:
            self.logger.info("✅ Cookie 存在且格式基本正确。")
            return True
        self.logger.warning("⚠️ Cookie 不存在或格式不正确。")
        return False

    def _generate_anonymous_cookies(self) -> None:
        """生成匿名访客 Cookie"""

        def _do_generate() -> None:
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

            self.logger.info("🚀 正在从微博服务器请求匿名 Cookie...")

            try:
                response = httpx.post(
                    url, headers=headers, data=data, timeout=self.config.timeout
                )
                response.raise_for_status()

                # 尝试从响应头获取 Cookie
                sub, subp = response.cookies.get("SUB"), response.cookies.get("SUBP")
                if sub and subp:
                    self.cookies = f"SUB={sub}; SUBP={subp}"
                    self.logger.info("✅ 成功从响应头获取匿名 Cookie！")
                    return

                self.logger.warning("⚠️ 未能在响应头中找到 Cookie，尝试解析响应体...")
                match = re.search(r"\((.*)\)", response.text)
                if match:
                    json_data = json.loads(match.group(1))
                    if json_data.get("retcode") == 20000000 and "data" in json_data:
                        sub, subp = json_data["data"].get("sub"), json_data["data"].get(
                            "subp"
                        )
                        if sub and subp:
                            self.cookies = f"SUB={sub}; SUBP={subp}"
                            self.logger.info("✅ 成功从响应体中解析出 Cookie！")
                            return

                self.logger.error(
                    "❌ 获取有效 Cookie 失败。响应体: %s...", response.text[:200]
                )
                raise ConnectionError("无法生成有效的匿名 Cookie。")

            except httpx.RequestError as e:
                raise NetworkError(f"网络请求失败: {e}")
            except json.JSONDecodeError as e:
                raise ParseError(f"JSON 解析失败: {e}")

        # 使用同步版本的重试执行
        self._execute_with_retry_sync(_do_generate)

    def _request(
        self,
        method: str,
        url: str,
        with_cookies: bool = True,
        with_headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> Optional[httpx.Response]:
        """底层的核心请求方法"""

        def _do_request() -> Optional[httpx.Response]:
            # 检查速率限制
            self._check_rate_limit()

            if with_headers is None:
                headers = self.base_headers.copy()
            else:
                headers = {**with_headers}
            if with_cookies and self.cookies:
                headers["Cookie"] = self.cookies

            try:
                response = httpx.request(
                    method, url, headers=headers, timeout=self.config.timeout, **kwargs
                )
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                self.logger.error(f"❌ HTTP 错误: {e.response.status_code} - {url}")
                self.logger.debug(f"   响应内容: {e.response.text}")
                if e.response.status_code == 401:
                    raise AuthenticationError("认证失败，请检查 Cookie")
                elif e.response.status_code == 429:
                    raise RateLimitError("请求过于频繁，请稍后重试")
                else:
                    raise NetworkError(
                        f"HTTP 错误 {e.response.status_code}: {e.response.text}"
                    )
            except httpx.RequestError as e:
                self.logger.error(f"❌ 请求失败: {e} - {url}")
                raise NetworkError(f"请求错误: {e}")

        # 使用同步版本的重试执行
        result = self._execute_with_retry_sync(_do_request)
        return result  # type: ignore

    def _get_json(
        self,
        url: str,
        with_cookies: bool = True,
        with_headers: Optional[Dict[str, str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """发送请求并期望返回 JSON 数据"""
        response = self._request(
            "GET", url, with_cookies=with_cookies, with_headers=with_headers
        )
        if not response:
            return None
        try:
            result = response.json()
            return result  # type: ignore
        except json.JSONDecodeError as e:
            self.logger.error(
                f"❌ JSON 解析失败 - {url} - 响应内容: {response.text[:200]}..."
            )
            raise ParseError(f"JSON 解析失败: {e}")

    def _get_text(
        self,
        url: str,
        with_cookies: bool = True,
        with_headers: Optional[Dict[str, str]] = None,
    ) -> Optional[str]:
        """发送请求并期望返回文本数据"""
        response = self._request(
            "GET", url, with_cookies=with_cookies, with_headers=with_headers
        )
        return response.text if response else None

    # --- 公共 API 方法 ---

    def get_weibo_detail(self, weibo_id: str) -> Dict[str, Any]:
        """通过微博 ID 获取单条微博的详细信息

        Args:
            weibo_id: 微博 ID

        Returns:
            微博详情数据字典
        """
        try:
            self.logger.info(f"正在获取微博 {weibo_id} 的详情页...")
            url = f"{self.config.mobile_url}/detail/{weibo_id}"

            html_content = self._get_text(url, with_cookies=False, with_headers={})
            if not html_content:
                return {"error": "获取微博详情页面失败"}

            json_pattern = r"\$render_data\s*=\s*\[(.*?)\]\[0\]\s*\|\|\s*\{\}"
            match = re.search(json_pattern, html_content, re.DOTALL)
            if match:
                try:
                    result = json.loads(match.group(1))
                    return result  # type: ignore
                except json.JSONDecodeError:
                    self.logger.error(f"❌ 解析微博详情页的 JSON 数据失败: {url}")
                    return {"error": "解析页面内嵌的JSON数据失败"}

            self.logger.warning(f"无法在页面中找到 $render_data: {url}")
            return {
                "error": "无法在响应中找到渲染数据",
                "content_preview": html_content[:500],
            }
        except Exception as e:
            self.logger.error(f"获取微博详情失败: {e}")
            return {"error": str(e)}

    @ensure_cookie_is_valid
    def get_user_timeline(
        self, user_id: str, page: int = 1
    ) -> Optional[Dict[str, Any]]:
        """通过用户 ID 获取其微博时间线

        Args:
            user_id: 用户 ID
            page: 页码，默认为 1

        Returns:
            用户时间线数据字典
        """
        try:
            self.logger.info(f"正在获取用户 {user_id} 的第 {page} 页微博...")
            url = f"{self.config.base_url}/ajax/statuses/mymblog?uid={user_id}&page={page}"
            return self._get_json(url)
        except Exception as e:
            self.logger.error(f"获取用户时间线失败: {e}")
            return {"error": str(e)}

    @ensure_cookie_is_valid
    def get_weibo_comments(self, weibo_id: str) -> Optional[Dict[str, Any]]:
        """获取指定微博的热门评论

        Args:
            weibo_id: 微博 ID

        Returns:
            微博评论数据字典
        """
        try:
            self.logger.info(f"正在获取微博 {weibo_id} 的评论...")
            url = f"{self.config.mobile_url}/comments/hotflow?mid={weibo_id}"
            return self._get_json(url)
        except Exception as e:
            self.logger.error(f"获取微博评论失败: {e}")
            return {"error": str(e)}

    @ensure_cookie_is_valid
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """通过用户 ID 获取其个人公开信息

        Args:
            user_id: 用户 ID

        Returns:
            用户信息数据字典
        """
        try:
            self.logger.info(f"正在获取用户 {user_id} 的个人信息...")
            url = f"{self.config.base_url}/ajax/profile/info?uid={user_id}"
            return self._get_json(url)
        except Exception as e:
            self.logger.error(f"获取用户信息失败: {e}")
            return {"error": str(e)}
