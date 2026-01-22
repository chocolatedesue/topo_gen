from __future__ import annotations

from pathlib import Path
from typing import Optional, Set

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .defaults import (
    BGP_DEFAULT_ASN,
    CONTAINER_DEFAULT_CPU_LIMIT,
    CONTAINER_DEFAULT_CPU_SET,
    CONTAINER_DEFAULT_MEMORY_LIMIT,
    DISABLE_LOGGING_DEFAULT,
    SKIP_LOG_FILES_DEFAULT,
    ZIP_OUTPUT_DEFAULT,
    ENABLE_DEFAULT_BFD,
    ENABLE_DEFAULT_BGP,
    ENABLE_DEFAULT_ISIS,
    ENABLE_DEFAULT_OSPF6,
    MGMT_DEFAULT_EXTERNAL_ACCESS,  # 自动添加
    OSPF_DEFAULT_DEAD_INTERVAL,
    OSPF_DEFAULT_HELLO_INTERVAL,
    OSPF_DEFAULT_LSA_MIN_ARRIVAL_MS,
    OSPF_DEFAULT_MAXIMUM_PATHS,
    OSPF_DEFAULT_SPF_DELAY_MS,
)
from ..core.types import TopologyType


class MgmtSettings(BaseSettings):
    """管理平面设置"""

    external_access: bool = Field(
        default=MGMT_DEFAULT_EXTERNAL_ACCESS, description="允许外部访问（将修改 iptables)"
    )


class AppSettings(BaseSettings):
    """全局应用设置（可由环境变量/配置文件覆盖）"""

    model_config = SettingsConfigDict(
        env_prefix="TOPO_",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 全局
    verbose: bool = Field(default=False, description="详细日志输出")
    dry_run: bool = Field(default=False, description="仅验证不生成")
    output_dir: Optional[Path] = Field(default=None, description="输出目录")

    # 通用拓扑参数
    size: int = Field(default=6, ge=2, le=100, description="网格大小")
    rows: Optional[int] = Field(default=None, ge=2, le=100, description="Torus行数(可选)")
    cols: Optional[int] = Field(default=None, ge=2, le=100, description="Torus列数(可选)")
    topology: TopologyType = Field(default=TopologyType.TORUS, description="拓扑类型")
    multi_area: bool = Field(default=False)
    area_size: Optional[int] = Field(default=None, ge=2)

    # 管理平面
    mgmt: MgmtSettings = Field(default_factory=MgmtSettings)

    # 协议启用
    enable_bgp: bool = Field(default=ENABLE_DEFAULT_BGP)
    enable_bfd: bool = Field(default=ENABLE_DEFAULT_BFD)
    enable_ospf6: bool = Field(default=ENABLE_DEFAULT_OSPF6)
    enable_isis: bool = Field(default=ENABLE_DEFAULT_ISIS)

    # OSPF 参数
    hello_interval: int = Field(default=OSPF_DEFAULT_HELLO_INTERVAL)
    dead_interval: int = Field(default=OSPF_DEFAULT_DEAD_INTERVAL)
    # 与 CLI 选项默认保持一致
    spf_delay: int = Field(default=OSPF_DEFAULT_SPF_DELAY_MS)
    lsa_min_arrival: int = Field(default=OSPF_DEFAULT_LSA_MIN_ARRIVAL_MS)
    maximum_paths: int = Field(default=OSPF_DEFAULT_MAXIMUM_PATHS)
    lsa_only_mode: bool = Field(default=False)

    # BGP 参数
    bgp_as: int = Field(default=BGP_DEFAULT_ASN)

    # 守护进程控制
    daemons_off: bool = Field(default=False)
    bgpd_off: bool = Field(default=False)
    ospf6d_off: bool = Field(default=False)
    isisd_off: bool = Field(default=False)
    bfdd_off: bool = Field(default=False)
    dummy_gen_protocols: Set[str] = Field(default_factory=set)
    no_config_protocols: Set[str] = Field(default_factory=set)
    disable_logging: bool = Field(default=DISABLE_LOGGING_DEFAULT)
    skip_log_files: bool = Field(default=SKIP_LOG_FILES_DEFAULT)
    zip_output: bool = Field(default=ZIP_OUTPUT_DEFAULT)

    # Container resource limits
    cpu_limit: float = Field(default=CONTAINER_DEFAULT_CPU_LIMIT, description="CPU limit per container")
    memory_limit: str = Field(default=CONTAINER_DEFAULT_MEMORY_LIMIT, description="Memory limit per container")
    cpu_set: str = Field(default=CONTAINER_DEFAULT_CPU_SET, description="CPU affinity (auto means 0-{cpus-2})")

    # 配置文件（若 CLI 未提供，可通过环境变量或 .env 中指向）
    config_file: Optional[Path] = Field(default=None, description="配置文件路径，可选")


__all__ = ["AppSettings"]
