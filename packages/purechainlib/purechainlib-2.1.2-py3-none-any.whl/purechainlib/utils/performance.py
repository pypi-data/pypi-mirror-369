"""
Performance measurement utilities for PureChain operations
Tracks latency, throughput, and success rates
"""

import time
import statistics
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
import asyncio
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn

console = Console()


@dataclass
class PerformanceMetric:
    """Single performance measurement"""
    operation: str
    start_time: float
    end_time: float
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def latency_ms(self) -> float:
        """Get latency in milliseconds"""
        return (self.end_time - self.start_time) * 1000
    
    @property
    def latency_seconds(self) -> float:
        """Get latency in seconds"""
        return self.end_time - self.start_time


@dataclass
class PerformanceStats:
    """Aggregated performance statistics"""
    operation: str
    total_calls: int
    successful_calls: int
    failed_calls: int
    min_latency_ms: float
    max_latency_ms: float
    avg_latency_ms: float
    median_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    throughput_per_sec: float
    success_rate: float
    total_time_seconds: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'operation': self.operation,
            'total_calls': self.total_calls,
            'successful_calls': self.successful_calls,
            'failed_calls': self.failed_calls,
            'min_latency_ms': round(self.min_latency_ms, 2),
            'max_latency_ms': round(self.max_latency_ms, 2),
            'avg_latency_ms': round(self.avg_latency_ms, 2),
            'median_latency_ms': round(self.median_latency_ms, 2),
            'p95_latency_ms': round(self.p95_latency_ms, 2),
            'p99_latency_ms': round(self.p99_latency_ms, 2),
            'throughput_per_sec': round(self.throughput_per_sec, 2),
            'success_rate': round(self.success_rate * 100, 2),
            'total_time_seconds': round(self.total_time_seconds, 2)
        }


class PerformanceMonitor:
    """
    Performance monitoring for PureChain operations
    Tracks latency, throughput, and success rates
    """
    
    def __init__(self):
        """Initialize performance monitor"""
        self.metrics: List[PerformanceMetric] = []
        self.start_time = time.time()
        self.operations: Dict[str, List[PerformanceMetric]] = {}
    
    def measure(self, operation: str):
        """
        Decorator to measure function performance
        
        Args:
            operation: Operation name
        """
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start = time.perf_counter()
                success = True
                error = None
                result = None
                
                try:
                    result = await func(*args, **kwargs)
                except Exception as e:
                    success = False
                    error = str(e)
                    raise
                finally:
                    end = time.perf_counter()
                    metric = PerformanceMetric(
                        operation=operation,
                        start_time=start,
                        end_time=end,
                        success=success,
                        error=error
                    )
                    self.add_metric(metric)
                
                return result
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start = time.perf_counter()
                success = True
                error = None
                result = None
                
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    success = False
                    error = str(e)
                    raise
                finally:
                    end = time.perf_counter()
                    metric = PerformanceMetric(
                        operation=operation,
                        start_time=start,
                        end_time=end,
                        success=success,
                        error=error
                    )
                    self.add_metric(metric)
                
                return result
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    def add_metric(self, metric: PerformanceMetric):
        """Add a performance metric"""
        self.metrics.append(metric)
        
        if metric.operation not in self.operations:
            self.operations[metric.operation] = []
        self.operations[metric.operation].append(metric)
    
    async def measure_operation(self, operation: str, func: Callable, *args, **kwargs) -> Any:
        """
        Measure a single operation
        
        Args:
            operation: Operation name
            func: Function to measure
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
        """
        start = time.perf_counter()
        success = True
        error = None
        result = None
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
        except Exception as e:
            success = False
            error = str(e)
            raise
        finally:
            end = time.perf_counter()
            metric = PerformanceMetric(
                operation=operation,
                start_time=start,
                end_time=end,
                success=success,
                error=error
            )
            self.add_metric(metric)
        
        return result
    
    def get_stats(self, operation: Optional[str] = None) -> Dict[str, PerformanceStats]:
        """
        Get performance statistics
        
        Args:
            operation: Specific operation or None for all
            
        Returns:
            Dictionary of operation -> PerformanceStats
        """
        stats = {}
        
        operations_to_analyze = {}
        if operation:
            if operation in self.operations:
                operations_to_analyze[operation] = self.operations[operation]
        else:
            operations_to_analyze = self.operations
        
        for op_name, metrics in operations_to_analyze.items():
            if not metrics:
                continue
            
            latencies = [m.latency_ms for m in metrics if m.success]
            successful = [m for m in metrics if m.success]
            failed = [m for m in metrics if not m.success]
            
            if latencies:
                sorted_latencies = sorted(latencies)
                p95_index = int(len(sorted_latencies) * 0.95)
                p99_index = int(len(sorted_latencies) * 0.99)
                
                total_time = sum(m.latency_seconds for m in metrics)
                
                stats[op_name] = PerformanceStats(
                    operation=op_name,
                    total_calls=len(metrics),
                    successful_calls=len(successful),
                    failed_calls=len(failed),
                    min_latency_ms=min(latencies),
                    max_latency_ms=max(latencies),
                    avg_latency_ms=statistics.mean(latencies),
                    median_latency_ms=statistics.median(latencies),
                    p95_latency_ms=sorted_latencies[min(p95_index, len(sorted_latencies)-1)],
                    p99_latency_ms=sorted_latencies[min(p99_index, len(sorted_latencies)-1)],
                    throughput_per_sec=len(metrics) / total_time if total_time > 0 else 0,
                    success_rate=len(successful) / len(metrics),
                    total_time_seconds=total_time
                )
            else:
                # All failed
                stats[op_name] = PerformanceStats(
                    operation=op_name,
                    total_calls=len(metrics),
                    successful_calls=0,
                    failed_calls=len(failed),
                    min_latency_ms=0,
                    max_latency_ms=0,
                    avg_latency_ms=0,
                    median_latency_ms=0,
                    p95_latency_ms=0,
                    p99_latency_ms=0,
                    throughput_per_sec=0,
                    success_rate=0,
                    total_time_seconds=0
                )
        
        return stats
    
    def print_report(self, detailed: bool = True):
        """
        Print performance report
        
        Args:
            detailed: Show detailed statistics
        """
        stats = self.get_stats()
        
        if not stats:
            console.print("[yellow]No performance data collected[/yellow]")
            return
        
        # Create summary table
        table = Table(title="🚀 PureChain Performance Report", 
                     title_style="bold cyan",
                     show_header=True,
                     header_style="bold magenta")
        
        table.add_column("Operation", style="cyan", width=25)
        table.add_column("Calls", justify="right", style="green")
        table.add_column("Success Rate", justify="right", style="green")
        table.add_column("Avg Latency", justify="right", style="yellow")
        table.add_column("P95 Latency", justify="right", style="yellow")
        table.add_column("P99 Latency", justify="right", style="yellow")
        table.add_column("Throughput", justify="right", style="blue")
        
        total_calls = 0
        total_successful = 0
        total_time = 0
        
        for op_name, stat in stats.items():
            table.add_row(
                op_name,
                str(stat.total_calls),
                f"{stat.success_rate * 100:.1f}%",
                f"{stat.avg_latency_ms:.2f}ms",
                f"{stat.p95_latency_ms:.2f}ms",
                f"{stat.p99_latency_ms:.2f}ms",
                f"{stat.throughput_per_sec:.2f}/s"
            )
            
            total_calls += stat.total_calls
            total_successful += stat.successful_calls
            total_time += stat.total_time_seconds
        
        console.print(table)
        
        # Overall summary
        overall_success_rate = (total_successful / total_calls * 100) if total_calls > 0 else 0
        overall_throughput = total_calls / total_time if total_time > 0 else 0
        
        summary = Panel(
            f"[bold]Overall Statistics[/bold]\n\n"
            f"📊 Total Operations: {total_calls}\n"
            f"✅ Success Rate: {overall_success_rate:.1f}%\n"
            f"⚡ Throughput: {overall_throughput:.2f} ops/sec\n"
            f"⏱️  Total Time: {total_time:.2f} seconds\n"
            f"💸 [bold yellow]Gas Cost: 0 (Zero gas blockchain!)[/bold yellow]",
            title="Summary",
            border_style="green"
        )
        console.print(summary)
        
        if detailed:
            # Detailed breakdown
            console.print("\n[bold cyan]Detailed Metrics:[/bold cyan]")
            for op_name, stat in stats.items():
                detail = Panel(
                    f"[bold]{op_name}[/bold]\n"
                    f"├─ Total Calls: {stat.total_calls}\n"
                    f"├─ Successful: {stat.successful_calls}\n"
                    f"├─ Failed: {stat.failed_calls}\n"
                    f"├─ Min Latency: {stat.min_latency_ms:.2f}ms\n"
                    f"├─ Max Latency: {stat.max_latency_ms:.2f}ms\n"
                    f"├─ Median: {stat.median_latency_ms:.2f}ms\n"
                    f"└─ Total Time: {stat.total_time_seconds:.2f}s",
                    border_style="blue"
                )
                console.print(detail)
    
    def export_metrics(self) -> Dict[str, Any]:
        """
        Export metrics for analysis
        
        Returns:
            Dictionary of metrics data
        """
        stats = self.get_stats()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_runtime_seconds': time.time() - self.start_time,
            'operations': {name: stat.to_dict() for name, stat in stats.items()},
            'raw_metrics': [
                {
                    'operation': m.operation,
                    'latency_ms': m.latency_ms,
                    'success': m.success,
                    'error': m.error
                }
                for m in self.metrics
            ]
        }
    
    def reset(self):
        """Reset all metrics"""
        self.metrics = []
        self.operations = {}
        self.start_time = time.time()


class LoadTester:
    """
    Load testing utilities for PureChain
    Tests throughput under concurrent load
    """
    
    def __init__(self, monitor: PerformanceMonitor):
        """
        Initialize load tester
        
        Args:
            monitor: Performance monitor instance
        """
        self.monitor = monitor
    
    async def run_concurrent(self, func: Callable, args_list: List[tuple], 
                            max_concurrent: int = 10, operation_name: str = "load_test") -> List[Any]:
        """
        Run function concurrently with different arguments
        
        Args:
            func: Async function to test
            args_list: List of argument tuples
            max_concurrent: Maximum concurrent executions
            operation_name: Name for performance tracking
            
        Returns:
            List of results
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def run_with_semaphore(args):
            async with semaphore:
                return await self.monitor.measure_operation(operation_name, func, *args)
        
        tasks = [run_with_semaphore(args) for args in args_list]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task(f"[cyan]Running {operation_name}...", total=len(tasks))
            
            results = []
            for coro in asyncio.as_completed(tasks):
                result = await coro
                results.append(result)
                progress.advance(task)
        
        return results