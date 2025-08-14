"""
Facade Pattern 架构演示

展示新的微博API架构的特性：
1. Facade Pattern - 简化的高级API接口
2. 防腐层 (Anti-Corruption Layer) - 数据映射和验证
3. 类型安全 - 强类型的Pydantic模型
4. 底层访问 - 直接使用原始客户端
"""

import asyncio
import logging
from typing import List

from weibo_api import AsyncWeiboClient, AsyncWeiboRawClient, WeiboDataMapper
from weibo_api.models import WeiboComment, WeiboPost, WeiboUser

# 设置日志
logging.basicConfig(level=logging.INFO)


async def facade_vs_raw_demo():
    """Facade层 vs 原始客户端对比演示"""
    print("🏗️ Facade Pattern vs Raw Client 对比演示")
    print("=" * 60)

    user_id = "1749127163"

    # 1. 使用Facade层客户端 (推荐方式)
    print("\n✨ 使用Facade层客户端 (AsyncWeiboClient)")
    print("-" * 40)

    facade_client = AsyncWeiboClient()

    try:
        # 获取用户信息 - 返回强类型的WeiboUser
        user = await facade_client.get_user_profile(user_id)
        print(f"📋 用户信息 (类型: {type(user).__name__})")
        print(f"   用户名: {user.screen_name}")
        print(f"   粉丝数: {user.followers_count:,}")
        print(f"   认证状态: {user.verified}")

        # 获取时间线 - 返回WeiboPost列表
        posts = await facade_client.get_user_timeline(user_id, page=1)
        print(f"\n📝 时间线 (类型: List[{type(posts[0]).__name__}])")
        print(f"   获取到 {len(posts)} 条微博")
        if posts:
            print(f"   最新微博: {posts[0].text[:50]}...")

    except Exception as e:
        print(f"❌ Facade客户端出错: {e}")

    # 2. 使用原始客户端 (底层访问)
    print("\n🔧 使用原始客户端 (AsyncWeiboRawClient)")
    print("-" * 40)

    raw_client = AsyncWeiboRawClient()

    try:
        # 获取用户信息 - 返回原始JSON字典
        raw_user_data = await raw_client.get_user_profile(user_id)
        print(f"📋 用户信息 (类型: {type(raw_user_data).__name__})")
        print(f"   原始数据结构: {list(raw_user_data.keys())}")

        # 获取时间线 - 返回原始JSON字典
        raw_timeline_data = await raw_client.get_user_timeline(user_id, page=1)
        print(f"\n📝 时间线 (类型: {type(raw_timeline_data).__name__})")
        print(f"   原始数据结构: {list(raw_timeline_data.keys())}")

    except Exception as e:
        print(f"❌ 原始客户端出错: {e}")


async def type_safety_demo():
    """类型安全演示"""
    print("\n🛡️ 类型安全演示")
    print("=" * 60)

    client = AsyncWeiboClient()
    user_id = "1749127163"

    try:
        # 获取用户信息
        user = await client.get_user_profile(user_id)

        print("✅ 类型安全的属性访问:")
        print(f"   user.screen_name: {user.screen_name} (str)")
        print(f"   user.followers_count: {user.followers_count:,} (int)")
        print(f"   user.verified: {user.verified} (bool)")

        # IDE会提供自动补全和类型检查
        print("\n🔍 IDE支持:")
        print("   - 自动补全: user.[Tab] 显示所有可用属性")
        print("   - 类型检查: 编译时发现类型错误")
        print("   - 文档提示: 鼠标悬停显示属性说明")

        # 获取时间线
        posts = await client.get_user_timeline(user_id, page=1)
        if posts:
            post = posts[0]
            print(f"\n📝 微博对象属性:")
            print(f"   post.id: {post.id} (int)")
            print(f"   post.text: {post.text[:30]}... (str)")
            print(f"   post.reposts_count: {post.reposts_count} (int)")
            print(f"   post.user.screen_name: {post.user.screen_name} (str)")

    except Exception as e:
        print(f"❌ 类型安全演示出错: {e}")


async def data_validation_demo():
    """数据验证演示"""
    print("\n🔍 数据验证演示")
    print("=" * 60)

    # 演示防腐层的数据验证功能
    mapper = WeiboDataMapper()

    print("✅ 有效数据验证:")
    try:
        from weibo_api.models import UserProfileRawDTO

        # 模拟有效的API响应
        valid_dto = UserProfileRawDTO(
            ok=1,
            data={
                "user": {
                    "id": 1749127163,
                    "screen_name": "雷军",
                    "profile_image_url": "https://example.com/avatar.jpg",
                    "avatar_hd": "https://example.com/avatar_hd.jpg",
                    "followers_count": 25000000,
                    "friends_count": 1000,
                    "verified": True,
                }
            },
        )

        user = mapper.map_user_profile(valid_dto)
        print(f"   ✅ 数据验证通过: {user.screen_name}")

    except Exception as e:
        print(f"   ❌ 有效数据验证失败: {e}")

    print("\n❌ 无效数据验证:")
    try:
        from weibo_api.models import UserProfileRawDTO

        # 模拟无效的API响应
        invalid_dto = UserProfileRawDTO(ok=0, data={})  # 错误的状态码

        user = mapper.map_user_profile(invalid_dto)
        print(f"   ⚠️ 无效数据竟然通过了验证")

    except Exception as e:
        print(f"   ✅ 正确拒绝无效数据: {e}")


async def mixed_architecture_demo():
    """混合架构演示 - 同时使用Facade和Raw客户端"""
    print("\n🔀 混合架构演示")
    print("=" * 60)

    # 创建Facade客户端
    facade_client = AsyncWeiboClient()

    # 获取底层原始客户端的引用
    raw_client = facade_client.raw_client

    user_id = "1749127163"

    print("🎯 使用场景: 大部分时候用Facade，特殊需求用Raw")

    try:
        # 1. 常规操作使用Facade (类型安全、易用)
        print("\n📋 常规操作 - 使用Facade层:")
        user = await facade_client.get_user_profile(user_id)
        print(f"   用户: {user.screen_name} (类型安全)")

        # 2. 特殊需求使用Raw (灵活性、原始数据)
        print("\n🔧 特殊需求 - 使用Raw层:")
        raw_data = await raw_client.get_user_profile(user_id)
        print(f"   原始响应包含 {len(raw_data)} 个字段")
        print(f"   可以访问Facade层未暴露的字段")

        # 3. 自定义数据处理
        if "data" in raw_data and "user" in raw_data["data"]:
            raw_user = raw_data["data"]["user"]
            custom_info = {
                "display_name": f"{raw_user.get('screen_name', '')} ({'认证' if raw_user.get('verified') else '未认证'})",
                "follower_level": (
                    "大V"
                    if raw_user.get("followers_count", 0) > 1000000
                    else "普通用户"
                ),
                "raw_fields_count": len(raw_user),
            }
            print(f"   自定义处理结果: {custom_info}")

    except Exception as e:
        print(f"❌ 混合架构演示出错: {e}")


async def performance_comparison_demo():
    """性能对比演示"""
    print("\n⚡ 性能对比演示")
    print("=" * 60)

    import time

    user_id = "1749127163"

    # 1. Facade层性能测试
    print("🏗️ Facade层性能测试:")
    facade_client = AsyncWeiboClient()

    start_time = time.time()
    try:
        user = await facade_client.get_user_profile(user_id)
        facade_time = time.time() - start_time
        print(f"   耗时: {facade_time:.3f}s (包含数据验证和映射)")
    except Exception as e:
        print(f"   ❌ Facade测试失败: {e}")
        facade_time = 0

    # 2. Raw层性能测试
    print("\n🔧 Raw层性能测试:")
    raw_client = AsyncWeiboRawClient()

    start_time = time.time()
    try:
        raw_data = await raw_client.get_user_profile(user_id)
        raw_time = time.time() - start_time
        print(f"   耗时: {raw_time:.3f}s (仅网络请求)")
    except Exception as e:
        print(f"   ❌ Raw测试失败: {e}")
        raw_time = 0

    # 3. 性能分析
    if facade_time > 0 and raw_time > 0:
        overhead = facade_time - raw_time
        overhead_percent = (overhead / raw_time) * 100
        print(f"\n📊 性能分析:")
        print(f"   Facade层额外开销: {overhead:.3f}s ({overhead_percent:.1f}%)")
        print(f"   换取收益: 类型安全 + 数据验证 + 易用性")


async def main():
    """主演示函数"""
    print("🎯 微博API Facade Pattern 架构演示")
    print("时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)

    # 运行各种演示
    await facade_vs_raw_demo()
    await type_safety_demo()
    await data_validation_demo()
    await mixed_architecture_demo()
    await performance_comparison_demo()

    print("\n🎉 Facade Pattern 演示完成！")
    print("\n💡 总结:")
    print("   ✅ Facade层: 类型安全、易用、数据验证")
    print("   ✅ Raw层: 灵活性、原始数据、高性能")
    print("   ✅ 防腐层: 隔离外部变化、数据映射")
    print("   ✅ 混合使用: 根据需求选择合适的层次")


if __name__ == "__main__":
    asyncio.run(main())
