"""ISIS协议配置"""
from typing import Optional
from pydantic import Field, field_validator, computed_field

from ..base import BaseConfig
from ....config.defaults import (
    ISIS_DEFAULT_AREA_ID,
    ISIS_DEFAULT_LEVEL_TYPE,
    ISIS_DEFAULT_METRIC_STYLE,
    ISIS_DEFAULT_HELLO_INTERVAL,
    ISIS_DEFAULT_HELLO_MULTIPLIER,
    ISIS_DEFAULT_PRIORITY,
    ISIS_DEFAULT_LSP_GEN_INTERVAL,
    ISIS_DEFAULT_LSP_REFRESH_INTERVAL,
    ISIS_DEFAULT_MAX_LSP_LIFETIME,
    ISIS_DEFAULT_SPF_INTERVAL,
    ISIS_DEFAULT_SPF_INIT_DELAY_MS,
    ISIS_DEFAULT_SPF_SHORT_DELAY_MS,
    ISIS_DEFAULT_SPF_LONG_DELAY_MS,
    ISIS_DEFAULT_SPF_HOLDDOWN_MS,
    ISIS_DEFAULT_SPF_TIME_TO_LEARN_MS,
    ISIS_DEFAULT_CSNP_INTERVAL,
    ISIS_DEFAULT_PSNP_INTERVAL,
    ISIS_DEFAULT_METRIC,
    ISIS_DEFAULT_VERTICAL_METRIC,
    ISIS_DEFAULT_HORIZONTAL_METRIC,
    ISIS_DEFAULT_THREE_WAY_HANDSHAKE,
    ISIS_DEFAULT_ENABLE_WIDE_METRICS,
)


class ISISConfig(BaseConfig):
    """ISIS配置 - 支持仅IPv6单实例快速收敛网格拓扑"""
    
    # 基本标识
    net_address: str = Field(description="NET地址，格式: 49.AREA.SYSID.00")
    area_id: str = Field(default=ISIS_DEFAULT_AREA_ID, description="Area ID")
    system_id: Optional[str] = Field(default=None, description="System ID，如果为None则自动生成")
    level_type: str = Field(default=ISIS_DEFAULT_LEVEL_TYPE, description="ISIS级别类型")
    metric_style: str = Field(default=ISIS_DEFAULT_METRIC_STYLE, description="度量样式")
    
    # 基础计时器参数
    hello_interval: int = Field(default=ISIS_DEFAULT_HELLO_INTERVAL, ge=1, le=600, description="Hello间隔(秒)")
    hello_multiplier: int = Field(default=ISIS_DEFAULT_HELLO_MULTIPLIER, ge=2, le=100, description="Hello倍数器")
    priority: int = Field(default=ISIS_DEFAULT_PRIORITY, ge=0, le=127, description="DIS选举优先级")
    
    # LSP生成和刷新优化
    lsp_gen_interval: int = Field(default=ISIS_DEFAULT_LSP_GEN_INTERVAL, ge=1, le=120, description="LSP生成间隔(秒)")
    lsp_refresh_interval: int = Field(default=ISIS_DEFAULT_LSP_REFRESH_INTERVAL, ge=1, le=65534, description="LSP刷新间隔(秒)")
    max_lsp_lifetime: int = Field(default=ISIS_DEFAULT_MAX_LSP_LIFETIME, ge=350, le=65535, description="LSP最大生存时间(秒)")
    
    # SPF计算优化
    spf_interval: int = Field(default=ISIS_DEFAULT_SPF_INTERVAL, ge=1, le=120, description="SPF计算间隔(秒)")
    spf_init_delay_ms: int = Field(default=ISIS_DEFAULT_SPF_INIT_DELAY_MS, ge=0, le=60000, description="SPF IETF 初始延迟(毫秒)")
    spf_short_delay_ms: int = Field(default=ISIS_DEFAULT_SPF_SHORT_DELAY_MS, ge=0, le=60000, description="SPF IETF 短延迟(毫秒)")
    spf_long_delay_ms: int = Field(default=ISIS_DEFAULT_SPF_LONG_DELAY_MS, ge=0, le=60000, description="SPF IETF 长延迟(毫秒)")
    spf_holddown_ms: int = Field(default=ISIS_DEFAULT_SPF_HOLDDOWN_MS, ge=0, le=60000, description="SPF IETF 抑制(毫秒)")
    spf_time_to_learn_ms: int = Field(default=ISIS_DEFAULT_SPF_TIME_TO_LEARN_MS, ge=0, le=60000, description="SPF IETF 学习时间(毫秒)")
    
    # CSNP/PSNP间隔
    csnp_interval: int = Field(default=ISIS_DEFAULT_CSNP_INTERVAL, ge=1, le=600, description="CSNP间隔(秒)")
    psnp_interval: int = Field(default=ISIS_DEFAULT_PSNP_INTERVAL, ge=1, le=120, description="PSNP间隔(秒)")
    
    # 接口度量
    isis_metric: int = Field(default=ISIS_DEFAULT_METRIC, ge=1, le=16777215, description="ISIS接口度量值")
    isis_vertical_metric: int = Field(default=ISIS_DEFAULT_VERTICAL_METRIC, ge=1, le=16777215, description="ISIS纵向度量值")
    isis_horizontal_metric: int = Field(default=ISIS_DEFAULT_HORIZONTAL_METRIC, ge=1, le=16777215, description="ISIS横向度量值")
    
    # 网格拓扑特性开关
    three_way_handshake: bool = Field(default=ISIS_DEFAULT_THREE_WAY_HANDSHAKE, description="启用三路握手")
    enable_wide_metrics: bool = Field(default=ISIS_DEFAULT_ENABLE_WIDE_METRICS, description="启用wide度量模式")
    
    @computed_field
    @property
    def dead_interval(self) -> int:
        """计算Dead间隔 = hello_interval * hello_multiplier"""
        return self.hello_interval * self.hello_multiplier
    
    @field_validator('level_type')
    @classmethod
    def validate_level_type(cls, v: str) -> str:
        """验证ISIS级别类型"""
        valid_types = {"level-1", "level-2", "level-1-2"}
        if v not in valid_types:
            raise ValueError(f"无效的ISIS级别类型: {v}。支持的类型: {', '.join(valid_types)}")
        return v
    
    @field_validator('metric_style')
    @classmethod
    def validate_metric_style(cls, v: str) -> str:
        """验证度量样式"""
        valid_styles = {"narrow", "wide", "transition"}
        if v not in valid_styles:
            raise ValueError(f"无效的度量样式: {v}。支持的样式: {', '.join(valid_styles)}")
        return v
    
    @field_validator('net_address')
    @classmethod
    def validate_net_address(cls, v: str) -> str:
        """验证NET地址格式"""
        parts = v.split('.')
        if len(parts) < 3:
            raise ValueError(f"无效的NET地址格式: {v}。应为Area.SystemID.SEL格式")
        return v
    
    @field_validator('lsp_refresh_interval')
    @classmethod
    def validate_lsp_refresh_interval(cls, v: int, info) -> int:
        """验证LSP刷新间隔必须小于最大生存时间"""
        if hasattr(info, 'data') and 'max_lsp_lifetime' in info.data and v >= info.data['max_lsp_lifetime']:
            raise ValueError("LSP刷新间隔必须小于最大生存时间")
        return v
    
    @computed_field
    @property
    def is_optimized_for_convergence(self) -> bool:
        """是否为收敛优化配置"""
        return (self.hello_interval <= 2 and 
                self.hello_multiplier <= 4 and
                self.lsp_gen_interval <= 2 and
                self.spf_interval <= 2)
