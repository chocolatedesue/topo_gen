"""
简化的拓扑生成引擎
使用anyio和简单的异步编程模式
"""

from __future__ import annotations

from typing import List
from pathlib import Path
import anyio

from .core.types import (
    Coordinate, Direction, NeighborMap, Failure, NodeType
)
from .core.models import (
    TopologyConfig, RouterInfo, SystemRequirements, GenerationResult,
    NetworkConfig
)
from .filesystem import (
    create_all_directories, create_all_template_files,
    generate_all_config_files, generate_clab_yaml
)
from .links import generate_interface_mappings, convert_links_to_clab_format, generate_loopback_ipv6
from .topology.special import filter_routers_for_special_topology
from .topology.strategies import TopologyStrategy
from .utils.topo import get_topology_type_str


class TopologyEngine:
    """拓扑生成引擎"""
    
    def __init__(self):
        self.network_config = NetworkConfig()
    
    async def generate_topology(self, config: TopologyConfig) -> GenerationResult:
        """生成完整拓扑"""
        try:
            # 1. 生成路由器信息
            routers = self._generate_routers(config)

            # 对于Special拓扑，只保留有连接的路由器
            topo_type = get_topology_type_str(config.topology_type)
            if topo_type == "special" and config.special_config:
                routers = filter_routers_for_special_topology(routers, config.special_config)
            
            # 2. 计算系统需求
            requirements = SystemRequirements.calculate_for_topology(config)
            
            # 3. 创建目录结构
            base_dir = self._get_output_dir(config)
            dir_result = await create_all_directories(config, routers, requirements)
            if isinstance(dir_result, Failure):
                return GenerationResult(
                    success=False,
                    message=f"目录创建失败: {dir_result.error}"
                )
            
            # 4. 创建模板文件
            template_result = await create_all_template_files(routers, requirements, base_dir, config)
            if isinstance(template_result, Failure):
                return GenerationResult(
                    success=False,
                    message=f"模板创建失败: {template_result.error}"
                )
            
            # 5. 生成接口地址映射 / 链路（避免重复计算）
            if config.no_links:
                links = []
                interface_mappings = {router.name: {} for router in routers}
            else:
                from .links import generate_all_links
                links = generate_all_links(config)
                interface_mappings = generate_interface_mappings(config, routers, links)
            
            # 6. 生成配置文件
            config_result = await generate_all_config_files(
                config, routers, interface_mappings, requirements, base_dir
            )
            if isinstance(config_result, Failure):
                return GenerationResult(
                    success=False,
                    message=f"配置生成失败: {config_result.error}"
                )
            
            # 7. 生成ContainerLab YAML
            if config.no_links:
                links_for_yaml = []
            else:
                links_for_yaml = convert_links_to_clab_format(config, routers, links, interface_mappings)
            yaml_result = await generate_clab_yaml(config, routers, links_for_yaml, base_dir)
            if isinstance(yaml_result, Failure):
                return GenerationResult(
                    success=False,
                    message=f"YAML生成失败: {yaml_result.error}"
                )
            
            return GenerationResult(
                success=True,
                message="拓扑生成成功",
                output_dir=base_dir,
                stats={
                    "total_routers": len(routers),
                    "total_links": len(links_for_yaml),
                    "topology_type": get_topology_type_str(config.topology_type),
                    "size": config.size
                }
            )
            
        except Exception as e:
            return GenerationResult(
                success=False,
                message=f"生成失败: {str(e)}",
                error_details=str(e)
            )
    
    def _generate_routers(self, config: TopologyConfig) -> List[RouterInfo]:
        """生成路由器信息"""
        routers = []

        neighbors_func = None
        if not config.no_links:
            neighbors_func = TopologyStrategy.get_neighbors_func(
                config.topology_type,
                config.size,
                config.special_config
            )
        
        for row in range(config.size):
            for col in range(config.size):
                coord = Coordinate(row, col)
                router = self._create_router_info(coord, config, neighbors_func)
                routers.append(router)
        
        return routers
    
    def _create_router_info(
        self,
        coord: Coordinate,
        config: TopologyConfig,
        neighbors_func=None
    ) -> RouterInfo:
        """创建单个路由器信息"""
        router_name = f"router_{coord.row:02d}_{coord.col:02d}"
        router_id = f"10.{coord.row}.{coord.col}.1"

        # 计算区域ID
        area_id = self._calculate_area_id(coord, config)
        area_id_int = int(area_id.split('.')[0]) if area_id != "0.0.0.0" else 0

        loopback_ipv6 = generate_loopback_ipv6(area_id_int, coord)
        
        # 确定节点类型
        node_type = self._get_node_type(coord, config)
        
        # 获取邻居信息
        if config.no_links:
            neighbors = {}
        else:
            if neighbors_func is None:
                neighbors = self._get_neighbors(coord, config)
            else:
                neighbors = neighbors_func(coord)
        
        # 确定AS号（如果启用BGP）
        as_number = None
        if config.enable_bgp and config.bgp_config:
            as_number = self._calculate_as_number(coord, config)
        
        return RouterInfo(
            name=router_name,
            coordinate=coord,
            node_type=node_type,
            router_id=router_id,
            loopback_ipv6=loopback_ipv6,
            interfaces={},  # 稍后填充
            neighbors=neighbors,
            area_id=area_id,
            as_number=as_number
        )
    
    def _get_node_type(self, coord: Coordinate, config: TopologyConfig) -> NodeType:
        """获取节点类型 - 使用统一策略接口"""
        return TopologyStrategy.get_node_type(
            coord,
            config.topology_type,
            config.size,
            config.special_config
        )
    
    def _get_neighbors(self, coord: Coordinate, config: TopologyConfig) -> NeighborMap:
        """获取邻居节点 - 使用统一策略接口"""
        neighbors_func = TopologyStrategy.get_neighbors_func(
            config.topology_type,
            config.size,
            config.special_config
        )
        return neighbors_func(coord)
    
    
    def _calculate_area_id(self, coord: Coordinate, config: TopologyConfig) -> str:
        """计算区域ID - 使用统一策略"""
        return TopologyStrategy.calculate_area_id(coord, config.multi_area, config.area_size)
    

    
    
    def _calculate_as_number(self, coord: Coordinate, config: TopologyConfig) -> int:
        """计算AS号 - 使用统一策略"""
        return TopologyStrategy.calculate_as_number(
            coord,
            config.topology_type,
            config.bgp_config.as_number,
            config.special_config
        )

    def _get_protocol_suffix(self, config: TopologyConfig) -> str:
        """获取协议后缀标识"""
        protocols = []
        
        # 检查启用的路由协议
        if config.ospf_config is not None:
            protocols.append("ospf6")
        if config.enable_isis:
            protocols.append("isis")
        
        # 如果没有启用任何路由协议，默认返回ospf6（向后兼容）
        if not protocols:
            protocols.append("ospf6")
        
        return "_".join(protocols)

    def _get_output_dir(self, config: TopologyConfig) -> Path:
        """获取输出目录（优先使用配置中的 output_dir）"""
        if getattr(config, "output_dir", None):
            return Path(str(config.output_dir))
        topo_type = get_topology_type_str(config.topology_type)
        protocol_suffix = self._get_protocol_suffix(config)
        
        # 添加 LSA-only 后缀
        lsa_only_suffix = ""
        if config.ospf_config and config.ospf_config.lsa_only_mode:
            lsa_only_suffix = "_lsa_only"
        
        return Path(f"{protocol_suffix}_{topo_type}{config.size}x{config.size}{lsa_only_suffix}")


# 便利函数
async def generate_topology(config: TopologyConfig) -> GenerationResult:
    """生成拓扑的便利函数"""
    engine = TopologyEngine()
    return await engine.generate_topology(config)
