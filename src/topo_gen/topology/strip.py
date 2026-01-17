"""
Strip拓扑实现
纵向环绕（环状），横向保持开放式连接
"""

from __future__ import annotations

from typing import Dict, List, Set
from functools import lru_cache

from ..core.types import Coordinate, Direction, NodeType, NeighborMap
from ..utils.functional import memoize
from .base import (
    BaseTopology, TopologyFactory, NeighborMapper, NodeTypeClassifier,
    get_neighbor_in_direction, get_torus_neighbor_in_direction
)


def _get_strip_neighbor(coord: Coordinate, direction: Direction, size: int) -> Coordinate | None:
    """条带拓扑的邻居计算：纵向环绕，横向开放。"""
    if direction in (Direction.NORTH, Direction.SOUTH):
        return get_torus_neighbor_in_direction(coord, direction, size)
    return get_neighbor_in_direction(coord, direction, size)


class StripTopology(BaseTopology):
    """条带拓扑（纵向环绕、横向直连）"""

    def __init__(self, topology_type):
        super().__init__(topology_type)

    @memoize
    def get_neighbors(self, coord: Coordinate, size: int) -> NeighborMap:
        """获取Strip拓扑的邻居节点"""
        return NeighborMapper.build_neighbor_map(coord, size, _get_strip_neighbor)

    def get_node_type(self, coord: Coordinate, size: int) -> NodeType:
        """获取节点类型"""
        return NodeTypeClassifier.classify_strip_node(coord, size)

    def calculate_total_links(self, size: int) -> int:
        """计算Strip拓扑的总链路数"""
        if size <= 0:
            return 0
        vertical_links = size * size  # 每一列形成一个环
        horizontal_links = size * max(0, size - 1)  # 每一行是开放式链路
        return vertical_links + horizontal_links

    @lru_cache(maxsize=128)
    def get_neighbor_count(self, coord: Coordinate, size: int) -> int:
        """获取邻居数量"""
        return len(self.get_neighbors(coord, size))

    def get_nodes_by_type(self, size: int) -> Dict[NodeType, Set[Coordinate]]:
        """按类型分组节点"""
        nodes_by_type = {
            NodeType.EDGE: set(),
            NodeType.INTERNAL: set(),
        }
        for row in range(size):
            for col in range(size):
                coord = Coordinate(row=row, col=col)
                node_type = self.get_node_type(coord, size)
                nodes_by_type.setdefault(node_type, set()).add(coord)
        return nodes_by_type

    def get_connectivity_stats(self, size: int) -> Dict[str, int]:
        """获取连通性统计信息"""
        total_nodes = size * size
        total_links = self.calculate_total_links(size)
        edge_nodes = 2 * size if size > 1 else size
        internal_nodes = max(0, total_nodes - edge_nodes)
        max_degree = 4 if size > 2 else 3
        min_degree = 3 if size > 1 else 0

        return {
            'total_nodes': total_nodes,
            'total_links': total_links,
            'corner_nodes': 0,
            'edge_nodes': edge_nodes,
            'internal_nodes': internal_nodes,
            'avg_degree': (total_links * 2) / total_nodes if total_nodes else 0,
            'max_degree': max_degree,
            'min_degree': min_degree,
        }

    def is_connected(self, size: int) -> bool:
        """条带拓扑在 size >= 1 时总是连通的"""
        return size >= 1

    def get_diameter(self, size: int) -> int:
        """获取网络直径"""
        if size <= 1:
            return 0
        vertical = size // 2
        horizontal = size - 1
        return vertical + horizontal

    def get_shortest_path_length(self, coord1: Coordinate, coord2: Coordinate, size: int) -> int:
        """计算两点之间的最短路径长度"""
        if coord1 == coord2:
            return 0

        vertical_diff = abs(coord1.row - coord2.row)
        vertical_distance = min(vertical_diff, size - vertical_diff)
        horizontal_distance = abs(coord1.col - coord2.col)
        return vertical_distance + horizontal_distance

    def validate_strip_properties(self, size: int) -> List[str]:
        """验证Strip拓扑基础属性"""
        errors: List[str] = []

        # 验证邻居数量
        for coord in self.get_all_coordinates(size):
            neighbor_count = len(self.get_neighbors(coord, size))
            expected = 4 if coord.col not in (0, size - 1) else 3
            if neighbor_count != expected:
                errors.append(f"节点{coord}的邻居数量应为{expected}，实际为{neighbor_count}")

        # 验证链路数量
        expected_links = self.calculate_total_links(size)
        actual_links = 0
        for coord in self.get_all_coordinates(size):
            actual_links += len(self.get_neighbors(coord, size))
        actual_links //= 2
        if actual_links != expected_links:
            errors.append(f"链路数量不匹配: 期望{expected_links}, 实际{actual_links}")

        if not self.is_connected(size):
            errors.append("拓扑不连通")

        return errors


# 注册Strip拓扑
TopologyFactory.register('strip', StripTopology)


def create_strip_topology() -> StripTopology:
    """创建Strip拓扑实例"""
    return StripTopology('strip')


def get_strip_neighbors(size: int):
    """获取Strip拓扑邻居函数"""
    topology = create_strip_topology()
    return lambda coord: topology.get_neighbors(coord, size)


def get_strip_node_type(size: int):
    """获取Strip拓扑节点类型函数"""
    topology = create_strip_topology()
    return lambda coord: topology.get_node_type(coord, size)


def calculate_strip_stats(size: int) -> Dict[str, int]:
    """计算Strip拓扑统计信息"""
    topology = create_strip_topology()
    return topology.get_connectivity_stats(size)


def validate_strip_topology(size: int) -> List[str]:
    """验证Strip拓扑属性"""
    topology = create_strip_topology()
    return topology.validate_strip_properties(size)
