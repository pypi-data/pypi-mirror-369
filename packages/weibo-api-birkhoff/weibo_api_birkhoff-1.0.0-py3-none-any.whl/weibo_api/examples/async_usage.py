"""
异步使用示例

演示异步微博 API 客户端的使用方法，包括并发请求。
使用新的Facade Pattern架构，提供类型安全的Pydantic模型。
"""

import asyncio
import logging
import time

from weibo_api import AsyncWeiboClient, WeiboConfig
from weibo_api.models import WeiboComment, WeiboPost, WeiboUser

# 设置日志
logging.basicConfig(level=logging.INFO)


async def basic_async_usage():
    """基本异步使用示例 - 使用新的Facade API"""
    print("🚀 异步微博 API 基本使用示例 (Facade Pattern)")
    print("=" * 50)

    # 创建异步客户端 (Facade层)
    client = AsyncWeiboClient()
    print("✅ 异步客户端初始化成功")

    user_id = "1749127163"

    # 1. 异步获取用户信息 - 返回强类型的WeiboUser模型
    print(f"\n📋 异步获取用户 {user_id} 的信息...")
    try:
        user = await client.get_user_profile(user_id)

        if user:
            print(f"   用户名: {user.screen_name}")
            print(f"   粉丝数: {user.followers_count:,}")
            print(f"   认证状态: {'✅ 已认证' if user.verified else '❌ 未认证'}")
            if user.description:
                print(f"   个人简介: {user.description[:50]}...")
        else:
            print(f"   ❌ 获取用户信息失败")

    except Exception as e:
        print(f"   ❌ 异步获取用户信息出错: {e}")

    # 2. 异步获取用户时间线 - 返回WeiboPost列表
    print(f"\n📝 异步获取用户时间线...")
    try:
        posts = await client.get_user_timeline(user_id, page=1)

        if posts:
            print(f"   异步获取到 {len(posts)} 条微博")

            if posts:
                latest_post = posts[0]
                print(f"   最新微博: {latest_post.text[:50]}...")
                print(f"   转发数: {latest_post.reposts_count}")
                print(f"   评论数: {latest_post.comments_count}")
                print(f"   点赞数: {latest_post.attitudes_count}")

                # 3. 获取微博详情
                print(f"\n📄 获取微博详情...")
                try:
                    detail_post = await client.get_weibo_detail(str(latest_post.id))
                    if detail_post:
                        print(f"   详情获取成功: {detail_post.text[:30]}...")
                except Exception as e:
                    print(f"   ⚠️ 获取微博详情失败: {e}")

                # 4. 获取微博评论
                print(f"\n💬 获取微博评论...")
                try:
                    comments = await client.get_weibo_comments(str(latest_post.id))
                    if comments:
                        print(f"   获取到 {len(comments)} 条评论")
                        if comments:
                            first_comment = comments[0]
                            print(f"   首条评论: {first_comment.text[:30]}...")
                    else:
                        print(f"   该微博暂无评论")
                except Exception as e:
                    print(f"   ⚠️ 获取评论失败: {e}")
        else:
            print(f"   ❌ 异步获取时间线失败")

    except Exception as e:
        print(f"   ❌ 异步获取时间线出错: {e}")


async def concurrent_requests_demo():
    """并发请求示例"""
    print("\n⚡ 并发请求示例")
    print("=" * 50)

    client = AsyncWeiboClient()

    # 测试多个用户ID
    user_ids = ["1749127163", "1749127163", "1749127163"]  # 使用相同ID测试

    # 1. 串行请求（对比用）
    print("🐌 串行请求测试...")
    start_time = time.time()

    serial_results = []
    for user_id in user_ids:
        try:
            result = await client.get_user_profile(user_id)
            serial_results.append(result)
        except Exception as e:
            serial_results.append({"error": str(e)})

    serial_time = time.time() - start_time
    print(f"   串行请求耗时: {serial_time:.2f}s")

    # 2. 并发请求
    print("\n⚡ 并发请求测试...")
    start_time = time.time()

    # 创建并发任务
    tasks = [client.get_user_profile(user_id) for user_id in user_ids]

    # 并发执行
    concurrent_results = await asyncio.gather(*tasks, return_exceptions=True)

    concurrent_time = time.time() - start_time
    print(f"   并发请求耗时: {concurrent_time:.2f}s")

    # 性能对比
    if serial_time > 0:
        improvement = ((serial_time - concurrent_time) / serial_time) * 100
        print(f"   性能提升: {improvement:.1f}%")

    # 验证结果
    success_count = sum(
        1
        for result in concurrent_results
        if not isinstance(result, Exception) and result is not None
    )
    print(f"   成功请求: {success_count}/{len(concurrent_results)}")

    # 显示第一个成功结果的详细信息
    for result in concurrent_results:
        if not isinstance(result, Exception) and result:
            print(
                f"   示例结果: {result.screen_name} (粉丝: {result.followers_count:,})"
            )
            break


async def mixed_api_concurrent_demo():
    """混合API并发调用示例"""
    print("\n🔀 混合API并发调用示例")
    print("=" * 50)

    client = AsyncWeiboClient()
    user_id = "1749127163"

    # 创建不同类型的API调用任务
    tasks = [
        ("用户信息", client.get_user_profile(user_id)),
        ("用户时间线", client.get_user_timeline(user_id, page=1)),
        ("微博详情", client.get_weibo_detail("4567890123456789")),  # 示例ID
    ]

    print("🚀 同时调用多个不同的API...")
    start_time = time.time()

    # 并发执行所有任务
    results = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)

    end_time = time.time()
    print(f"   总耗时: {end_time - start_time:.2f}s")

    # 显示结果
    for i, (api_name, result) in enumerate(zip([task[0] for task in tasks], results)):
        if isinstance(result, Exception):
            print(f"   {api_name}: ❌ 异常 - {result}")
        elif result and not result.get("error"):
            print(f"   {api_name}: ✅ 成功")
        else:
            print(f"   {api_name}: ⚠️ 失败或无数据")


async def rate_limiting_demo():
    """速率限制演示"""
    print("\n🚦 速率限制演示")
    print("=" * 50)

    # 创建严格速率限制的配置
    config = WeiboConfig(rate_limit_calls=3, rate_limit_window=5)  # 5秒内最多3次请求
    client = AsyncWeiboClient(config=config)

    user_id = "1749127163"

    print("🚀 快速发起5个请求（速率限制：5秒内最多3次）...")
    start_time = time.time()

    # 创建5个请求任务
    tasks = [client.get_user_profile(user_id) for _ in range(5)]

    # 并发执行（会自动处理速率限制）
    results = await asyncio.gather(*tasks, return_exceptions=True)

    end_time = time.time()
    total_time = end_time - start_time

    print(f"   总耗时: {total_time:.2f}s")
    print(f"   平均每请求: {total_time/5:.2f}s")

    # 统计结果
    success_count = sum(
        1
        for result in results
        if not isinstance(result, Exception) and result and result.get("ok") == 1
    )
    print(f"   成功请求: {success_count}/{len(results)}")

    # 由于速率限制，总时间应该大于5秒
    if total_time >= 4:  # 允许一些误差
        print("   ✅ 速率限制正常工作")
    else:
        print("   ⚠️ 速率限制可能未生效")


async def error_handling_demo():
    """错误处理演示"""
    print("\n🛡️ 错误处理演示")
    print("=" * 50)

    client = AsyncWeiboClient()

    # 1. 测试无效用户ID
    print("🔍 测试无效用户ID...")
    try:
        result = await client.get_user_profile("999999999999")
        if result and result.get("error"):
            print(f"   ✅ 正确处理无效用户ID: {result['error']}")
        else:
            print(f"   ⚠️ 无效用户ID返回了数据: {result}")
    except Exception as e:
        print(f"   ❌ 处理无效用户ID时出现异常: {e}")

    # 2. 测试无效微博ID
    print("\n🔍 测试无效微博ID...")
    try:
        result = await client.get_weibo_detail("invalid_id")
        if result and result.get("error"):
            print(f"   ✅ 正确处理无效微博ID: {result['error']}")
        else:
            print(f"   ⚠️ 无效微博ID返回了数据")
    except Exception as e:
        print(f"   ❌ 处理无效微博ID时出现异常: {e}")


async def main():
    """主函数"""
    print("🎯 异步微博 API 完整示例")
    print("时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)

    # 运行各种示例
    await basic_async_usage()
    await concurrent_requests_demo()
    await mixed_api_concurrent_demo()
    await rate_limiting_demo()
    await error_handling_demo()

    print("\n🎉 异步示例完成！")


if __name__ == "__main__":
    asyncio.run(main())
