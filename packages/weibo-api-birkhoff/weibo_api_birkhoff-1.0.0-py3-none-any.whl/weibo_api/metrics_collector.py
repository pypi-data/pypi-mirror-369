"""
性能指标收集器模块

提供API调用性能指标的收集、统计和导出功能。
"""

import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


@dataclass
class RequestMetrics:
    """单个请求的指标数据"""

    endpoint: str
    duration: float
    success: bool
    timestamp: datetime
    error_type: Optional[str] = None


@dataclass
class EndpointStats:
    """端点统计信息"""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_duration: float = 0.0
    durations: deque = field(
        default_factory=lambda: deque(maxlen=1000)
    )  # 保留最近1000次请求的响应时间
    error_counts: Dict[str, int] = field(default_factory=dict)


class MetricsCollector:
    """
    性能指标收集器

    负责收集和统计API调用的性能指标，包括：
    - 请求计数和成功率
    - 响应时间统计
    - 错误分类统计
    - 缓存命中率统计

    线程安全，支持并发访问。
    """

    def __init__(self, enabled: bool = True, max_history: int = 10000):
        """
        初始化指标收集器

        Args:
            enabled: 是否启用指标收集
            max_history: 最大历史记录数量
        """
        self.enabled = enabled
        self.max_history = max_history

        # 线程安全锁
        self._lock = threading.RLock()

        # 端点统计信息
        self._endpoint_stats: Dict[str, EndpointStats] = defaultdict(EndpointStats)

        # 全局统计
        self._total_requests = 0
        self._total_successful_requests = 0
        self._total_failed_requests = 0
        self._total_duration = 0.0

        # 缓存统计
        self._cache_hits = 0
        self._cache_misses = 0

        # 错误统计
        self._error_counts: Dict[str, int] = defaultdict(int)

        # 历史记录
        self._request_history: deque = deque(maxlen=max_history)

        # 启动时间
        self._start_time = datetime.now()

    def record_request(
        self,
        endpoint: str,
        duration: float,
        success: bool,
        error_type: Optional[str] = None,
    ) -> None:
        """
        记录API请求指标

        Args:
            endpoint: API端点名称
            duration: 请求持续时间（秒）
            success: 请求是否成功
            error_type: 错误类型（如果失败）
        """
        if not self.enabled:
            return

        with self._lock:
            # 更新全局统计
            self._total_requests += 1
            self._total_duration += duration

            if success:
                self._total_successful_requests += 1
            else:
                self._total_failed_requests += 1
                if error_type:
                    self._error_counts[error_type] += 1

            # 更新端点统计
            stats = self._endpoint_stats[endpoint]
            stats.total_requests += 1
            stats.total_duration += duration
            stats.durations.append(duration)

            if success:
                stats.successful_requests += 1
            else:
                stats.failed_requests += 1
                if error_type:
                    stats.error_counts[error_type] = (
                        stats.error_counts.get(error_type, 0) + 1
                    )

            # 添加到历史记录
            metrics = RequestMetrics(
                endpoint=endpoint,
                duration=duration,
                success=success,
                timestamp=datetime.now(),
                error_type=error_type,
            )
            self._request_history.append(metrics)

    def record_cache_hit(self, hit: bool) -> None:
        """
        记录缓存命中情况

        Args:
            hit: 是否命中缓存
        """
        if not self.enabled:
            return

        with self._lock:
            if hit:
                self._cache_hits += 1
            else:
                self._cache_misses += 1

    def record_error(self, error_type: str) -> None:
        """
        记录错误统计

        Args:
            error_type: 错误类型
        """
        if not self.enabled:
            return

        with self._lock:
            self._error_counts[error_type] += 1

    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            包含所有统计信息的字典
        """
        if not self.enabled:
            return {"enabled": False}

        with self._lock:
            # 计算全局统计
            uptime = datetime.now() - self._start_time
            total_cache_requests = self._cache_hits + self._cache_misses

            stats: Dict[str, Any] = {
                "enabled": True,
                "uptime_seconds": uptime.total_seconds(),
                "start_time": self._start_time.isoformat(),
                "total_requests": self._total_requests,
                "successful_requests": self._total_successful_requests,
                "failed_requests": self._total_failed_requests,
                "success_rate": self._total_successful_requests
                / max(self._total_requests, 1),
                "error_rate": self._total_failed_requests
                / max(self._total_requests, 1),
                "average_response_time": self._total_duration
                / max(self._total_requests, 1),
                "total_response_time": self._total_duration,
                "cache_hits": self._cache_hits,
                "cache_misses": self._cache_misses,
                "cache_hit_rate": self._cache_hits / max(total_cache_requests, 1),
                "error_breakdown": dict(self._error_counts),
                "endpoints": {},
            }

            # 计算端点统计
            for endpoint, endpoint_stats in self._endpoint_stats.items():
                durations = list(endpoint_stats.durations)
                if durations:
                    durations.sort()
                    n = len(durations)
                    # 使用更准确的百分位数计算
                    p50_idx = max(0, (n - 1) // 2)
                    p95_idx = max(0, min(n - 1, int((n - 1) * 0.95)))
                    p99_idx = max(0, min(n - 1, int((n - 1) * 0.99)))

                    p50 = durations[p50_idx]
                    p95 = durations[p95_idx]
                    p99 = durations[p99_idx]
                else:
                    p50 = p95 = p99 = 0

                stats["endpoints"][endpoint] = {
                    "total_requests": endpoint_stats.total_requests,
                    "successful_requests": endpoint_stats.successful_requests,
                    "failed_requests": endpoint_stats.failed_requests,
                    "success_rate": endpoint_stats.successful_requests
                    / max(endpoint_stats.total_requests, 1),
                    "average_response_time": endpoint_stats.total_duration
                    / max(endpoint_stats.total_requests, 1),
                    "p50_response_time": p50,
                    "p95_response_time": p95,
                    "p99_response_time": p99,
                    "error_breakdown": dict(endpoint_stats.error_counts),
                }

            return stats

    def reset_stats(self) -> None:
        """重置所有统计信息"""
        if not self.enabled:
            return

        with self._lock:
            # 重置全局统计
            self._total_requests = 0
            self._total_successful_requests = 0
            self._total_failed_requests = 0
            self._total_duration = 0.0

            # 重置缓存统计
            self._cache_hits = 0
            self._cache_misses = 0

            # 重置错误统计
            self._error_counts.clear()

            # 重置端点统计
            self._endpoint_stats.clear()

            # 清空历史记录
            self._request_history.clear()

            # 重置启动时间
            self._start_time = datetime.now()

    def get_recent_requests(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取最近的请求记录

        Args:
            limit: 返回记录数量限制

        Returns:
            最近请求记录列表
        """
        if not self.enabled:
            return []

        with self._lock:
            recent = list(self._request_history)[-limit:]
            return [
                {
                    "endpoint": req.endpoint,
                    "duration": req.duration,
                    "success": req.success,
                    "timestamp": req.timestamp.isoformat(),
                    "error_type": req.error_type,
                }
                for req in recent
            ]

    def get_endpoint_stats(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """
        获取特定端点的统计信息

        Args:
            endpoint: 端点名称

        Returns:
            端点统计信息，如果不存在则返回None
        """
        if not self.enabled:
            return None

        with self._lock:
            if endpoint not in self._endpoint_stats:
                return None

            stats = self._endpoint_stats[endpoint]
            durations = list(stats.durations)
            if durations:
                durations.sort()
                n = len(durations)
                # 使用更准确的百分位数计算
                p50_idx = max(0, (n - 1) // 2)
                p95_idx = max(0, min(n - 1, int((n - 1) * 0.95)))
                p99_idx = max(0, min(n - 1, int((n - 1) * 0.99)))

                p50 = durations[p50_idx]
                p95 = durations[p95_idx]
                p99 = durations[p99_idx]
            else:
                p50 = p95 = p99 = 0

            return {
                "endpoint": endpoint,
                "total_requests": stats.total_requests,
                "successful_requests": stats.successful_requests,
                "failed_requests": stats.failed_requests,
                "success_rate": stats.successful_requests
                / max(stats.total_requests, 1),
                "average_response_time": stats.total_duration
                / max(stats.total_requests, 1),
                "p50_response_time": p50,
                "p95_response_time": p95,
                "p99_response_time": p99,
                "error_breakdown": dict(stats.error_counts),
            }

    def is_enabled(self) -> bool:
        """检查指标收集是否启用"""
        return self.enabled

    def enable(self) -> None:
        """启用指标收集"""
        self.enabled = True

    def disable(self) -> None:
        """禁用指标收集"""
        self.enabled = False


def create_metrics_collector(
    enabled: bool = True, max_history: int = 10000
) -> MetricsCollector:
    """
    创建指标收集器实例

    Args:
        enabled: 是否启用指标收集
        max_history: 最大历史记录数量

    Returns:
        MetricsCollector实例
    """
    return MetricsCollector(enabled=enabled, max_history=max_history)
