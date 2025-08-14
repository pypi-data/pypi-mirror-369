"""
依赖注入容器模块

提供依赖注入功能，支持接口到实现的注册和获取，以及单例模式支持。
用于解耦组件依赖关系，提高代码的可测试性和可维护性。
"""

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Type, TypeVar, Union

if TYPE_CHECKING:
    from .facade_client import AsyncWeiboClient

from .config import WeiboConfig
from .exceptions import WeiboError

# 类型变量
T = TypeVar("T")


class DependencyError(WeiboError):
    """依赖注入相关错误"""

    pass


class DependencyContainer:
    """依赖注入容器

    提供依赖注入功能，支持：
    - 接口到实现的注册和获取
    - 单例模式支持
    - 工厂方法支持
    - 依赖解析和验证

    特性：
    - 类型安全：支持泛型类型提示
    - 单例管理：自动管理单例实例的生命周期
    - 工厂支持：支持工厂方法创建复杂依赖
    - 错误处理：提供清晰的依赖解析错误信息
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """初始化依赖容器

        Args:
            logger: 可选的日志记录器
        """
        self._dependencies: Dict[Type, Any] = {}
        self._singletons: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable[[], Any]] = {}
        self._singleton_flags: Dict[Type, bool] = {}
        self._call_stack: set[Type] = set()  # For circular dependency detection
        self._logger = logger or logging.getLogger(__name__)

    def register(
        self,
        interface: Type[T],
        implementation: Union[T, Type[T], Callable[[], T]],
        singleton: bool = False,
        as_instance: bool = False,
    ) -> None:
        """注册依赖项

        Args:
            interface: 接口类型
            implementation: 实现类型、实例或工厂方法
            singleton: 是否为单例模式
            as_instance: 是否强制作为实例注册（用于Mock对象等特殊情况）

        Raises:
            DependencyError: 当注册参数无效时
        """
        if interface is None:
            raise DependencyError("接口类型不能为None")

        if implementation is None:
            raise DependencyError("实现不能为None")

        # 清除之前的注册信息
        self.unregister(interface)

        # 获取接口名称，处理Mock对象
        interface_name = getattr(interface, "__name__", str(interface))

        # 如果强制作为实例注册
        if as_instance:
            self._dependencies[interface] = implementation
            if singleton:
                self._singletons[interface] = implementation
                self._singleton_flags[interface] = True
                self._logger.debug(f"注册实例 {interface_name} (单例模式, 强制)")
            else:
                self._logger.debug(f"注册实例 {interface_name} (强制)")
        # 如果是类型
        elif isinstance(implementation, type):
            self._dependencies[interface] = implementation
            implementation_name = getattr(
                implementation, "__name__", str(implementation)
            )
            if singleton:
                self._singleton_flags[interface] = True
                self._logger.debug(
                    f"注册类型 {interface_name} -> {implementation_name} (单例模式)"
                )
            else:
                self._logger.debug(
                    f"注册类型 {interface_name} -> {implementation_name}"
                )
        # 如果是工厂方法（可调用对象，但不是类型）
        elif callable(implementation):
            self._factories[interface] = implementation
            if singleton:
                self._singleton_flags[interface] = True
                self._logger.debug(f"注册工厂方法 {interface_name} (单例模式)")
            else:
                self._logger.debug(f"注册工厂方法 {interface_name}")
        # 如果是实例
        else:
            self._dependencies[interface] = implementation
            if singleton:
                self._singletons[interface] = implementation
                self._singleton_flags[interface] = True
                self._logger.debug(f"注册实例 {interface_name} (单例模式)")
            else:
                self._logger.debug(f"注册实例 {interface_name}")

    def get(self, interface: Type[T]) -> T:
        """获取依赖项实例

        Args:
            interface: 接口类型

        Returns:
            T: 依赖项实例

        Raises:
            DependencyError: 当依赖项未注册或创建失败时
        """
        if interface is None:
            raise DependencyError("接口类型不能为None")

        # 检查循环依赖
        interface_name = getattr(interface, "__name__", str(interface))
        if interface in self._call_stack:
            stack_names = [
                getattr(dep, "__name__", str(dep)) for dep in self._call_stack
            ]
            raise DependencyError(
                f"检测到循环依赖: {' -> '.join(stack_names)} -> {interface_name}"
            )

        # 添加到调用栈
        self._call_stack.add(interface)

        try:
            # 检查是否已有单例实例
            if interface in self._singletons:
                interface_name = getattr(interface, "__name__", str(interface))
                self._logger.debug(f"返回单例实例 {interface_name}")
                return self._singletons[interface]

            # 检查工厂方法
            if interface in self._factories:
                try:
                    factory = self._factories[interface]
                    instance = factory()  # type: ignore

                    # 如果需要单例，保存实例
                    interface_name = getattr(interface, "__name__", str(interface))
                    if self._should_be_singleton(interface):
                        self._singletons[interface] = instance
                        self._logger.debug(f"通过工厂方法创建单例实例 {interface_name}")
                    else:
                        self._logger.debug(f"通过工厂方法创建实例 {interface_name}")

                    return instance  # type: ignore
                except Exception as e:
                    interface_name = getattr(interface, "__name__", str(interface))
                    raise DependencyError(
                        f"工厂方法创建 {interface_name} 失败: {str(e)}"
                    )

            # 检查已注册的依赖
            if interface in self._dependencies:
                implementation = self._dependencies[interface]

                # 如果是实例，直接返回
                if not isinstance(implementation, type):
                    return implementation  # type: ignore

                # 如果是类型，创建实例
                try:
                    instance = implementation()

                    # 如果需要单例，保存实例
                    interface_name = getattr(interface, "__name__", str(interface))
                    if self._should_be_singleton(interface):
                        self._singletons[interface] = instance
                        self._logger.debug(f"创建单例实例 {interface_name}")
                    else:
                        self._logger.debug(f"创建实例 {interface_name}")

                    return instance  # type: ignore
                except Exception as e:
                    interface_name = getattr(interface, "__name__", str(interface))
                    raise DependencyError(f"创建 {interface_name} 实例失败: {str(e)}")

            interface_name = getattr(interface, "__name__", str(interface))
            raise DependencyError(f"依赖项 {interface_name} 未注册")
        finally:
            # 从调用栈中移除
            self._call_stack.discard(interface)

    def _should_be_singleton(self, interface: Type) -> bool:
        """检查接口是否应该是单例

        Args:
            interface: 接口类型

        Returns:
            bool: 是否应该是单例
        """
        return self._singleton_flags.get(interface, False)

    def is_registered(self, interface: Type) -> bool:
        """检查接口是否已注册

        Args:
            interface: 接口类型

        Returns:
            bool: 是否已注册
        """
        return (
            interface in self._dependencies
            or interface in self._factories
            or interface in self._singletons
        )

    def unregister(self, interface: Type) -> None:
        """取消注册依赖项

        Args:
            interface: 接口类型
        """
        interface_name = getattr(interface, "__name__", str(interface))

        if interface in self._dependencies:
            del self._dependencies[interface]
            self._logger.debug(f"取消注册依赖 {interface_name}")

        if interface in self._factories:
            del self._factories[interface]
            self._logger.debug(f"取消注册工厂 {interface_name}")

        if interface in self._singletons:
            del self._singletons[interface]
            self._logger.debug(f"取消注册单例 {interface_name}")

        if interface in self._singleton_flags:
            del self._singleton_flags[interface]

    def clear(self) -> None:
        """清空所有注册的依赖项"""
        self._dependencies.clear()
        self._factories.clear()
        self._singletons.clear()
        self._singleton_flags.clear()
        self._logger.debug("清空所有依赖项")

    def get_registered_interfaces(self) -> list[Type]:
        """获取所有已注册的接口类型

        Returns:
            list: 已注册的接口类型列表
        """
        interfaces: set[Type] = set()
        interfaces.update(self._dependencies.keys())
        interfaces.update(self._factories.keys())
        interfaces.update(self._singletons.keys())
        return list(interfaces)

    def create_client(self, config: Optional[WeiboConfig] = None) -> "AsyncWeiboClient":
        """创建配置好的微博客户端实例

        这是一个工厂方法，用于创建完全配置的AsyncWeiboClient实例，
        自动注入所有必要的依赖项。支持：
        - 自动依赖解析和注入
        - 循环依赖检测
        - 配置驱动的依赖创建

        Args:
            config: 可选的配置对象

        Returns:
            AsyncWeiboClient: 配置好的客户端实例

        Raises:
            DependencyError: 当依赖创建失败或存在循环依赖时
        """
        # 延迟导入避免循环依赖
        from .async_client import AsyncWeiboRawClient
        from .facade_client import AsyncWeiboClient
        from .mapper import WeiboDataMapper

        try:
            # 使用提供的配置或默认配置
            client_config = config or WeiboConfig()

            # 循环依赖检测栈
            dependency_stack: set[Type] = set()

            # 获取或创建依赖项
            raw_client: Optional[AsyncWeiboRawClient] = self._resolve_dependency(
                AsyncWeiboRawClient, client_config, dependency_stack
            )

            mapper: Optional[WeiboDataMapper] = self._resolve_dependency(
                WeiboDataMapper, client_config, dependency_stack
            )

            # 创建客户端实例
            kwargs: Dict[str, Any] = {"config": client_config}

            if raw_client is not None:
                kwargs["raw_client"] = raw_client
                self._logger.debug("注入raw_client依赖")

            if mapper is not None:
                kwargs["mapper"] = mapper
                self._logger.debug("注入mapper依赖")

            client = AsyncWeiboClient(**kwargs)  # type: ignore

            # 记录创建方式
            if raw_client or mapper:
                self._logger.info(
                    f"通过依赖注入创建AsyncWeiboClient (raw_client: {raw_client is not None}, mapper: {mapper is not None})"
                )
            else:
                self._logger.info("使用默认方式创建AsyncWeiboClient")

            return client

        except Exception as e:
            if isinstance(e, DependencyError):
                raise
            raise DependencyError(f"创建AsyncWeiboClient失败: {str(e)}")

    def _resolve_dependency(
        self, interface: Type[T], config: WeiboConfig, dependency_stack: set[Type]
    ) -> Optional[T]:
        """解析依赖项，支持循环依赖检测

        Args:
            interface: 要解析的接口类型
            config: 配置对象
            dependency_stack: 依赖解析栈，用于循环依赖检测

        Returns:
            Optional[T]: 解析的依赖项实例，如果未注册则返回None

        Raises:
            DependencyError: 当存在循环依赖时
        """
        # 检查循环依赖
        interface_name = getattr(interface, "__name__", str(interface))
        if interface in dependency_stack:
            stack_names = [
                getattr(dep, "__name__", str(dep)) for dep in dependency_stack
            ]
            raise DependencyError(
                f"检测到循环依赖: {' -> '.join(stack_names)} -> {interface_name}"
            )

        # 如果未注册，返回None（不自动创建）
        if not self.is_registered(interface):
            self._logger.debug(f"依赖 {interface_name} 未注册")
            return None

        # 添加到依赖栈
        dependency_stack.add(interface)

        try:
            # 获取已注册的依赖
            instance = self.get(interface)
            self._logger.debug(f"解析已注册依赖: {interface_name}")
            return instance
        finally:
            # 从依赖栈中移除
            dependency_stack.discard(interface)

    def _auto_create_dependency(
        self, interface: Type[T], config: WeiboConfig, dependency_stack: set
    ) -> Optional[T]:
        """自动创建依赖项

        根据接口类型和配置自动创建合适的依赖项实例。

        Args:
            interface: 要创建的接口类型
            config: 配置对象
            dependency_stack: 依赖解析栈

        Returns:
            Optional[T]: 创建的依赖项实例，如果无法自动创建则返回None
        """
        from .async_client import AsyncWeiboRawClient
        from .connection_manager import ConnectionManager
        from .mapper import WeiboDataMapper

        interface_name = getattr(interface, "__name__", str(interface))

        # 检查循环依赖
        if interface in dependency_stack:
            stack_names = [
                getattr(dep, "__name__", str(dep)) for dep in dependency_stack
            ]
            raise DependencyError(
                f"自动创建时检测到循环依赖: {' -> '.join(stack_names)} -> {interface_name}"
            )

        # 添加到依赖栈
        dependency_stack.add(interface)

        try:
            # 根据接口类型自动创建实例
            if interface == AsyncWeiboRawClient:
                # 检查是否需要ConnectionManager
                connection_manager = None
                if self.is_registered(ConnectionManager):
                    connection_manager = self._resolve_dependency(
                        ConnectionManager, config, dependency_stack
                    )

                # 创建AsyncWeiboRawClient实例
                instance = AsyncWeiboRawClient(config=config)
                self._logger.info(f"自动创建{interface_name}")

                # 注册为单例以避免重复创建
                self.register(interface, instance, singleton=True, as_instance=True)
                return instance

            elif interface == WeiboDataMapper:
                # 创建WeiboDataMapper实例
                instance = WeiboDataMapper()
                self._logger.info(f"自动创建{interface_name}")

                # 注册为单例以避免重复创建
                self.register(interface, instance, singleton=True, as_instance=True)
                return instance

            elif interface == ConnectionManager:
                # 创建ConnectionManager实例
                instance = ConnectionManager(config)
                self._logger.info(f"自动创建{interface_name}")

                # 注册为单例以避免重复创建
                self.register(interface, instance, singleton=True, as_instance=True)
                return instance

            else:
                # 对于其他类型，尝试直接实例化
                if isinstance(interface, type):
                    # 检查是否为内置类型，不尝试自动创建内置类型
                    if interface.__module__ == "builtins":
                        self._logger.debug(
                            f"无法自动创建{interface_name}: 不支持内置类型"
                        )
                        return None

                    try:
                        instance = interface(config=config)
                        self._logger.info(f"自动创建{interface_name} (带config参数)")
                        self.register(
                            interface, instance, singleton=True, as_instance=True
                        )
                        return instance
                    except TypeError:
                        try:
                            instance = interface()
                            self._logger.info(f"自动创建{interface_name} (无参数)")
                            self.register(
                                interface, instance, singleton=True, as_instance=True
                            )
                            return instance
                        except Exception as e:
                            self._logger.debug(f"无法自动创建{interface_name}: {e}")
                            return None

                self._logger.debug(f"无法自动创建{interface_name}: 不支持的类型")
                return None

        except Exception as e:
            if isinstance(e, DependencyError):
                raise
            self._logger.error(f"自动创建{interface_name}失败: {e}")
            raise DependencyError(f"自动创建{interface_name}失败: {str(e)}")
        finally:
            # 从依赖栈中移除
            dependency_stack.discard(interface)

    def create_production_client(
        self, config: Optional[WeiboConfig] = None
    ) -> "AsyncWeiboClient":
        """创建生产环境客户端

        使用保守配置和完整的监控功能创建适合生产环境的客户端。

        Args:
            config: 可选的配置对象，如果未提供将使用保守配置

        Returns:
            AsyncWeiboClient: 生产环境客户端实例
        """
        # 使用保守配置
        prod_config = config or WeiboConfig.create_conservative_config()

        self._logger.info("创建生产环境客户端")
        return self.create_client(prod_config)

    def create_development_client(
        self, config: Optional[WeiboConfig] = None
    ) -> "AsyncWeiboClient":
        """创建开发环境客户端

        使用快速配置创建适合开发环境的客户端。

        Args:
            config: 可选的配置对象，如果未提供将使用快速配置

        Returns:
            AsyncWeiboClient: 开发环境客户端实例
        """
        # 使用快速配置
        dev_config = config or WeiboConfig.create_fast_config()

        self._logger.info("创建开发环境客户端")
        return self.create_client(dev_config)

    def create_test_client(
        self,
        config: Optional[WeiboConfig] = None,
        mock_raw_client: Optional[Any] = None,
        mock_mapper: Optional[Any] = None,
    ) -> "AsyncWeiboClient":
        """创建测试环境客户端

        支持mock依赖注入的测试客户端创建。

        Args:
            config: 可选的配置对象
            mock_raw_client: 可选的mock raw_client
            mock_mapper: 可选的mock mapper

        Returns:
            AsyncWeiboClient: 测试环境客户端实例
        """
        from .async_client import AsyncWeiboRawClient
        from .mapper import WeiboDataMapper

        # 使用快速配置作为默认测试配置
        test_config = config or WeiboConfig.create_fast_config()

        # 临时注册mock依赖
        original_raw_client = None
        original_mapper = None

        try:
            # 保存原有注册（如果存在）
            if self.is_registered(AsyncWeiboRawClient):
                original_raw_client = self._dependencies.get(AsyncWeiboRawClient)
            if self.is_registered(WeiboDataMapper):
                original_mapper = self._dependencies.get(WeiboDataMapper)

            # 注册mock依赖
            if mock_raw_client is not None:
                self.register(AsyncWeiboRawClient, mock_raw_client, as_instance=True)
                self._logger.debug("注册mock raw_client用于测试")

            if mock_mapper is not None:
                self.register(WeiboDataMapper, mock_mapper, as_instance=True)
                self._logger.debug("注册mock mapper用于测试")

            self._logger.info("创建测试环境客户端")
            return self.create_client(test_config)

        finally:
            # 恢复原有注册
            if mock_raw_client is not None:
                if original_raw_client is not None:
                    self.register(
                        AsyncWeiboRawClient, original_raw_client, as_instance=True
                    )
                else:
                    self.unregister(AsyncWeiboRawClient)

            if mock_mapper is not None:
                if original_mapper is not None:
                    self.register(WeiboDataMapper, original_mapper, as_instance=True)
                else:
                    self.unregister(WeiboDataMapper)

    def validate_dependencies(self) -> Dict[str, Any]:
        """验证所有已注册依赖的完整性

        检查依赖项是否可以正常创建，是否存在循环依赖等问题。

        Returns:
            Dict[str, Any]: 验证结果，包含成功和失败的依赖项信息
        """
        validation_result: Dict[str, Any] = {
            "valid_dependencies": [],
            "invalid_dependencies": [],
            "circular_dependencies": [],
            "missing_dependencies": [],
        }

        interfaces = self.get_registered_interfaces()

        for interface in interfaces:
            interface_name = getattr(interface, "__name__", str(interface))

            try:
                # 尝试创建实例来验证依赖
                dependency_stack: set[Type] = set()
                instance = self._resolve_dependency(
                    interface, WeiboConfig(), dependency_stack
                )

                if instance is not None:
                    validation_result["valid_dependencies"].append(
                        {"interface": interface_name, "type": type(instance).__name__}
                    )
                else:
                    validation_result["missing_dependencies"].append(interface_name)

            except DependencyError as e:
                if "循环依赖" in str(e):
                    validation_result["circular_dependencies"].append(
                        {"interface": interface_name, "error": str(e)}
                    )
                else:
                    validation_result["invalid_dependencies"].append(
                        {"interface": interface_name, "error": str(e)}
                    )
            except Exception as e:
                validation_result["invalid_dependencies"].append(
                    {"interface": interface_name, "error": f"未知错误: {str(e)}"}
                )

        self._logger.info(
            f"依赖验证完成: {len(validation_result['valid_dependencies'])} 个有效, "
            f"{len(validation_result['invalid_dependencies'])} 个无效, "
            f"{len(validation_result['circular_dependencies'])} 个循环依赖"
        )

        return validation_result
