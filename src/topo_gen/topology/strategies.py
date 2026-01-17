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
    
    @staticmethod
    def calculate_area_id(coord: Coordinate, multi_area: bool, area_size: Optional[int]) -> str:
        """计算区域ID
        
        Args:
            coord: 节点坐标
            multi_area: 是否多区域
            area_size: 区域大小
            
        Returns:
            区域ID字符串 (e.g., "0.0.0.0" or "1.2.0.0")
        """
        if multi_area and area_size:
            area_row = coord.row // area_size
            area_col = coord.col // area_size
            return f"{area_row}.{area_col}.0.0"
        else:
            return "0.0.0.0"
    
    @staticmethod
    def calculate_as_number(
        coord: Coordinate, 
        topology_type: TopologyType,
        base_as: int,
        special_config=None
    ) -> int:
        """计算AS号
        
        Args:
            coord: 节点坐标
            topology_type: 拓扑类型
            base_as: 基础AS号
            special_config: 特殊拓扑配置（可选）
            
        Returns:
            AS号
        """
        if topology_type == TopologyType.SPECIAL and special_config:
            # Special拓扑的AS分配逻辑（基于dm6_6_sample）
            return TopologyStrategy._calculate_special_as_number(coord, base_as)
        else:
            # Grid/Torus拓扑使用统一AS
            return base_as
    
    @staticmethod
    def _calculate_special_as_number(coord: Coordinate, base_as: int) -> int:
        """获取Special拓扑的AS号
        
        域分割规则（基于 dm6_6_sample）：
        - 域1 (AS base+1): (0,0) 到 (2,2) - 左上角
        - 域2 (AS base+2): (0,3) 到 (2,5) - 右上角
        - 域3 (AS base+3): (3,0) 到 (5,2) - 左下角
        - 域4 (AS base+4): (3,3) 到 (5,5) - 右下角
        """
        row, col = coord.row, coord.col
        
        if 0 <= row <= 2 and 0 <= col <= 2:
            return base_as + 1  # 域1
        elif 0 <= row <= 2 and 3 <= col <= 5:
            return base_as + 2  # 域2
        elif 3 <= row <= 5 and 0 <= col <= 2:
            return base_as + 3  # 域3
        elif 3 <= row <= 5 and 3 <= col <= 5:
            return base_as + 4  # 域4
        else:
            return base_as  # 默认AS（不应该发生）
