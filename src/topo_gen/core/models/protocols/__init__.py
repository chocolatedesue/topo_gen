"""协议配置包"""
from .ospf import OSPFConfig
from .bgp import BGPConfig
from .isis import ISISConfig
from .bfd import BFDConfig

__all__ = [
    "OSPFConfig",
    "BGPConfig",
    "ISISConfig",
    "BFDConfig",
]
