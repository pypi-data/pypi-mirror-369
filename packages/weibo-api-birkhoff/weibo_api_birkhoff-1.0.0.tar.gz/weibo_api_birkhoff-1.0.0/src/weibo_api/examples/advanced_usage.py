"""
高级使用示例

演示微博 API 客户端的高级功能，包括自定义配置、错误处理、数据处理等。
"""

import logging
import time
from datetime import datetime, timedelta

from weibo_api import AsyncWeiboClient, WeiboClient, WeiboConfig
from weibo_api.exceptions import NetworkError, RateLimitError, WeiboError
from weibo_api.models import UserDetailResponse, UserTimelineResponse
from weibo_api.utils import clean_text, format_count

# 设置详细日志
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def custom_configuration_demo():
    """自定义配置示例"""
    print("⚙️ 自定义配置示例")
    print("=" * 50)

    # 1. 快速配置（适用于快速测试）
    fast_config = WeiboConfig.create_fast_config()
    fast_client = WeiboClient(config=fast_config)
    print("✅ 快速配置客户端创建成功")
    print(f"   超时时间: {fast_config.timeout}s")
    print(f"   最大重试: {fast_config.max_retries}次")
    print(
        f"   速率限制: {fast_config.rate_limit_calls}次/{fast_config.rate_limit_window}s"
    )

    # 2. 保守配置（适用于稳定性要求高的场景）
    conservative_config = WeiboConfig.create_conservative_config()
    conservative_client = WeiboClient(config=conservative_config)
    print("\n✅ 保守配置客户端创建成功")
    print(f"   超时时间: {conservative_config.timeout}s")
    print(f"   最大重试: {conservative_config.max_retries}次")
    print(
        f"   速率限制: {conservative_config.rate_limit_calls}次/{conservative_config.rate_limit_window}s"
    )

    # 3. 完全自定义配置
    custom_config = WeiboConfig(
        timeout=20.0,
        max_retries=5,
        retry_delay=2.0,
        rate_limit_calls=30,
        rate_limit_window=60,
        user_agent="Custom Weibo Client 1.0",
    )
    custom_client = WeiboClient(config=custom_config)
    print("\n✅ 自定义配置客户端创建成功")
    print(f"   自定义User-Agent: {custom_config.user_agent}")


def error_handling_demo():
    """错误处理示例"""
    print("\n🛡️ 错误处理示例")
    print("=" * 50)

    client = WeiboClient()

    # 1. 处理网络错误
    print("🌐 网络错误处理...")
    try:
        # 这里可能会因为网络问题失败
        result = client.get_user_profile("1749127163")
        if result:
            print("   ✅ 网络请求成功")
        else:
            print("   ⚠️ 网络请求返回空结果")
    except NetworkError as e:
        print(f"   ❌ 网络错误: {e}")
    except WeiboError as e:
        print(f"   ❌ 微博API错误: {e}")
    except Exception as e:
        print(f"   ❌ 未知错误: {e}")

    # 2. 处理速率限制
    print("\n🚦 速率限制处理...")
    rate_limited_config = WeiboConfig(rate_limit_calls=1, rate_limit_window=5)
    rate_limited_client = WeiboClient(config=rate_limited_config)

    try:
        # 第一次请求应该成功
        result1 = rate_limited_client.get_user_profile("1749127163")
        print("   ✅ 第一次请求成功")

        # 第二次请求应该触发速率限制
        result2 = rate_limited_client.get_user_profile("1749127163")
        print("   ⚠️ 第二次请求意外成功")

    except RateLimitError as e:
        print(f"   ✅ 正确捕获速率限制错误: {e}")
    except Exception as e:
        print(f"   ❌ 意外错误: {e}")


def data_processing_demo():
    """数据处理示例"""
    print("\n📊 数据处理示例")
    print("=" * 50)

    client = WeiboClient()
    user_id = "1749127163"

    try:
        # 获取用户时间线
        timeline_data = client.get_user_timeline(user_id, page=1)

        if timeline_data and timeline_data.get("ok") == 1:
            timeline_response = UserTimelineResponse.model_validate(timeline_data)
            posts = timeline_response.data.list

            print(f"📈 分析 {len(posts)} 条微博数据:")

            # 1. 统计数据
            total_reposts = sum(post.reposts_count for post in posts)
            total_comments = sum(post.comments_count for post in posts)
            total_likes = sum(post.attitudes_count for post in posts)

            print(f"   总转发数: {format_count(total_reposts)}")
            print(f"   总评论数: {format_count(total_comments)}")
            print(f"   总点赞数: {format_count(total_likes)}")

            # 2. 时间分析
            if posts:
                latest_time = posts[0].created_at
                oldest_time = posts[-1].created_at
                time_span = latest_time - oldest_time

                print(f"\n⏰ 时间分析:")
                print(f"   最新微博: {latest_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   最早微博: {oldest_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   时间跨度: {time_span.days}天")

            # 3. 内容分析
            print(f"\n📝 内容分析:")

            # 统计带图片的微博
            posts_with_images = [post for post in posts if post.images]
            print(
                f"   带图片微博: {len(posts_with_images)}/{len(posts)} ({len(posts_with_images)/len(posts)*100:.1f}%)"
            )

            # 统计带视频的微博
            posts_with_video = [post for post in posts if post.page_info]
            print(
                f"   带视频微博: {len(posts_with_video)}/{len(posts)} ({len(posts_with_video)/len(posts)*100:.1f}%)"
            )

            # 文本长度分析
            text_lengths = [len(clean_text(post.text)) for post in posts]
            avg_length = sum(text_lengths) / len(text_lengths) if text_lengths else 0
            print(f"   平均文本长度: {avg_length:.1f}字符")

            # 4. 热门微博分析
            print(f"\n🔥 热门微博分析:")

            # 按点赞数排序
            posts_by_likes = sorted(
                posts, key=lambda x: x.attitudes_count, reverse=True
            )
            top_post = posts_by_likes[0] if posts_by_likes else None

            if top_post:
                print(f"   最热门微博:")
                print(f"     内容: {clean_text(top_post.text)[:100]}...")
                print(f"     点赞: {format_count(top_post.attitudes_count)}")
                print(f"     转发: {format_count(top_post.reposts_count)}")
                print(f"     评论: {format_count(top_post.comments_count)}")
                print(
                    f"     发布时间: {top_post.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
                )

            # 5. 图片信息分析
            if posts_with_images:
                print(f"\n🖼️ 图片信息分析:")
                total_images = sum(len(post.images) for post in posts_with_images)
                print(f"   总图片数: {total_images}")
                print(
                    f"   平均每条微博图片数: {total_images/len(posts_with_images):.1f}"
                )

                # 分析图片尺寸
                if posts_with_images[0].images:
                    sample_image = posts_with_images[0].images[0]
                    print(f"   示例图片尺寸:")
                    print(
                        f"     缩略图: {sample_image.thumbnail.width}x{sample_image.thumbnail.height}"
                    )
                    print(
                        f"     大图: {sample_image.large.width}x{sample_image.large.height}"
                    )
                    print(
                        f"     原图: {sample_image.original.width}x{sample_image.original.height}"
                    )

        else:
            print("❌ 无法获取时间线数据")

    except Exception as e:
        print(f"❌ 数据处理出错: {e}")


def batch_processing_demo():
    """批量处理示例"""
    print("\n📦 批量处理示例")
    print("=" * 50)

    client = WeiboClient()

    # 批量获取多个用户的信息
    user_ids = ["1749127163", "1749127163", "1749127163"]  # 示例用户ID
    user_info_list = []

    print(f"🔄 批量获取 {len(user_ids)} 个用户的信息...")

    for i, user_id in enumerate(user_ids, 1):
        try:
            print(f"   处理用户 {i}/{len(user_ids)}: {user_id}")

            profile_data = client.get_user_profile(user_id)

            if profile_data and profile_data.get("ok") == 1:
                user_response = UserDetailResponse.model_validate(profile_data)
                user = user_response.data.user

                user_info = {
                    "id": user.id,
                    "name": user.screen_name,
                    "followers": user.followers_count,
                    "friends": user.friends_count,
                    "verified": user.verified,
                }
                user_info_list.append(user_info)

                print(
                    f"     ✅ {user.screen_name} - 粉丝: {format_count(user.followers_count)}"
                )
            else:
                print(f"     ❌ 获取失败")

            # 添加延迟避免速率限制
            time.sleep(1)

        except Exception as e:
            print(f"     ❌ 处理出错: {e}")

    # 汇总结果
    if user_info_list:
        print(f"\n📊 批量处理结果汇总:")
        print(f"   成功处理: {len(user_info_list)}/{len(user_ids)}")

        total_followers = sum(user["followers"] for user in user_info_list)
        verified_count = sum(1 for user in user_info_list if user["verified"])

        print(f"   总粉丝数: {format_count(total_followers)}")
        print(f"   认证用户: {verified_count}/{len(user_info_list)}")


def performance_monitoring_demo():
    """性能监控示例"""
    print("\n⏱️ 性能监控示例")
    print("=" * 50)

    client = WeiboClient()
    user_id = "1749127163"

    # 监控不同API的性能
    apis = [
        ("用户信息", lambda: client.get_user_profile(user_id)),
        ("用户时间线", lambda: client.get_user_timeline(user_id, page=1)),
        ("微博详情", lambda: client.get_weibo_detail("4567890123456789")),
    ]

    performance_results = []

    for api_name, api_func in apis:
        print(f"🔍 测试 {api_name} API性能...")

        start_time = time.time()
        try:
            result = api_func()
            end_time = time.time()

            duration = end_time - start_time
            success = result is not None and not result.get("error")

            performance_results.append(
                {"api": api_name, "duration": duration, "success": success}
            )

            status = "✅ 成功" if success else "❌ 失败"
            print(f"   {status} - 耗时: {duration:.3f}s")

        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time

            performance_results.append(
                {
                    "api": api_name,
                    "duration": duration,
                    "success": False,
                    "error": str(e),
                }
            )

            print(f"   ❌ 异常 - 耗时: {duration:.3f}s - 错误: {e}")

    # 性能汇总
    print(f"\n📊 性能汇总:")
    successful_apis = [r for r in performance_results if r["success"]]

    if successful_apis:
        avg_duration = sum(r["duration"] for r in successful_apis) / len(
            successful_apis
        )
        fastest_api = min(successful_apis, key=lambda x: x["duration"])
        slowest_api = max(successful_apis, key=lambda x: x["duration"])

        print(f"   平均响应时间: {avg_duration:.3f}s")
        print(f"   最快API: {fastest_api['api']} ({fastest_api['duration']:.3f}s)")
        print(f"   最慢API: {slowest_api['api']} ({slowest_api['duration']:.3f}s)")

    success_rate = len(successful_apis) / len(performance_results) * 100
    print(f"   成功率: {success_rate:.1f}%")


def main():
    """主函数"""
    print("🎯 微博 API 高级使用示例")
    print("时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)

    # 运行各种高级示例
    custom_configuration_demo()
    error_handling_demo()
    data_processing_demo()
    batch_processing_demo()
    performance_monitoring_demo()

    print("\n🎉 高级示例完成！")


if __name__ == "__main__":
    main()
