"""
微博 API 数据模型模块

提供所有微博相关的数据模型定义，使用 Pydantic 进行数据验证和序列化。
包括用户、微博、评论、图片、视频等核心数据模型。
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator


class WeiboUser(BaseModel):
    """微博用户模型"""

    id: int = Field(..., description="用户ID")
    screen_name: str = Field(..., description="用户昵称")
    profile_image_url: HttpUrl = Field(..., description="用户头像 (50x50)")
    avatar_hd: HttpUrl = Field(..., description="高清用户头像")
    followers_count: int = Field(0, description="粉丝数")
    friends_count: int = Field(0, description="关注数")
    location: Optional[str] = Field(None, description="用户归属地")
    description: Optional[str] = Field(None, description="用户个人简介")
    verified: bool = Field(False, description="是否认证")
    verified_reason: Optional[str] = Field(None, description="认证原因")

    @field_validator("followers_count", "friends_count", mode="before")
    @classmethod
    def standardize_counts(cls, v: Any) -> int:
        """处理粉丝/关注数可能为字符串（如 "2683.1万"）或整数的情况"""
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            v = v.strip()
            if "万" in v:
                num = float(v.replace("万", ""))
                return int(num * 10000)
            if "亿" in v:
                num = float(v.replace("亿", ""))
                return int(num * 100000000)
        try:
            return int(v)
        except (ValueError, TypeError):
            return 0


class ImageInfo(BaseModel):
    """单个尺寸的图片信息"""

    url: HttpUrl
    width: int
    height: int


class WeiboImage(BaseModel):
    """单张微博图片的所有尺寸信息集合"""

    pic_id: str = Field(..., description="图片ID")
    thumbnail: ImageInfo = Field(..., description="缩略图")
    bmiddle: ImageInfo = Field(..., description="中等尺寸图")
    large: ImageInfo = Field(..., description="大尺寸图")
    original: ImageInfo = Field(..., description="原始尺寸图")


class VideoPlaybackInfo(BaseModel):
    """视频不同清晰度的播放信息"""

    quality_label: str
    url: HttpUrl
    bitrate: Optional[int] = None


class WeiboVideo(BaseModel):
    """微博视频模型"""

    duration: float = Field(0.0, description="视频时长（秒）")
    play_count_text: Optional[str] = Field(None, alias="online_users")
    playback_list: List[VideoPlaybackInfo] = Field([])


class BaseContent(BaseModel):
    """微博与评论的基类"""

    id: int
    created_at: datetime
    text: str
    source: Optional[str] = None
    user: WeiboUser

    @field_validator("created_at", mode="before")
    @classmethod
    def format_datetime(cls, v: Any) -> datetime:
        """将微博特定的时间字符串转换为 datetime 对象"""
        if isinstance(v, datetime):
            return v

        # 尝试多种时间格式
        formats = [
            "%a %b %d %H:%M:%S %z %Y",  # 原始微博格式: Mon Jan 01 12:00:00 +0800 2024
            "%Y-%m-%d %H:%M:%S%z",  # ISO格式: 2025-06-29 06:46:38+08:00
        ]

        for fmt in formats:
            try:
                return datetime.strptime(v, fmt)
            except ValueError:
                continue

        # 如果都失败了，抛出错误
        raise ValueError(f"无法解析时间格式: {v}")

    @field_validator("source", mode="before")
    @classmethod
    def clean_source(cls, v: Optional[str]) -> Optional[str]:
        """清理来源信息中的HTML标签"""
        if v:
            match = re.search(">(.*?)</a>", v)
            if match:
                return match.group(1)
        return v


class WeiboPost(BaseContent):
    """单条微博模型 (已增强对图片的支持)"""

    text_raw: Optional[str] = None
    region_name: Optional[str] = None
    reposts_count: int = 0
    comments_count: int = 0
    attitudes_count: int = 0

    # 图片相关字段
    pic_num: int = 0
    pic_ids: List[str] = Field([], description="有序的图片ID列表 (内部使用)")
    pic_infos: Optional[Dict[str, WeiboImage]] = Field(
        None, description="图片信息字典 (内部使用)"
    )

    # 视频相关字段
    page_info: Optional[WeiboVideo] = None

    # ✨ 关键优化：提供一个有序的、可直接使用的图片列表 ✨
    images: List[WeiboImage] = Field([], description="有序的图片对象列表 (推荐使用)")

    @field_validator("pic_infos", mode="before")
    @classmethod
    def _add_pic_id_to_infos(cls, v: Any) -> Any:
        """在解析前，将作为key的pic_id注入到value字典中，以便WeiboImage模型能获取它"""
        if isinstance(v, dict):
            for pic_id, info_dict in v.items():
                if isinstance(info_dict, dict) and "pic_id" not in info_dict:
                    info_dict["pic_id"] = pic_id
        return v

    @model_validator(mode="after")
    def _assemble_ordered_images(self) -> "WeiboPost":
        """在模型创建后，根据有序的 pic_ids 和已处理的 pic_infos 组装 images 列表"""
        if self.pic_ids and self.pic_infos:
            self.images = [
                self.pic_infos[pid] for pid in self.pic_ids if pid in self.pic_infos
            ]
        return self


class WeiboComment(BaseContent):
    """单条评论模型"""

    id: int
    rootid: int
    floor_number: int
    like_count: int = 0


# ---------------------------------------------------------------------------
# 响应模型 - 用于 API 响应的封装
# ---------------------------------------------------------------------------


class UserTimelineData(BaseModel):
    """用户时间线数据"""

    list: List[WeiboPost] = Field([])


class UserTimelineResponse(BaseModel):
    """用户时间线响应"""

    ok: int
    data: UserTimelineData


class PostDetailResponse(BaseModel):
    """微博详情响应"""

    ok: int
    status: WeiboPost


class UserDetailData(BaseModel):
    """用户详情数据"""

    user: WeiboUser


class UserDetailResponse(BaseModel):
    """用户详情响应"""

    ok: int
    data: UserDetailData


class PostCommentsData(BaseModel):
    """微博评论数据"""

    comments: List[WeiboComment] = Field(..., alias="data")
    total_number: int


class PostCommentsResponse(BaseModel):
    """微博评论响应"""

    ok: int
    data: PostCommentsData


class ApiResponse(BaseModel):
    """统一的 API 响应包装"""

    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    status_code: Optional[int] = None

    @classmethod
    def success_response(cls, data: Any) -> "ApiResponse":
        """创建成功响应"""
        return cls(success=True, data=data)

    @classmethod
    def error_response(
        cls, error: str, status_code: Optional[int] = None
    ) -> "ApiResponse":
        """创建错误响应"""
        return cls(success=False, error=error, status_code=status_code)


# ---------------------------------------------------------------------------
# DTO 模型 - 防腐层输入，表示外部API的原始响应数据结构
# ---------------------------------------------------------------------------


class UserProfileRawDTO(BaseModel):
    """用户信息原始API响应DTO"""

    ok: int = Field(..., description="API响应状态码")
    data: Dict[str, Any] = Field(..., description="原始用户数据")

    @field_validator("ok")
    @classmethod
    def validate_ok_status(cls, v: int) -> int:
        """验证API响应状态"""
        if v != 1:
            raise ValueError(f"API响应状态异常: {v}")
        return v


class UserTimelineRawDTO(BaseModel):
    """用户时间线原始API响应DTO"""

    ok: int = Field(..., description="API响应状态码")
    data: Dict[str, Any] = Field(..., description="原始时间线数据")

    @field_validator("ok")
    @classmethod
    def validate_ok_status(cls, v: int) -> int:
        """验证API响应状态"""
        if v != 1:
            raise ValueError(f"API响应状态异常: {v}")
        return v


class WeiboDetailRawDTO(BaseModel):
    """微博详情原始API响应DTO"""

    status: Dict[str, Any] = Field(..., description="原始微博详情数据")

    @field_validator("status")
    @classmethod
    def validate_status_data(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """验证微博详情数据"""
        if not v or not isinstance(v, dict):
            raise ValueError("微博详情数据格式错误")
        return v


class WeiboCommentsRawDTO(BaseModel):
    """微博评论原始API响应DTO"""

    ok: int = Field(..., description="API响应状态码")
    data: Dict[str, Any] = Field(..., description="原始评论数据")

    @field_validator("ok")
    @classmethod
    def validate_ok_status(cls, v: int) -> int:
        """验证API响应状态"""
        if v != 1:
            raise ValueError(f"API响应状态异常: {v}")
        return v

    @field_validator("data")
    @classmethod
    def validate_comments_data(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """验证评论数据结构"""
        if not isinstance(v, dict):
            raise ValueError("评论数据格式错误")
        return v
