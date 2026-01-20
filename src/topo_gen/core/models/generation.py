"""生成结果和系统需求模块"""
from __future__ import annotations

from typing import Optional, Dict, Any, List
from pathlib import Path
from pydantic import Field

from .base import BaseConfig
from .topology import TopologyConfig

class SystemRequirements(BaseConfig):
    """系统需求"""
    min_memory_gb: float = Field(description="最小内存需求(GB)")
    recommended_memory_gb: float = Field(description="推荐内存需求(GB)")
    min_disk_gb: float = Field(description="最小磁盘需求(GB)")
    min_cpus: int = Field(description="最小CPU核心数")
    recommended_cpus: int = Field(description="推荐CPU核心数")
    max_workers_config: int = Field(default=6, ge=1, le=32, description="配置生成最大工作线程")
    max_workers_filesystem: int = Field(default=4, ge=1, le=16, description="文件系统最大工作线程")
    
    @classmethod
    def calculate_for_topology(cls, config: TopologyConfig) -> SystemRequirements:
        """根据拓扑配置计算系统需求"""
        base_memory = config.total_routers * 0.015  # 每个路由器15MB (实测约7.4MB)
        if config.enable_bgp:
            base_memory *= 1.5  # BGP增加50%内存需求
        if config.enable_bfd:
            base_memory *= 1.2  # BFD增加20%内存需求
            
        return cls(
            min_memory_gb=base_memory,
            recommended_memory_gb=base_memory * 1.5,
            min_disk_gb=config.total_routers * 0.015,  # 15MB/node for logs
            min_cpus=2,
            recommended_cpus=max(2, 1 + (config.total_routers // 25)),
            max_workers_config=min(6, max(1, config.total_routers // 50)),
            max_workers_filesystem=min(4, max(1, config.total_routers // 100))
        )

class GenerationResult(BaseConfig):
    """生成结果，支持位置参数和关键字参数"""
    success: bool = Field(description="是否成功")
    message: str = Field(description="结果消息")
    output_dir: Optional[Path] = Field(default=None, description="输出目录")
    error_details: Optional[str] = Field(default=None, description="错误详情")
    stats: Optional[Dict[str, Any]] = Field(default=None, description="生成统计信息")
    errors: Optional[List[str]] = Field(default=None, description="错误列表")

    def __init__(self, *args, **kwargs):
        """支持位置参数和关键字参数的构造函数

        支持的调用方式：
        - GenerationResult(success, message)  # 位置参数
        - GenerationResult(success, message, output_dir)  # 位置参数
        - GenerationResult(success=success, message=message)  # 关键字参数
        """
        if len(args) == 2 and not kwargs:
            # 位置参数调用: GenerationResult(success, message)
            super().__init__(success=args[0], message=args[1])
        elif len(args) == 3 and not kwargs:
            # 位置参数调用: GenerationResult(success, message, output_dir)
            super().__init__(success=args[0], message=args[1], output_dir=args[2])
        elif len(args) == 0:
            # 关键字参数调用: GenerationResult(success=success, message=message)
            super().__init__(**kwargs)
        else:
            raise TypeError(f"Invalid arguments for GenerationResult: args={args}, kwargs={kwargs}")
