from __future__ import annotations

from typing import Any

from ..core.models import TopologyConfig
from ..core.types import TopologyType


def get_topology_type_str(topology_type: Any) -> str:
    """Return normalized topology type as lowercase string.
    Accepts enum-like objects (with .value) or plain strings.
    """
    if hasattr(topology_type, "value"):
        return str(topology_type.value)
    return str(topology_type).lower()


def get_topology_dimensions(config: TopologyConfig) -> tuple[int, int]:
    """获取拓扑有效行列数（Torus支持矩形，其余为方形）"""
    if (
        config.topology_type == TopologyType.TORUS
        and config.rows is not None
        and config.cols is not None
    ):
        return config.rows, config.cols
    return config.size, config.size


def get_topology_size_label(config: TopologyConfig) -> str:
    """获取拓扑尺寸标签，如 5x7 或 4x4"""
    rows, cols = get_topology_dimensions(config)
    return f"{rows}x{cols}"
