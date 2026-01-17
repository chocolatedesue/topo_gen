"""BFD协议配置"""
from pydantic import Field, field_validator, computed_field

from ..base import BaseConfig
from ....config.defaults import (
    BFD_DEFAULT_ENABLED,
    BFD_DEFAULT_DETECT_MULTIPLIER,
    BFD_DEFAULT_INTERVAL_MS,
    BFD_DEFAULT_PROFILE_NAME,
    BFD_DEFAULT_ECHO_MODE,
    BFD_DEFAULT_ECHO_INTERVAL_MS,
    BFD_DEFAULT_PASSIVE_MODE,
    BFD_DEFAULT_MIN_TTL,
)


class BFDConfig(BaseConfig):
    """BFD配置"""
    
    # 基本配置
    enabled: bool = Field(default=BFD_DEFAULT_ENABLED, description="是否启用BFD")
    detect_multiplier: int = Field(default=BFD_DEFAULT_DETECT_MULTIPLIER, ge=1, le=255, description="检测倍数")
    receive_interval: int = Field(default=BFD_DEFAULT_INTERVAL_MS, ge=10, le=60000, description="接收间隔(毫秒)")
    transmit_interval: int = Field(default=BFD_DEFAULT_INTERVAL_MS, ge=10, le=60000, description="发送间隔(毫秒)")
    profile_name: str = Field(default=BFD_DEFAULT_PROFILE_NAME, description="配置文件名")
    
    # 高级配置
    echo_mode: bool = Field(default=BFD_DEFAULT_ECHO_MODE, description="是否启用回显模式")
    echo_interval: int = Field(default=BFD_DEFAULT_ECHO_INTERVAL_MS, ge=10, le=60000, description="回显间隔(毫秒)")
    passive_mode: bool = Field(default=BFD_DEFAULT_PASSIVE_MODE, description="是否为被动模式")
    minimum_ttl: int = Field(default=BFD_DEFAULT_MIN_TTL, ge=1, le=255, description="最小TTL值")
    
    @computed_field
    @property
    def detection_time_ms(self) -> int:
        """检测时间(毫秒)"""
        return self.receive_interval * self.detect_multiplier
    
    @computed_field
    @property
    def detection_time_seconds(self) -> float:
        """检测时间(秒)"""
        return self.detection_time_ms / 1000.0
    
    @field_validator('echo_interval')
    @classmethod
    def validate_echo_interval(cls, v: int, info) -> int:
        """验证回显间隔"""
        if 'receive_interval' in info.data and v > info.data['receive_interval']:
            raise ValueError("回显间隔不应大于接收间隔")
        return v
