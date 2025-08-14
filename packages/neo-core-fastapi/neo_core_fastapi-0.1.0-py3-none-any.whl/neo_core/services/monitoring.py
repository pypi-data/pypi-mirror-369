"""Monitoring and metrics services."""

from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import time
import psutil
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
from enum import Enum
from pydantic import BaseModel

from .base import BaseService, ServiceException
from ..config import CoreSettings


class MonitoringException(ServiceException):
    """Monitoring-related exception."""
    pass


class MetricType(str, Enum):
    """Metric types."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class AlertLevel(str, Enum):
    """Alert levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class HealthStatus(str, Enum):
    """Health check status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class Metric:
    """Metric data structure."""
    name: str
    value: Union[int, float]
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)
    description: Optional[str] = None


@dataclass
class Alert:
    """Alert data structure."""
    id: str
    name: str
    level: AlertLevel
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class HealthCheck(BaseModel):
    """Health check model."""
    name: str
    status: HealthStatus
    message: Optional[str] = None
    timestamp: datetime
    duration_ms: Optional[float] = None
    details: Optional[Dict[str, Any]] = None
    
    def __init__(self, **data):
        if 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)


class SystemMetrics(BaseModel):
    """System metrics model."""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_total_mb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    network_sent_mb: float
    network_recv_mb: float
    load_average: Optional[List[float]] = None
    process_count: int
    timestamp: datetime
    
    def __init__(self, **data):
        if 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)


class ApplicationMetrics(BaseModel):
    """Application metrics model."""
    request_count: int = 0
    error_count: int = 0
    response_time_avg: float = 0.0
    response_time_p95: float = 0.0
    response_time_p99: float = 0.0
    active_connections: int = 0
    database_connections: int = 0
    cache_hit_rate: float = 0.0
    timestamp: datetime
    
    def __init__(self, **data):
        if 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)


class MetricsCollector:
    """Metrics collection and storage."""
    
    def __init__(self, max_metrics: int = 10000):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_metrics))
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()
    
    def record_metric(self, metric: Metric) -> None:
        """Record a metric."""
        with self._lock:
            self.metrics[metric.name].append(metric)
            
            if metric.metric_type == MetricType.COUNTER:
                self.counters[metric.name] += metric.value
            elif metric.metric_type == MetricType.GAUGE:
                self.gauges[metric.name] = metric.value
            elif metric.metric_type == MetricType.HISTOGRAM:
                self.histograms[metric.name].append(metric.value)
                # Keep only last 1000 values for histograms
                if len(self.histograms[metric.name]) > 1000:
                    self.histograms[metric.name] = self.histograms[metric.name][-1000:]
            elif metric.metric_type == MetricType.TIMER:
                self.timers[metric.name].append(metric.value)
                # Keep only last 1000 values for timers
                if len(self.timers[metric.name]) > 1000:
                    self.timers[metric.name] = self.timers[metric.name][-1000:]
    
    def get_metrics(self, name: str, limit: Optional[int] = None) -> List[Metric]:
        """Get metrics by name."""
        with self._lock:
            metrics = list(self.metrics[name])
            if limit:
                return metrics[-limit:]
            return metrics
    
    def get_counter_value(self, name: str) -> float:
        """Get counter value."""
        with self._lock:
            return self.counters[name]
    
    def get_gauge_value(self, name: str) -> float:
        """Get gauge value."""
        with self._lock:
            return self.gauges[name]
    
    def get_histogram_stats(self, name: str) -> Dict[str, float]:
        """Get histogram statistics."""
        with self._lock:
            values = self.histograms[name]
            if not values:
                return {}
            
            sorted_values = sorted(values)
            count = len(sorted_values)
            
            return {
                'count': count,
                'min': min(sorted_values),
                'max': max(sorted_values),
                'mean': sum(sorted_values) / count,
                'p50': sorted_values[int(count * 0.5)],
                'p95': sorted_values[int(count * 0.95)],
                'p99': sorted_values[int(count * 0.99)]
            }
    
    def get_timer_stats(self, name: str) -> Dict[str, float]:
        """Get timer statistics."""
        return self.get_histogram_stats(name)
    
    def clear_metrics(self, name: Optional[str] = None) -> None:
        """Clear metrics."""
        with self._lock:
            if name:
                if name in self.metrics:
                    self.metrics[name].clear()
                self.counters.pop(name, None)
                self.gauges.pop(name, None)
                self.histograms.pop(name, None)
                self.timers.pop(name, None)
            else:
                self.metrics.clear()
                self.counters.clear()
                self.gauges.clear()
                self.histograms.clear()
                self.timers.clear()


class AlertManager:
    """Alert management."""
    
    def __init__(self, max_alerts: int = 1000):
        self.alerts: deque = deque(maxlen=max_alerts)
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_handlers: List[Callable[[Alert], None]] = []
        self._lock = threading.Lock()
    
    def add_alert_handler(self, handler: Callable[[Alert], None]) -> None:
        """Add alert handler."""
        self.alert_handlers.append(handler)
    
    def create_alert(
        self,
        name: str,
        level: AlertLevel,
        message: str,
        source: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> Alert:
        """Create and register alert."""
        alert_id = f"{name}_{int(time.time())}"
        alert = Alert(
            id=alert_id,
            name=name,
            level=level,
            message=message,
            source=source,
            tags=tags or {}
        )
        
        with self._lock:
            self.alerts.append(alert)
            if level in [AlertLevel.ERROR, AlertLevel.CRITICAL]:
                self.active_alerts[alert_id] = alert
        
        # Notify handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                # Don't let handler errors break alert creation
                pass
        
        return alert
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an active alert."""
        with self._lock:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.resolved = True
                alert.resolved_at = datetime.utcnow()
                del self.active_alerts[alert_id]
                return True
            return False
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        with self._lock:
            return list(self.active_alerts.values())
    
    def get_alerts(
        self,
        level: Optional[AlertLevel] = None,
        limit: Optional[int] = None
    ) -> List[Alert]:
        """Get alerts with optional filtering."""
        with self._lock:
            alerts = list(self.alerts)
            
            if level:
                alerts = [a for a in alerts if a.level == level]
            
            if limit:
                alerts = alerts[-limit:]
            
            return alerts


class HealthCheckManager:
    """Health check management."""
    
    def __init__(self):
        self.health_checks: Dict[str, Callable[[], HealthCheck]] = {}
        self.last_results: Dict[str, HealthCheck] = {}
        self._lock = threading.Lock()
    
    def register_health_check(
        self,
        name: str,
        check_func: Callable[[], HealthCheck]
    ) -> None:
        """Register a health check."""
        with self._lock:
            self.health_checks[name] = check_func
    
    def run_health_check(self, name: str) -> HealthCheck:
        """Run a specific health check."""
        if name not in self.health_checks:
            return HealthCheck(
                name=name,
                status=HealthStatus.UNKNOWN,
                message=f"Health check '{name}' not found"
            )
        
        start_time = time.time()
        try:
            result = self.health_checks[name]()
            result.duration_ms = (time.time() - start_time) * 1000
        except Exception as e:
            result = HealthCheck(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000
            )
        
        with self._lock:
            self.last_results[name] = result
        
        return result
    
    def run_all_health_checks(self) -> Dict[str, HealthCheck]:
        """Run all registered health checks."""
        results = {}
        for name in self.health_checks:
            results[name] = self.run_health_check(name)
        return results
    
    def get_overall_health(self) -> HealthStatus:
        """Get overall system health status."""
        results = self.run_all_health_checks()
        
        if not results:
            return HealthStatus.UNKNOWN
        
        statuses = [result.status for result in results.values()]
        
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        elif all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN


class SystemMonitor:
    """System resource monitoring."""
    
    def __init__(self):
        self.last_network_stats = None
        self.start_time = time.time()
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_mb = memory.used / (1024 * 1024)
        memory_total_mb = memory.total / (1024 * 1024)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        disk_used_gb = disk.used / (1024 * 1024 * 1024)
        disk_total_gb = disk.total / (1024 * 1024 * 1024)
        
        # Network usage
        network = psutil.net_io_counters()
        network_sent_mb = network.bytes_sent / (1024 * 1024)
        network_recv_mb = network.bytes_recv / (1024 * 1024)
        
        # Load average (Unix-like systems only)
        load_average = None
        try:
            load_average = list(psutil.getloadavg())
        except AttributeError:
            # Windows doesn't have load average
            pass
        
        # Process count
        process_count = len(psutil.pids())
        
        return SystemMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_mb=memory_used_mb,
            memory_total_mb=memory_total_mb,
            disk_percent=disk_percent,
            disk_used_gb=disk_used_gb,
            disk_total_gb=disk_total_gb,
            network_sent_mb=network_sent_mb,
            network_recv_mb=network_recv_mb,
            load_average=load_average,
            process_count=process_count
        )
    
    def get_process_metrics(self, pid: Optional[int] = None) -> Dict[str, Any]:
        """Get metrics for a specific process."""
        try:
            if pid is None:
                process = psutil.Process()
            else:
                process = psutil.Process(pid)
            
            return {
                'pid': process.pid,
                'name': process.name(),
                'cpu_percent': process.cpu_percent(),
                'memory_percent': process.memory_percent(),
                'memory_info': process.memory_info()._asdict(),
                'num_threads': process.num_threads(),
                'create_time': process.create_time(),
                'status': process.status()
            }
        except psutil.NoSuchProcess:
            return {}
        except Exception as e:
            return {'error': str(e)}


class MonitoringService(BaseService):
    """Main monitoring service."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(settings)
        
        # Initialize components
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.health_check_manager = HealthCheckManager()
        self.system_monitor = SystemMonitor()
        
        # Monitoring settings
        self.monitoring_interval = getattr(self.settings, 'MONITORING_INTERVAL', 60)  # seconds
        self.enable_system_monitoring = getattr(self.settings, 'ENABLE_SYSTEM_MONITORING', True)
        self.alert_thresholds = getattr(self.settings, 'ALERT_THRESHOLDS', {
            'cpu_percent': 80,
            'memory_percent': 85,
            'disk_percent': 90,
            'response_time_p95': 5000  # ms
        })
        
        # Background monitoring
        self._monitoring_active = False
        self._monitoring_thread = None
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Application metrics
        self.app_metrics = ApplicationMetrics()
        
        # Register default health checks
        self._register_default_health_checks()
        
        self.logger.info("Monitoring service initialized")
    
    def start_monitoring(self) -> None:
        """Start background monitoring."""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitoring_thread.start()
        
        self.logger.info("Background monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop background monitoring."""
        self._monitoring_active = False
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)
        
        self.logger.info("Background monitoring stopped")
    
    def _monitoring_loop(self) -> None:
        """Background monitoring loop."""
        while self._monitoring_active:
            try:
                if self.enable_system_monitoring:
                    self._collect_system_metrics()
                    self._check_system_alerts()
                
                time.sleep(self.monitoring_interval)
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(5)  # Short sleep on error
    
    def _collect_system_metrics(self) -> None:
        """Collect system metrics."""
        try:
            system_metrics = self.system_monitor.get_system_metrics()
            
            # Record metrics
            self.record_gauge('system.cpu_percent', system_metrics.cpu_percent)
            self.record_gauge('system.memory_percent', system_metrics.memory_percent)
            self.record_gauge('system.disk_percent', system_metrics.disk_percent)
            self.record_gauge('system.process_count', system_metrics.process_count)
            
            if system_metrics.load_average:
                self.record_gauge('system.load_average_1m', system_metrics.load_average[0])
                self.record_gauge('system.load_average_5m', system_metrics.load_average[1])
                self.record_gauge('system.load_average_15m', system_metrics.load_average[2])
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {str(e)}")
    
    def _check_system_alerts(self) -> None:
        """Check for system alert conditions."""
        try:
            # CPU alert
            cpu_percent = self.metrics_collector.get_gauge_value('system.cpu_percent')
            if cpu_percent > self.alert_thresholds.get('cpu_percent', 80):
                self.alert_manager.create_alert(
                    name='high_cpu_usage',
                    level=AlertLevel.WARNING,
                    message=f'High CPU usage: {cpu_percent:.1f}%',
                    source='system_monitor'
                )
            
            # Memory alert
            memory_percent = self.metrics_collector.get_gauge_value('system.memory_percent')
            if memory_percent > self.alert_thresholds.get('memory_percent', 85):
                self.alert_manager.create_alert(
                    name='high_memory_usage',
                    level=AlertLevel.WARNING,
                    message=f'High memory usage: {memory_percent:.1f}%',
                    source='system_monitor'
                )
            
            # Disk alert
            disk_percent = self.metrics_collector.get_gauge_value('system.disk_percent')
            if disk_percent > self.alert_thresholds.get('disk_percent', 90):
                self.alert_manager.create_alert(
                    name='high_disk_usage',
                    level=AlertLevel.ERROR,
                    message=f'High disk usage: {disk_percent:.1f}%',
                    source='system_monitor'
                )
        except Exception as e:
            self.logger.error(f"Failed to check system alerts: {str(e)}")
    
    def _register_default_health_checks(self) -> None:
        """Register default health checks."""
        def database_health_check() -> HealthCheck:
            # This would typically check database connectivity
            # For now, return a simple check
            return HealthCheck(
                name='database',
                status=HealthStatus.HEALTHY,
                message='Database connection OK'
            )
        
        def cache_health_check() -> HealthCheck:
            # This would typically check cache connectivity
            return HealthCheck(
                name='cache',
                status=HealthStatus.HEALTHY,
                message='Cache connection OK'
            )
        
        def disk_space_health_check() -> HealthCheck:
            try:
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                
                if disk_percent > 95:
                    status = HealthStatus.UNHEALTHY
                    message = f'Critical disk usage: {disk_percent:.1f}%'
                elif disk_percent > 85:
                    status = HealthStatus.DEGRADED
                    message = f'High disk usage: {disk_percent:.1f}%'
                else:
                    status = HealthStatus.HEALTHY
                    message = f'Disk usage OK: {disk_percent:.1f}%'
                
                return HealthCheck(
                    name='disk_space',
                    status=status,
                    message=message,
                    details={'disk_percent': disk_percent}
                )
            except Exception as e:
                return HealthCheck(
                    name='disk_space',
                    status=HealthStatus.UNHEALTHY,
                    message=f'Failed to check disk space: {str(e)}'
                )
        
        self.health_check_manager.register_health_check('database', database_health_check)
        self.health_check_manager.register_health_check('cache', cache_health_check)
        self.health_check_manager.register_health_check('disk_space', disk_space_health_check)
    
    # Metrics recording methods
    def record_counter(self, name: str, value: Union[int, float] = 1, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a counter metric."""
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.COUNTER,
            tags=tags or {}
        )
        self.metrics_collector.record_metric(metric)
    
    def record_gauge(self, name: str, value: Union[int, float], tags: Optional[Dict[str, str]] = None) -> None:
        """Record a gauge metric."""
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            tags=tags or {}
        )
        self.metrics_collector.record_metric(metric)
    
    def record_histogram(self, name: str, value: Union[int, float], tags: Optional[Dict[str, str]] = None) -> None:
        """Record a histogram metric."""
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.HISTOGRAM,
            tags=tags or {}
        )
        self.metrics_collector.record_metric(metric)
    
    def record_timer(self, name: str, value: Union[int, float], tags: Optional[Dict[str, str]] = None) -> None:
        """Record a timer metric."""
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.TIMER,
            tags=tags or {}
        )
        self.metrics_collector.record_metric(metric)
    
    def time_function(self, name: str, tags: Optional[Dict[str, str]] = None):
        """Decorator to time function execution."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration = (time.time() - start_time) * 1000  # Convert to milliseconds
                    self.record_timer(name, duration, tags)
            return wrapper
        return decorator
    
    # Application metrics
    def increment_request_count(self) -> None:
        """Increment request count."""
        self.app_metrics.request_count += 1
        self.record_counter('app.requests')
    
    def increment_error_count(self) -> None:
        """Increment error count."""
        self.app_metrics.error_count += 1
        self.record_counter('app.errors')
    
    def record_response_time(self, duration_ms: float) -> None:
        """Record response time."""
        self.record_timer('app.response_time', duration_ms)
    
    def update_active_connections(self, count: int) -> None:
        """Update active connections count."""
        self.app_metrics.active_connections = count
        self.record_gauge('app.active_connections', count)
    
    def update_cache_hit_rate(self, rate: float) -> None:
        """Update cache hit rate."""
        self.app_metrics.cache_hit_rate = rate
        self.record_gauge('app.cache_hit_rate', rate)
    
    # Query methods
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        return {
            'counters': dict(self.metrics_collector.counters),
            'gauges': dict(self.metrics_collector.gauges),
            'histogram_stats': {
                name: self.metrics_collector.get_histogram_stats(name)
                for name in self.metrics_collector.histograms
            },
            'timer_stats': {
                name: self.metrics_collector.get_timer_stats(name)
                for name in self.metrics_collector.timers
            }
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        system_metrics = self.system_monitor.get_system_metrics()
        health_checks = self.health_check_manager.run_all_health_checks()
        overall_health = self.health_check_manager.get_overall_health()
        
        return {
            'overall_health': overall_health,
            'system_metrics': system_metrics.dict(),
            'health_checks': {name: check.dict() for name, check in health_checks.items()},
            'active_alerts': [alert.__dict__ for alert in self.alert_manager.get_active_alerts()],
            'monitoring_active': self._monitoring_active
        }
    
    def get_application_metrics(self) -> ApplicationMetrics:
        """Get current application metrics."""
        # Update calculated metrics
        response_time_stats = self.metrics_collector.get_timer_stats('app.response_time')
        if response_time_stats:
            self.app_metrics.response_time_avg = response_time_stats.get('mean', 0)
            self.app_metrics.response_time_p95 = response_time_stats.get('p95', 0)
            self.app_metrics.response_time_p99 = response_time_stats.get('p99', 0)
        
        self.app_metrics.timestamp = datetime.utcnow()
        return self.app_metrics
    
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        if format == "json":
            data = {
                'timestamp': datetime.utcnow().isoformat(),
                'system_status': self.get_system_status(),
                'application_metrics': self.get_application_metrics().dict(),
                'metrics_summary': self.get_metrics_summary()
            }
            return json.dumps(data, indent=2, default=str)
        else:
            raise MonitoringException(f"Unsupported export format: {format}")
    
    def health_check(self) -> Dict[str, Any]:
        """Check monitoring service health."""
        try:
            # Test metrics collection
            test_metric = Metric(
                name='test_metric',
                value=1,
                metric_type=MetricType.COUNTER
            )
            self.metrics_collector.record_metric(test_metric)
            metrics_ok = self.metrics_collector.get_counter_value('test_metric') > 0
            
            # Test alert creation
            test_alert = self.alert_manager.create_alert(
                name='test_alert',
                level=AlertLevel.INFO,
                message='Test alert'
            )
            alerts_ok = test_alert is not None
            
            # Test health checks
            health_results = self.health_check_manager.run_all_health_checks()
            health_checks_ok = len(health_results) > 0
            
            is_healthy = all([metrics_ok, alerts_ok, health_checks_ok])
            
            return {
                'healthy': is_healthy,
                'monitoring_active': self._monitoring_active,
                'checks': {
                    'metrics_collection': metrics_ok,
                    'alert_management': alerts_ok,
                    'health_checks': health_checks_ok
                }
            }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }