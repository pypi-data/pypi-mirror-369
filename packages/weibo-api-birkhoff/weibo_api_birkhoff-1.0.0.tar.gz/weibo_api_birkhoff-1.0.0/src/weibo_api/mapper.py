"""
微博 API 数据映射器模块

实现防腐层模式，负责将外部API的原始DTO数据转换为内部业务模型。
提供数据清洗、验证和标准化功能，隔离外部API变化对业务逻辑的影响。
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import ValidationError

from .exceptions import ParseError
from .models import (  # 业务模型; DTO模型
    ImageInfo,
    UserProfileRawDTO,
    UserTimelineRawDTO,
    VideoPlaybackInfo,
    WeiboComment,
    WeiboCommentsRawDTO,
    WeiboDetailRawDTO,
    WeiboImage,
    WeiboPost,
    WeiboUser,
    WeiboVideo,
)
from .utils import setup_logger


class WeiboDataMapper:
    """微博数据映射器

    实现防腐层模式，负责将外部API的DTO数据转换为业务模型。
    提供统一的数据转换、验证和错误处理机制。
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or setup_logger(f"{__name__}.{self.__class__.__name__}")

    def map_user_profile(self, raw_dto: UserProfileRawDTO) -> WeiboUser:
        """将用户信息DTO转换为业务模型

        Args:
            raw_dto: 用户信息原始DTO

        Returns:
            WeiboUser: 用户业务模型

        Raises:
            ParseError: 当数据转换失败时
        """
        try:
            user_data = raw_dto.data.get("user", {})
            if not user_data:
                raise ParseError("用户数据为空")

            # 数据清洗和标准化
            cleaned_data = self._clean_user_data(user_data)

            # 转换为业务模型
            return WeiboUser(**cleaned_data)

        except ValidationError as e:
            self.logger.error(f"用户数据验证失败: {e}")
            raise ParseError(f"用户数据格式错误: {e}")
        except Exception as e:
            self.logger.error(f"用户数据映射失败: {e}")
            raise ParseError(f"用户数据转换失败: {e}")

    def map_user_timeline(self, raw_dto: UserTimelineRawDTO) -> List[WeiboPost]:
        """将用户时间线DTO转换为业务模型列表

        Args:
            raw_dto: 用户时间线原始DTO

        Returns:
            List[WeiboPost]: 微博列表

        Raises:
            ParseError: 当数据转换失败时
        """
        try:
            timeline_data = raw_dto.data.get("list", [])
            if not isinstance(timeline_data, list):
                raise ParseError("时间线数据格式错误")

            posts = []
            for post_data in timeline_data:
                try:
                    cleaned_data = self._clean_post_data(post_data)
                    post = WeiboPost(**cleaned_data)
                    posts.append(post)
                except Exception as e:
                    self.logger.warning(f"跳过无效微博数据: {e}")
                    continue

            return posts

        except Exception as e:
            self.logger.error(f"时间线数据映射失败: {e}")
            raise ParseError(f"时间线数据转换失败: {e}")

    def map_weibo_detail(self, raw_dto: WeiboDetailRawDTO) -> WeiboPost:
        """将微博详情DTO转换为业务模型

        Args:
            raw_dto: 微博详情原始DTO

        Returns:
            WeiboPost: 微博业务模型

        Raises:
            ParseError: 当数据转换失败时
        """
        try:
            post_data = raw_dto.status
            if not post_data:
                raise ParseError("微博详情数据为空")

            # 数据清洗和标准化
            cleaned_data = self._clean_post_data(post_data)

            # 转换为业务模型
            return WeiboPost(**cleaned_data)

        except ValidationError as e:
            self.logger.error(f"微博详情数据验证失败: {e}")
            raise ParseError(f"微博详情数据格式错误: {e}")
        except Exception as e:
            self.logger.error(f"微博详情数据映射失败: {e}")
            raise ParseError(f"微博详情数据转换失败: {e}")

    def map_weibo_comments(self, raw_dto: WeiboCommentsRawDTO) -> List[WeiboComment]:
        """将微博评论DTO转换为业务模型列表

        Args:
            raw_dto: 微博评论原始DTO

        Returns:
            List[WeiboComment]: 评论列表

        Raises:
            ParseError: 当数据转换失败时
        """
        try:
            comments_data = raw_dto.data.get("data", [])
            if not isinstance(comments_data, list):
                raise ParseError("评论数据格式错误")

            comments = []
            for comment_data in comments_data:
                try:
                    cleaned_data = self._clean_comment_data(comment_data)
                    comment = WeiboComment(**cleaned_data)
                    comments.append(comment)
                except Exception as e:
                    self.logger.warning(f"跳过无效评论数据: {e}")
                    continue

            return comments

        except Exception as e:
            self.logger.error(f"评论数据映射失败: {e}")
            raise ParseError(f"评论数据转换失败: {e}")

    def _clean_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """清洗用户数据"""
        return {
            "id": int(user_data.get("id", 0)),
            "screen_name": str(user_data.get("screen_name", "")),
            "profile_image_url": user_data.get("profile_image_url", ""),
            "avatar_hd": user_data.get(
                "avatar_hd", user_data.get("profile_image_url", "")
            ),
            "followers_count": user_data.get("followers_count", 0),
            "friends_count": user_data.get("friends_count", 0),
            "location": user_data.get("location"),
            "description": user_data.get("description"),
            "verified": bool(user_data.get("verified", False)),
            "verified_reason": user_data.get("verified_reason"),
        }

    def _clean_post_data(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """清洗微博数据"""
        # 处理用户信息
        user_data = post_data.get("user", {})
        cleaned_user = self._clean_user_data(user_data) if user_data else {}

        return {
            "id": int(post_data.get("id", 0)),
            "created_at": post_data.get("created_at", ""),
            "text": str(post_data.get("text", "")),
            "text_raw": post_data.get("text_raw"),
            "source": post_data.get("source"),
            "region_name": post_data.get("region_name"),
            "reposts_count": int(post_data.get("reposts_count", 0)),
            "comments_count": int(post_data.get("comments_count", 0)),
            "attitudes_count": int(post_data.get("attitudes_count", 0)),
            "pic_num": int(post_data.get("pic_num", 0)),
            "pic_ids": post_data.get("pic_ids", []),
            "pic_infos": post_data.get("pic_infos"),
            "page_info": post_data.get("page_info"),
            "user": cleaned_user,
        }

    def _clean_comment_data(self, comment_data: Dict[str, Any]) -> Dict[str, Any]:
        """清洗评论数据"""
        # 处理用户信息
        user_data = comment_data.get("user", {})
        cleaned_user = self._clean_user_data(user_data) if user_data else {}

        return {
            "id": int(comment_data.get("id", 0)),
            "rootid": int(comment_data.get("rootid", 0)),
            "floor_number": int(comment_data.get("floor_number", 0)),
            "created_at": comment_data.get("created_at", ""),
            "text": str(comment_data.get("text", "")),
            "source": comment_data.get("source"),
            "like_count": int(comment_data.get("like_count", 0)),
            "user": cleaned_user,
        }

    def _safe_parse_datetime(self, date_str: str) -> str:
        """安全解析日期时间字符串"""
        if not date_str:
            return datetime.now().strftime("%a %b %d %H:%M:%S %z %Y")

        # 如果已经是标准格式，直接返回
        if isinstance(date_str, str) and len(date_str) > 20:
            return date_str

        # 处理相对时间格式（如"2分钟前"、"今天 12:30"等）
        try:
            # 这里可以添加更复杂的时间解析逻辑
            return date_str
        except Exception:
            # 如果解析失败，返回当前时间
            return datetime.now().strftime("%a %b %d %H:%M:%S %z %Y")

    def _extract_image_info(self, pic_info: Dict[str, Any]) -> Optional[ImageInfo]:
        """提取图片信息"""
        try:
            if not pic_info or not isinstance(pic_info, dict):
                return None

            return ImageInfo(
                url=pic_info.get("url", ""),
                width=int(pic_info.get("width", 0)),
                height=int(pic_info.get("height", 0)),
            )
        except Exception as e:
            self.logger.warning(f"图片信息提取失败: {e}")
            return None

    def _extract_video_info(self, page_info: Dict[str, Any]) -> Optional[WeiboVideo]:
        """提取视频信息"""
        try:
            if not page_info or not isinstance(page_info, dict):
                return None

            # 提取播放列表
            playback_list = []
            media_info = page_info.get("media_info", {})
            if media_info:
                for quality, info in media_info.items():
                    if isinstance(info, dict) and "url" in info:
                        playback_info = VideoPlaybackInfo(
                            quality_label=quality,
                            url=info["url"],
                            bitrate=info.get("bitrate"),
                        )
                        playback_list.append(playback_info)

            return WeiboVideo(
                duration=float(page_info.get("duration", 0)),
                online_users=page_info.get("online_users"),
                playback_list=playback_list,
            )
        except Exception as e:
            self.logger.warning(f"视频信息提取失败: {e}")
            return None
