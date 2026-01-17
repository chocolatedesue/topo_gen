"""统一的拓扑策略访问接口"""
from __future__ import annotations

from typing import Dict, Callable, Optional
from ..core.types import Coordinate, Direction, NodeType, TopologyType

# 导入现有的工厂函数
from .grid import get_grid_neighbors
from .torus import get_torus_neighbors  
from .strip import get_strip_neighbors
from .special import SpecialTopology


class TopologyStrategy:
    """拓扑策略统一接口 - 单一真实来源"""
    
    @staticmethod
    def get_neighbors_func(
        topology_type: TopologyType,
        size: int,
        special_config=None
    ) -> Callable[[Coordinate], Dict[Direction, Coordinate]]:
        """获取邻居计算函数
        
        Args:
            topology_type: 拓扑类型
            size: 网格大小
            special_config: 特殊拓扑配置（可选）
            
        Returns:
            接受坐标并返回邻居字典的函数
        """
        if topology_type == TopologyType.GRID:
            grid_neighbors = get_grid_neighbors(size)
            return lambda coord: grid_neighbors(coord)
        elif topology_type == TopologyType.TORUS:
            torus_neighbors = get_torus_neighbors(size)
            return lambda coord: torus_neighbors(coord)
        elif topology_type == TopologyType.STRIP:
            strip_neighbors = get_strip_neighbors(size)
            return lambda coord: strip_neighbors(coord)
        elif topology_type == TopologyType.SPECIAL and special_config:
            topo = SpecialTopology(TopologyType.SPECIAL)
            return lambda coord: topo.get_neighbors(coord, size, special_config)
        else:
            # 默认使用 Grid
            grid_neighbors = get_grid_neighbors(size)
            return lambda coord: grid_neighbors(coord)
    
    @staticmethod
    def get_node_type(
        coord: Coordinate,
        topology_type: TopologyType,
        size: int,
        special_config=None
    ) -> NodeType:
        """确定节点类型
        
        Args:
            coord: 节点坐标
            topology_type: 拓扑类型
            size: 网格大小
            special_config: 特殊拓扑配置（可选）
            
        Returns:
            节点类型
        """
        if topology_type == TopologyType.GRID:
            return TopologyStrategy._get_grid_node_type(coord, size)
        elif topology_type == TopologyType.STRIP:
            return TopologyStrategy._get_strip_node_type(coord, size)
        elif topology_type == TopologyType.TORUS:
            # Torus 中所有节点都是内部节点
            return NodeType.INTERNAL
        elif topology_type == TopologyType.SPECIAL and special_config:
            return TopologyStrategy._get_special_node_type(coord, special_config)
        else:
            return NodeType.INTERNAL
    
    @staticmethod
    def _get_grid_node_type(coord: Coordinate, size: int) -> NodeType:
        """获取 Grid 节点类型"""
        row, col = coord.row, coord.col
        
        # 角点
        if (row, col) in [(0, 0), (0, size-1), (size-1, 0), (size-1, size-1)]:
            return NodeType.CORNER
        # 边缘
        elif row == 0 or row == size-1 or col == 0 or col == size-1:
            return NodeType.EDGE
        # 内部
        else:
            return NodeType.INTERNAL
    
    @staticmethod
    def _get_strip_node_type(coord: Coordinate, size: int) -> NodeType:
        """获取 Strip 节点类型"""
        if coord.col == 0 or coord.col == size - 1:
            return NodeType.EDGE
        return NodeType.INTERNAL
    
    @staticmethod
    def _get_special_node_type(coord: Coordinate, special_config) -> NodeType:
        """获取 Special 拓扑的节点类型"""
        if coord == special_config.source_node:
            return NodeType.SOURCE
        elif coord == special_config.dest_node:
            return NodeType.DESTINATION
        elif coord in special_config.gateway_nodes:
            return NodeType.GATEWAY
        else:
            return NodeType.INTERNAL
