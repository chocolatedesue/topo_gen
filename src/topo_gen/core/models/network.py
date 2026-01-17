"""网络配置模块"""
import ipaddress
from pydantic import Field, field_validator

from .base import BaseConfig


class NetworkConfig(BaseConfig):
    """网络配置"""
    
    ipv6_prefix: str = Field(default="2001:db8:1000::", description="IPv6前缀")
    loopback_prefix: str = Field(default="2001:db8:1000::", description="Loopback前缀")
    link_prefix: str = Field(default="2001:db8:2000::", description="链路前缀")
    subnet_mask: int = Field(default=127, ge=64, le=128, description="子网掩码长度")
    
    @field_validator('ipv6_prefix', 'loopback_prefix', 'link_prefix')
    @classmethod
    def validate_ipv6_prefix(cls, v: str) -> str:
        """验证IPv6前缀格式"""
        try:
            ipaddress.IPv6Network(f"{v}/64")
            return v
        except ValueError as e:
            raise ValueError(f"无效的IPv6前缀: {v}") from e
