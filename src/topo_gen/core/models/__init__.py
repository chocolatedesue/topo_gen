"""
Models 包 - 拓扑生成器数据模型

此包包含所有配置和数据模型类。
"""

# 基础
from .base import BaseConfig
from .network import NetworkConfig

# 协议配置
from .protocols import OSPFConfig, BGPConfig, ISISConfig, BFDConfig

# 路由器和链路
from .router import RouterInfo, LinkInfo

# 拓扑配置
from .topology import TopologyConfig, SpecialTopologyConfig

# 生成相关
from .generation import GenerationResult, SystemRequirements

__all__ = [
    # 基础
    "BaseConfig",
    "NetworkConfig",
    # 协议配置
    "OSPFConfig",
    "BGPConfig",
    "ISISConfig",
    "BFDConfig",
    # 路由器和链路
    "RouterInfo",
    "LinkInfo",
    # 拓扑配置
    "TopologyConfig",
    "SpecialTopologyConfig",
    # 生成结果
    "GenerationResult",
    "SystemRequirements",
]
