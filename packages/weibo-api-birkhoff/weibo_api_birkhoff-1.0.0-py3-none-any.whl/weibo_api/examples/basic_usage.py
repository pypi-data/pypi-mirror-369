"""
基本使用示例

演示微博 API 客户端的基本使用方法。
"""

import logging
import os
import sys

# 添加父目录到路径，以便导入 weibo_api 模块
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from weibo_api import WeiboClient, WeiboConfig
from weibo_api.models import UserDetailResponse, UserTimelineResponse

# 设置日志
logging.basicConfig(level=logging.INFO)


def main():
    """基本使用示例"""
    print("🎯 微博 API 基本使用示例")
    print("=" * 50)

    # 1. 创建客户端（使用默认配置）
    client = WeiboClient()
    print("✅ 客户端初始化成功")

    # 2. 创建自定义配置的客户端
    config = WeiboConfig(
        timeout=15.0, max_retries=3, rate_limit_calls=50, rate_limit_window=60
    )
    custom_client = WeiboClient(config=config)
    print("✅ 自定义配置客户端初始化成功")

    # 测试用户ID (雷军)
    user_id = "1749127163"

    # 3. 获取用户信息
    print(f"\n📋 获取用户 {user_id} 的信息...")
    try:
        profile_data = client.get_user_profile(user_id)

        if profile_data and profile_data.get("ok") == 1:
            # 使用 Pydantic 模型解析数据
            user_response = UserDetailResponse.model_validate(profile_data)
            user = user_response.data.user

            print(f"   用户名: {user.screen_name}")
            print(f"   用户ID: {user.id}")
            print(f"   粉丝数: {user.followers_count:,}")
            print(f"   关注数: {user.friends_count:,}")
            print(f"   认证状态: {'已认证' if user.verified else '未认证'}")
            if user.description:
                print(f"   简介: {user.description[:50]}...")
        else:
            print(f"   ❌ 获取用户信息失败: {profile_data}")

    except Exception as e:
        print(f"   ❌ 获取用户信息出错: {e}")

    # 4. 获取用户时间线
    print(f"\n📝 获取用户 {user_id} 的微博时间线...")
    try:
        timeline_data = client.get_user_timeline(user_id, page=1)

        if timeline_data and timeline_data.get("ok") == 1:
            timeline_response = UserTimelineResponse.model_validate(timeline_data)
            posts = timeline_response.data.list

            print(f"   获取到 {len(posts)} 条微博")

            # 显示前3条微博
            for i, post in enumerate(posts[:3], 1):
                print(f"\n   微博 {i}:")
                print(f"     ID: {post.id}")
                print(f"     时间: {post.created_at}")
                print(f"     内容: {post.text[:100]}...")
                print(
                    f"     转发: {post.reposts_count} | 评论: {post.comments_count} | 点赞: {post.attitudes_count}"
                )

                # 如果有图片，显示图片信息
                if post.images:
                    print(f"     图片数量: {len(post.images)}")
                    for j, image in enumerate(post.images[:2], 1):
                        print(f"       图片 {j}: {image.large.url}")

                # 如果有视频，显示视频信息
                if post.page_info:
                    print(f"     视频时长: {post.page_info.duration}秒")
        else:
            print(f"   ❌ 获取时间线失败: {timeline_data}")

    except Exception as e:
        print(f"   ❌ 获取时间线出错: {e}")

    # 5. 获取微博详情
    print(f"\n🔍 获取微博详情...")
    try:
        # 使用一个示例微博ID
        weibo_id = "4567890123456789"  # 这需要是一个真实的微博ID
        detail_data = client.get_weibo_detail(weibo_id)

        if detail_data and not detail_data.get("error"):
            print(f"   ✅ 微博详情获取成功")
            print(f"   数据键: {list(detail_data.keys())}")
        else:
            print(
                f"   ⚠️ 微博详情获取失败或无数据: {detail_data.get('error', '未知错误')}"
            )

    except Exception as e:
        print(f"   ❌ 获取微博详情出错: {e}")

    # 6. 获取微博评论
    print(f"\n💬 获取微博评论...")
    try:
        # 使用一个示例微博ID
        weibo_id = "4567890123456789"  # 这需要是一个真实的微博ID
        comments_data = client.get_weibo_comments(weibo_id)

        if comments_data and comments_data.get("ok") == 1:
            comments_list = comments_data.get("data", {}).get("data", [])
            if comments_list:
                print(f"   获取到 {len(comments_list)} 条评论")

                # 显示前2条评论
                for i, comment_data in enumerate(comments_list[:2], 1):
                    print(f"\n   评论 {i}:")
                    print(
                        f"     用户: {comment_data.get('user', {}).get('screen_name', '未知')}"
                    )
                    print(f"     内容: {comment_data.get('text', '')[:50]}...")
                    print(f"     点赞: {comment_data.get('like_count', 0)}")
            else:
                print(f"   ℹ️ 该微博暂无评论")
        else:
            print(f"   ⚠️ 获取评论失败: {comments_data}")

    except Exception as e:
        print(f"   ❌ 获取评论出错: {e}")

    print(f"\n🎉 基本使用示例完成！")


if __name__ == "__main__":
    main()
