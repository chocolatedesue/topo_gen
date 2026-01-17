"""路由器和链路信息模块"""
from typing import Dict, Optional
from pydantic import Field, computed_field
from pydantic.networks import IPv6Address

from .base import BaseConfig
from ..types import (
    Coordinate, Direction, NodeType, RouterName, InterfaceName,
    RouterID, NeighborMap, AreaID, IPv6AddressHelper, ASNumber,
    LinkAddress
)
from pydantic.networks import IPv6Network


class RouterInfo(BaseConfig):
    """路由器信息"""
    
    name: RouterName = Field(description="路由器名称")
    coordinate: Coordinate = Field(description="坐标位置")
    node_type: NodeType = Field(description="节点类型")
    router_id: RouterID = Field(description="路由器ID")
    loopback_ipv6: IPv6Address = Field(description="Loopback IPv6地址")
    interfaces: Dict[InterfaceName, IPv6Address] = Field(default_factory=dict, description="接口地址映射")
    neighbors: Dict[Direction, Coordinate] = Field(default_factory=dict, description="邻居映射")
    area_id: AreaID = Field(default="0.0.0.0", description="OSPF区域ID")
    as_number: Optional[ASNumber] = Field(default=None, description="BGP AS号")
    
    # 可选字段
    management_ip: Optional[IPv6Address] = Field(default=None, description="管理IP地址")
    description: Optional[str] = Field(default=None, max_length=255, description="路由器描述")
    vendor: Optional[str] = Field(default="generic", description="设备厂商")
    model: Optional[str] = Field(default="router", description="设备型号")
    
    @computed_field
    @property
    def neighbor_count(self) -> int:
        """邻居数量"""
        return len(self.neighbors)
    
    @computed_field
    @property
    def interface_count(self) -> int:
        """接口数量"""
        return len(self.interfaces)
    
    @computed_field
    @property
    def neighbor_map(self) -> NeighborMap:
        """获取邻居映射对象"""
        return NeighborMap.from_dict(self.neighbors)
    
    @computed_field
    @property
    def loopback_helper(self) -> IPv6AddressHelper:
        """Loopback地址助手"""
        return IPv6AddressHelper.from_string(self.loopback_ipv6)
    
    @computed_field
    @property
    def is_border_router(self) -> bool:
        """是否为边界路由器"""
        return self.node_type in {NodeType.CORNER, NodeType.EDGE, NodeType.GATEWAY}
    
    @computed_field
    @property
    def is_special_node(self) -> bool:
        """是否为特殊节点"""
        return self.node_type.is_special
    
    def get_interface_for_direction(self, direction: Direction) -> Optional[str]:
        """获取指定方向的接口地址"""
        from ..types import get_interface_for_direction
        interface_name = get_interface_for_direction(direction)
        return self.interfaces.get(interface_name)
    
    def has_neighbor_in_direction(self, direction: Direction) -> bool:
        """检查指定方向是否有邻居"""
        return direction in self.neighbors
    
    def get_neighbor_coordinate(self, direction: Direction) -> Optional[Coordinate]:
        """获取指定方向的邻居坐标"""
        return self.neighbors.get(direction)


class LinkInfo(BaseConfig):
    """链路信息"""
    
    router1_name: RouterName = Field(description="路由器1名称")
    router2_name: RouterName = Field(description="路由器2名称")
    router1_coord: Coordinate = Field(description="路由器1坐标")
    router2_coord: Coordinate = Field(description="路由器2坐标")
    router1_interface: InterfaceName = Field(description="路由器1接口")
    router2_interface: InterfaceName = Field(description="路由器2接口")
    router1_ipv6: IPv6Address = Field(description="路由器1 IPv6地址")
    router2_ipv6: IPv6Address = Field(description="路由器2 IPv6地址")
    network: IPv6Network = Field(description="网络地址")
    
    # 可选字段
    bandwidth: Optional[int] = Field(default=None, ge=1, description="带宽(Mbps)")
    delay: Optional[int] = Field(default=None, ge=0, description="延迟(微秒)")
    cost: Optional[int] = Field(default=None, ge=1, le=65535, description="链路开销")
    description: Optional[str] = Field(default=None, max_length=255, description="链路描述")
    
    @computed_field
    @property
    def link_id(self) -> str:
        """链路唯一标识"""
        coords = sorted([self.router1_coord, self.router2_coord], key=lambda c: (c.row, c.col))
        return f"{coords[0]}_{coords[1]}"
    
    @computed_field
    @property
    def link_address(self) -> LinkAddress:
        """获取链路地址对象"""
        return LinkAddress(
            network=self.network,
            router1_addr=self.router1_ipv6,
            router2_addr=self.router2_ipv6,
            router1_name=self.router1_name,
            router2_name=self.router2_name
        )
    
    @computed_field
    @property
    def is_horizontal(self) -> bool:
        """是否为水平链路"""
        return self.router1_coord.row == self.router2_coord.row
    
    @computed_field
    @property
    def is_vertical(self) -> bool:
        """是否为垂直链路"""
        return self.router1_coord.col == self.router2_coord.col
    
    @computed_field
    @property
    def manhattan_distance(self) -> int:
        """曼哈顿距离"""
        return self.router1_coord.manhattan_distance_to(self.router2_coord)
    
    @computed_field
    @property
    def is_adjacent(self) -> bool:
        """是否为相邻链路"""
        return self.manhattan_distance == 1
    
    def get_peer_info(self, router_name: str) -> tuple[str, str, Coordinate]:
        """获取对端路由器信息"""
        if router_name == self.router1_name:
            return self.router2_name, self.router2_ipv6, self.router2_coord
        elif router_name == self.router2_name:
            return self.router1_name, self.router1_ipv6, self.router1_coord
        else:
            raise ValueError(f"路由器 {router_name} 不在此链路上")
