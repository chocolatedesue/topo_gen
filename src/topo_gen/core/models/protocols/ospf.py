"""OSPF协议配置"""
from typing import Optional
from pydantic import Field, field_validator, computed_field

from ..base import BaseConfig
from ...types import AreaID
from ....config.defaults import (
    OSPF_DEFAULT_HELLO_INTERVAL,
    OSPF_DEFAULT_DEAD_INTERVAL,
    OSPF_DEFAULT_SPF_DELAY_MS,
    OSPF_DEFAULT_AREA_ID,
    OSPF_DEFAULT_RETRANSMIT_INTERVAL,
    OSPF_DEFAULT_TRANSMIT_DELAY,
    OSPF_DEFAULT_LSA_MIN_ARRIVAL_MS,
    OSPF_DEFAULT_MAXIMUM_PATHS,
)


class OSPFConfig(BaseConfig):
    """OSPF配置"""
    
    # 基本计时器
    hello_interval: int = Field(
        default=OSPF_DEFAULT_HELLO_INTERVAL, 
        ge=1, le=65535, 
        description="Hello间隔(秒)"
   )
    dead_interval: int = Field(
        default=OSPF_DEFAULT_DEAD_INTERVAL, 
        ge=1, le=65535, 
        description="Dead间隔(秒)"
    )
    spf_delay: int = Field(
        default=OSPF_DEFAULT_SPF_DELAY_MS, 
        ge=1, le=65535, 
        description="SPF延迟(毫秒)"
    )
    
    # 区域和接口配置
    area_id: AreaID = Field(default=OSPF_DEFAULT_AREA_ID, description="区域ID")
    cost: Optional[int] = Field(default=None, ge=1, le=65535, description="接口开销")
    priority: Optional[int] = Field(default=None, ge=0, le=255, description="路由器优先级")
    
    # 高级配置
    retransmit_interval: int = Field(
        default=OSPF_DEFAULT_RETRANSMIT_INTERVAL, 
        ge=1, le=3600, 
        description="重传间隔(秒)"
    )
    transmit_delay: int = Field(
        default=OSPF_DEFAULT_TRANSMIT_DELAY, 
        ge=1, le=3600, 
        description="传输延迟(秒)"
    )
    authentication_type: Optional[str] = Field(default=None, description="认证类型")
    lsa_min_arrival: int = Field(
        default=OSPF_DEFAULT_LSA_MIN_ARRIVAL_MS, 
        ge=10, le=60000, 
        description="LSA最小到达间隔(毫秒)"
    )
    maximum_paths: int = Field(
        default=OSPF_DEFAULT_MAXIMUM_PATHS, 
        ge=1, le=128, 
        description="ECMP最大路径数"
    )
    lsa_only_mode: bool = Field(default=False, description="仅交换LSA模式")
    
    @field_validator('dead_interval')
    @classmethod
    def validate_dead_interval(cls, v: int, info) -> int:
        """验证Dead间隔必须大于Hello间隔"""
        if 'hello_interval' in info.data and v <= info.data['hello_interval']:
            raise ValueError("Dead间隔必须大于Hello间隔")
        return v
    
    @computed_field
    @property
    def is_backbone_area(self) -> bool:
        """是否为骨干区域"""
        return self.area_id == "0.0.0.0"
    
    @computed_field
    @property
    def dead_to_hello_ratio(self) -> float:
        """Dead间隔与Hello间隔的比值"""
        return self.dead_interval / self.hello_interval
