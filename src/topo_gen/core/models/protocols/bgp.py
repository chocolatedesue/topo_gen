"""BGP协议配置"""
from typing import Optional
from pydantic import Field, field_validator, computed_field

from ..base import BaseConfig
from ...types import ASNumber, RouterID


class BGPConfig(BaseConfig):
    """BGP配置"""
    
    # 基本配置
    as_number: ASNumber = Field(description="AS号")
    router_id: Optional[RouterID] = Field(default=None, description="路由器ID")
    enable_ipv6: bool = Field(default=True, description="启用IPv6")
    confederation_id: Optional[ASNumber] = Field(default=None, description="联邦ID")
    
    # 路由策略
    local_preference: int = Field(
        default=100, 
        ge=0, le=4294967295, 
        description="本地优先级"
    )
    med: Optional[int] = Field(
        default=None, 
        ge=0, le=4294967295, 
        description="多出口判别器"
    )
    
    # 计时器配置
    hold_time: int = Field(default=180, ge=3, le=65535, description="保持时间(秒)")
    keepalive_time: int = Field(default=60, ge=1, le=21845, description="保活时间(秒)")
    connect_retry_time: int = Field(default=120, ge=1, le=65535, description="连接重试时间(秒)")
    
    @field_validator('as_number')
    @classmethod
    def validate_as_number(cls, v: int) -> int:
        """验证AS号范围"""
        if not (1 <= v <= 4294967295):  # 32位AS号范围
            raise ValueError(f"AS号必须在1-4294967295范围内: {v}")
        return v
    
    @field_validator('keepalive_time')
    @classmethod
    def validate_keepalive_time(cls, v: int, info) -> int:
        """验证保活时间必须小于保持时间的1/3"""
        if 'hold_time' in info.data and v >= info.data['hold_time'] / 3:
            raise ValueError("保活时间必须小于保持时间的1/3")
        return v
    
    @computed_field
    @property
    def is_private_as(self) -> bool:
        """是否为私有AS号"""
        return (64512 <= self.as_number <= 65534) or (4200000000 <= self.as_number <= 4294967294)
    
    @computed_field
    @property
    def as_type(self) -> str:
        """AS类型"""
        if self.is_private_as:
            return "private"
        elif 1 <= self.as_number <= 64511:
            return "public_16bit"
        else:
            return "public_32bit"
