"""
简化的文件系统操作模块
使用anyio进行异步文件操作，不依赖复杂的第三方库
"""

from __future__ import annotations

from typing import Dict, List, Tuple
from pathlib import Path
import anyio
from anyio import Path as AsyncPath
import stat
import os

from .core.types import RouterName, Success, Failure, Result
from .core.models import TopologyConfig, RouterInfo, SystemRequirements
from .generators.config import ConfigGeneratorFactory
from .generators.templates import generate_all_templates
from .utils.topo import get_topology_type_str

def get_protocol_suffix(config: TopologyConfig) -> str:
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


class FileSystemManager:
    """文件系统管理器"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
    
    async def create_directory_structure(self, routers: List[RouterInfo]) -> Result:
        """创建目录结构"""
        try:
            # 创建基础目录
            await self._create_base_directories()
            
            # 为每个路由器创建目录
            for router in routers:
                await self._create_router_directories(router)
            
            return Success(f"成功创建 {len(routers)} 个路由器目录")
            
        except Exception as e:
            return Failure(f"目录创建失败: {str(e)}")
    
    async def _create_base_directories(self):
        """创建基础目录"""
        base_path = AsyncPath(self.base_dir)
        await base_path.mkdir(parents=True, exist_ok=True)
        
        etc_path = base_path / "etc"
        await etc_path.mkdir(exist_ok=True)
        
        configs_path = base_path / "configs"
        await configs_path.mkdir(exist_ok=True)
    
    async def _create_router_directories(self, router: RouterInfo):
        """为单个路由器创建目录"""
        router_path = AsyncPath(self.base_dir) / "etc" / router.name
        await router_path.mkdir(parents=True, exist_ok=True)
        
        # 创建配置目录
        conf_path = router_path / "conf"
        await conf_path.mkdir(exist_ok=True)
        
        # 创建日志目录
        log_path = router_path / "log"
        await log_path.mkdir(exist_ok=True)
        
        # 创建日志文件
        log_files = ["zebra.log", "ospf6d.log", "bgpd.log", "bfdd.log", "staticd.log", "route.json", "isisd.log"]
        for log_file in log_files:
            log_file_path = log_path / log_file
            await log_file_path.touch()
            # 设置权限为777
            import os
            await anyio.to_thread.run_sync(
                os.chmod, str(log_file_path), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO
            )
    
    async def write_template_files(self, routers: List[RouterInfo], config: TopologyConfig = None) -> Result:
        """写入模板文件"""
        try:
            for router in routers:
                await self._write_router_templates(router, config)

            return Success(f"成功写入 {len(routers)} 个路由器的模板文件")

        except Exception as e:
            return Failure(f"模板文件写入失败: {str(e)}")

    async def _write_router_templates(self, router: RouterInfo, config: TopologyConfig = None):
        """为单个路由器写入模板文件"""
        templates = generate_all_templates(router, config)
        conf_path = AsyncPath(self.base_dir) / "etc" / router.name / "conf"

        for template_name, content in templates.items():
            file_path = conf_path / template_name
            async with await file_path.open('w') as f:
                await f.write(content)
    
    async def write_config_files(
        self, 
        routers: List[RouterInfo], 
        config: TopologyConfig,
        interface_mappings: Dict[RouterName, Dict[str, str]]
    ) -> Result:
        """写入配置文件"""
        try:
            config_types = ["daemons", "zebra.conf"]

            if config.ospf_config is not None:
                config_types.append("ospf6d.conf")

            if config.enable_isis:
                config_types.append("isisd.conf")

            if config.enable_bgp:
                config_types.append("bgpd.conf")

            if config.enable_bfd:
                config_types.append("bfdd.conf")
            
            for router in routers:
                await self._write_router_configs(router, config, config_types, interface_mappings)
            
            return Success(f"成功写入 {len(routers)} 个路由器的配置文件")
            
        except Exception as e:
            return Failure(f"配置文件写入失败: {str(e)}")
    
    async def _write_router_configs(
        self, 
        router: RouterInfo, 
        config: TopologyConfig,
        config_types: List[str],
        interface_mappings: Dict[RouterName, Dict[str, str]]
    ):
        """为单个路由器写入配置文件"""
        conf_path = AsyncPath(self.base_dir) / "etc" / router.name / "conf"
        
        # 更新路由器接口信息
        if router.name in interface_mappings:
            router.interfaces.update(interface_mappings[router.name])
        
        # 在写入前，清理与当前启用协议不一致的旧配置文件
        # 仅处理我们生成的协议配置文件，避免误删其他文件
        stale_candidates = {"ospf6d.conf", "isisd.conf", "bgpd.conf", "bfdd.conf"}
        allowed_now = set(config_types)
        for fname in stale_candidates:
            if fname not in allowed_now:
                file_path = conf_path / fname
                try:
                    if await file_path.exists():
                        await file_path.unlink()
                except Exception:
                    # 清理失败不影响后续写入
                    pass

        for config_type in config_types:
            generator = ConfigGeneratorFactory.create(config_type)
            content = generator.generate(router, config)

            # 处理 dummy 生成：如果配置的协议在 dummy 集合中，则将真实内容写到 -bak.conf，并生成空主配置
            protocol_name = config_type  # e.g., "ospf6d.conf"
            base_protocol = protocol_name.split('.')[0]
            is_dummy = False
            is_no_config = False
            if hasattr(config, 'dummy_gen_protocols') and isinstance(config.dummy_gen_protocols, set):
                # 支持传入如 'ospf6d', 'bgpd', 'bfdd'
                if base_protocol in config.dummy_gen_protocols:
                    is_dummy = True
            if hasattr(config, 'no_config_protocols') and isinstance(config.no_config_protocols, set):
                if base_protocol in config.no_config_protocols:
                    is_no_config = True

            if is_no_config:
                # 清理可能存在的 dummy 备份
                bak_path = conf_path / f"{base_protocol}-bak.conf"
                try:
                    if await bak_path.exists():
                        await bak_path.unlink()
                except Exception:
                    pass
                file_path = conf_path / protocol_name
                async with await file_path.open('w') as f:
                    await f.write("")
                continue

            if content:
                if is_dummy:
                    # 写入备份配置
                    bak_path = conf_path / f"{protocol_name.replace('.conf', '')}-bak.conf"
                    async with await bak_path.open('w') as f:
                        await f.write(content)
                    # 写入空主配置
                    file_path = conf_path / protocol_name
                    async with await file_path.open('w') as f:
                        await f.write("")
                else:
                    file_path = conf_path / config_type
                    async with await file_path.open('w') as f:
                        await f.write(content)
    
    async def write_containerlab_yaml(
        self, 
        config: TopologyConfig,
        routers: List[RouterInfo],
        links: List[Tuple[str, str, str, str]]  # (router1, intf1, router2, intf2)
    ) -> Result:
        """写入ContainerLab YAML配置"""
        try:
            yaml_content = self._generate_containerlab_yaml(config, routers, links)
            
            # 确定文件名
            topo_type = get_topology_type_str(config.topology_type)
            protocol_suffix = get_protocol_suffix(config)
            yaml_filename = f"{protocol_suffix}_{topo_type}{config.size}x{config.size}.clab.yaml"
            
            yaml_path = AsyncPath(self.base_dir) / yaml_filename
            async with await yaml_path.open('w') as f:
                await f.write(yaml_content)
            
            return Success(f"成功生成ContainerLab配置: {yaml_filename}")
            
        except Exception as e:
            return Failure(f"ContainerLab YAML生成失败: {str(e)}")
    
    def _generate_containerlab_yaml(
        self,
        config: TopologyConfig,
        routers: List[RouterInfo],
        links: List[Tuple[str, str, str, str]]
    ) -> str:
        """生成ContainerLab YAML内容"""
        import yaml

        # 确定拓扑类型名称
        topo_type_str = get_topology_type_str(config.topology_type)
        if topo_type_str == "special" and config.special_config:
            base_name = get_topology_type_str(config.special_config.base_topology)
            if config.special_config.include_base_connections:
                topo_suffix = f"{base_name}_special"
            else:
                topo_suffix = "pure_special"
        else:
            topo_suffix = topo_type_str

        # 生成节点配置
        nodes = {}
        for router in routers:
            node_def = {
                "kind": "linux",
                # "image": "docker.cnb.cool/jmncnic/frrbgpls/origin:latest",
                # "image": "quay.io/frrouting/frr:10.3.1",
                "image" : "docker.cnb.cool/jmncnic/frrbgpls/origin",
                "binds": [
                    f"etc/{router.name}/conf:/etc/frr",
                    f"etc/{router.name}/log:/var/log/frr",
                ]
            }
            if not config.podman:
                node_def["network-mode"] = "none"
            nodes[router.name] = node_def

        # 生成链路配置
        clab_links = []
        for router1, intf1, router2, intf2 in links:
            # 使用标准的 veth pair 并添加延迟
            # 注意: containerlab 允许在 endpoints 定义中直接指定 latency 等参数，或者使用 kind: linux 节点的 tc 功能
            # 更简单的方式是使用 link 的属性
            link_def = {
                "endpoints": [f"{router1}:{intf1}", f"{router2}:{intf2}"]
            }
            # 如果配置了延迟，应用到链路
            if config.link_delay and config.link_delay != "0ms":
                 # Containerlab 支持在链路定义中使用 'vars' 或者直接在 interfaces 上配置 tc (但这里是 link level definition)
                 # 正确的方式通常取决于 containerlab 版本和运行时。
                 # 标准方式：在 link 定义中无法直接加 latency。
                 # 但可以通过 endpoint 扩展属性: endpoint:interface:latency (不支持)
                 # 另一种方式：kind: cvx 支持，但 linux bridge/veth 默认不支持直接写 latency。
                 # 必须使用 'tc' 流量控制。Containerlab 为每个链路端点自动创建 tc qdisc 吗？不。
                 # 
                 # 修正：Containerlab 目前原生不支持在 simple link array 中直接定义 latency。
                 # 需要使用 tc 镜像或手动 tc 命令，或者在节点定义中添加 exec 命令。
                 # 
                 # 为了简起见，我们将在节点启动后的 exec 中不方便添加。
                 # 
                 # 更好的方法：Containerlab 确实支持 endpoint attributes 吗？
                 # 文档显示：
                 # links:
                 #   - endpoints: ["node1:eth1", "node2:eth1"]
                 #     latency: 10ms  <-- 这是一个受支持的特性吗？这不是核心 link schema。
                 #
                 # 验证：Containerlab 实验性功能或某些 kind 支持。
                 # 
                 # 对于 linux kind，最稳妥的方法是生成 startup-config script 或 exec。
                 # 
                 # 但等等，我们可以使用 containerlab 的 'exec' 列表在拓扑文件中。
                 # 
                 # 让我们尝试一种更通用的方法：
                 # 为每个容器生成一个 startup script，调用 tc。
                 # 
                 # 实际上，containerlab 确实在早期版本讨论过链路属性。
                 # Modern approach: 使用 kind: linux，可以执行命令。
                 # 
                 # 让我们先保持简单：我们不修改 schema 除非确定 clab 支持。
                 # 经确认，clab 目前并不直接在 links 列表支持 'latency' 字段用于 veth。
                 # 
                 # 替代方案：在 deploy 后运行脚本。这在生成器中比较难办。
                 # 
                 # 再次确认：Containerlab 文档 "Link Impairments"。
                 # 目前大多通过 sidecar 或 tc 脚本。
                 # 
                 # 但是！我们可以生成一个设置脚本 `setup_latency.sh`。
                 # 
                 # 咦，等等。用户请求 "用来更好观测"。
                 # 如果我们生成脚本，用户需要手动运行。
                 # 
                 # 让我们在 clab yaml 中为每个节点添加 exec 命令。
                 pass 

            clab_links.append(link_def)

        # 辅助函数：为所有接口设置延迟的命令
        # 我们可以利用 clab 的 `exec` 钩子。
        
        # 重新遍历 routers 添加 exec
        for router in routers:
            if config.link_delay and config.link_delay != "0ms":
                 # 简单的 tc 命令添加延迟
                 # 注意：这需要容器内有 tc 工具，或者宿主机支持。
                 # FRR 镜像通常包含 iproute2。
                 # 对每个接口（除了 lo 和 eth0-mgmt）添加 netem
                 cmds = []
                 for intf in router.interfaces.keys():
                     # qdisc add dev eth1 root netem delay 10ms
                     cmds.append(f"tc qdisc add dev {intf} root netem delay {config.link_delay}")
                 
                 # 添加到节点定义
                 if "exec" not in nodes[router.name]:
                     nodes[router.name]["exec"] = []
                 nodes[router.name]["exec"].extend(cmds)


        # 计算 CPU 亲和性范围
        if config.cpu_set == "auto":
            # auto 模式：0 ~ (cpus - 2)
            try:
                total_cpus = os.cpu_count() or 1
            except Exception:
                total_cpus = 1
            cpu_set_range = f"0-{max(0, total_cpus - 2)}"
        else:
            # 使用配置指定的值
            cpu_set_range = config.cpu_set

        # 生成完整配置
        protocol_suffix = get_protocol_suffix(config)
        clab_config = {
            "name": f"{protocol_suffix.replace('_', '-')}-{topo_suffix}{config.size}x{config.size}",
            "mgmt": {
                "ipv4-subnet": "10.0.0.0/16",
                "ipv6-subnet": "2001:db8::/64",
                "external-access": False, # 用户指定方便调试
            },
            "topology": {
                "defaults": {
                    # 限制所有容器 CPU 亲和性到 0~cpus-1，单容器上限可配置 CPU，内存上限可配置
                    "cpu-set": cpu_set_range,
                    "cpu": config.cpu_limit,
                    "memory": config.memory_limit,
                },
                "nodes": nodes,
                "links": clab_links
            }
        }

        return yaml.dump(clab_config, default_flow_style=False, indent=2)


# 便利函数
async def create_all_directories(
    config: TopologyConfig,
    routers: List[RouterInfo],
    requirements: SystemRequirements
) -> Result:
    """创建所有目录"""
    if getattr(config, "output_dir", None):
        base_dir = Path(str(config.output_dir))
    else:
        protocol_suffix = get_protocol_suffix(config)
        
        # 添加 LSA-only 后缀
        lsa_only_suffix = ""
        if config.ospf_config and config.ospf_config.lsa_only_mode:
            lsa_only_suffix = "_lsa_only"
        
        base_dir = Path(f"{protocol_suffix}_{get_topology_type_str(config.topology_type)}{config.size}x{config.size}{lsa_only_suffix}")

    fs_manager = FileSystemManager(base_dir)
    return await fs_manager.create_directory_structure(routers)


async def create_all_template_files(
    routers: List[RouterInfo],
    requirements: SystemRequirements,
    base_dir: Path,
    config: TopologyConfig = None
) -> Result:
    """创建所有模板文件"""
    fs_manager = FileSystemManager(base_dir)
    return await fs_manager.write_template_files(routers, config)


async def generate_all_config_files(
    config: TopologyConfig,
    routers: List[RouterInfo],
    interface_mappings: Dict[RouterName, Dict[str, str]],
    requirements: SystemRequirements,
    base_dir: Path
) -> Result:
    """生成所有配置文件"""
    fs_manager = FileSystemManager(base_dir)
    return await fs_manager.write_config_files(routers, config, interface_mappings)


async def generate_clab_yaml(
    config: TopologyConfig,
    routers: List[RouterInfo],
    links: List[Tuple[str, str, str, str]],
    base_dir: Path
) -> Result:
    """生成ContainerLab YAML"""
    fs_manager = FileSystemManager(base_dir)
    return await fs_manager.write_containerlab_yaml(config, routers, links)
