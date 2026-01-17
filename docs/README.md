# Topo Gen 操作文档

基于uv管理的现代化OSPF6/ISIS拓扑生成工具。

## 目录

- [快速开始](#快速开始)
- [安装](#安装)
- [基本使用](#基本使用)
- [拓扑类型](#拓扑类型)
- [高级配置](#高级配置)
- [部署与管理](#部署与管理)
- [故障排查](#故障排查)

## 快速开始

### 生成3x3 Torus拓扑

```bash
# 生成拓扑配置
uv run topo-gen generate torus 3 -y

# 部署到ContainerLab
cd ospf6_torus3x3
containerlab deploy -t ospf6_torus3x3.clab.yaml

# 进入路由器查看
docker exec -it clab-ospf6-torus3x3-router_00_00 vtysh
```

## 安装

### 前置要求

- Python 3.13+
- uv (Python包管理器)
- Docker
- ContainerLab

### 安装uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 安装项目

```bash
# 克隆仓库
git clone <repository-url>
cd topo_gen

# 安装依赖
uv sync

# 验证安装
uv run topo-gen --help
```

## 基本使用

### 命令行界面

```bash
# 查看帮助
uv run topo-gen --help

# 生成拓扑
uv run topo-gen generate [TOPOLOGY_TYPE] [SIZE] [OPTIONS]

# 从配置文件生成
uv run topo-gen from-config -c config.yaml

# 生成特殊拓扑
uv run topo-gen special [OPTIONS]
```

### 常用选项

```bash
# 启用ISIS协议
uv run topo-gen generate grid 4 --enable-isis

# 启用BGP
uv run topo-gen generate torus 5 --enable-bgp

# 启用BFD
uv run topo-gen generate grid 3 --enable-bfd

# 禁用OSPF6
uv run topo-gen generate grid 4 --disable-ospf6 --enable-isis

# 多区域OSPF
uv run topo-gen generate grid 6 --multi-area --area-size 3

# 禁用日志
uv run topo-gen generate torus 3 --disable-logging

# 指定输出目录
uv run topo-gen generate grid 4 -o my_topology
```

## 拓扑类型

### Grid (网格拓扑)

标准的二维网格拓扑，每个路由器最多有4个邻居（东、西、南、北）。

```bash
uv run topo-gen generate grid 4 -y
```

**特点**:
- 适合测试标准路由协议
- 清晰的层次结构
- 易于理解和调试

### Torus (环形拓扑)

网格拓扑的变体，边缘节点环绕连接形成环形结构。

```bash
uv run topo-gen generate torus 3 -y
```

**特点**:
- 所有节点都有4个邻居
- 无边缘节点
- 适合测试收敛性能

### Strip (条带拓扑)

仅在纵向（南北）方向环绕的拓扑。

```bash
uv run topo-gen generate strip 4 -y
```

**特点**:
- 横向有边缘，纵向环绕
- 中间形态
- 适合特定测试场景

### Special (特殊拓扑)

支持多AS的复杂拓扑，包含gateway节点和域间BGP。

```bash
uv run topo-gen special --size 6 -y
```

**特点**:
- 多AS架构
- iBGP + eBGP
- 复杂路由策略

## 高级配置

### OSPF6参数调优

```bash
uv run topo-gen generate grid 5 \
  --hello-interval 1 \
  --dead-interval 5 \
  --spf-delay 10 \
  --lsa-min-arrival 500 \
  --maximum-paths 4 \
  -y
```

### ISIS参数调优

```bash
uv run topo-gen generate torus 4 \
  --enable-isis \
  --isis-hello-interval 2 \
  --isis-hello-multiplier 3 \
  --isis-vertical-metric 10 \
  --isis-horizontal-metric 20 \
  --isis-fast-convergence \
  -y
```

### BGP配置

```bash
uv run topo-gen generate grid 4 \
  --enable-bgp \
  --bgp-as 65001 \
  -y
```

### 守护进程控制

```bash
# 关闭所有守护进程（仅生成配置文件）
uv run topo-gen generate grid 3 --daemons-off -y

# 仅关闭BGP守护进程
uv run topo-gen generate grid 3 --enable-bgp --bgpd-off -y

# 仅关闭OSPF6守护进程
uv run topo-gen generate grid 3 --ospf6d-off -y

# 生成空配置（dummy模式）
uv run topo-gen generate grid 3 --dummy-gen ospf6d,bgpd -y

# 不生成配置文件
uv run topo-gen generate grid 3 --no-config ospf6d -y
```

## 部署与管理

### 部署拓扑

```bash
# 进入生成的目录
cd ospf6_torus3x3

# 部署
containerlab deploy -t ospf6_torus3x3.clab.yaml

# 查看状态
containerlab inspect -t ospf6_torus3x3.clab.yaml
```

### 销毁拓扑

```bash
# 销毁拓扑
containerlab destroy -t ospf6_torus3x3.clab.yaml

# 强制销毁（清理所有资源）
containerlab destroy -t ospf6_torus3x3.clab.yaml --cleanup
```

### 访问路由器

```bash
# 进入路由器CLI
docker exec -it clab-ospf6-torus3x3-router_00_00 vtysh

# 执行单条命令
docker exec clab-ospf6-torus3x3-router_00_00 vtysh -c "show ipv6 ospf6 neighbor"

# 进入Shell
docker exec -it clab-ospf6-torus3x3-router_00_00 bash
```

### 常用FRR命令

```bash
# OSPF6
show ipv6 ospf6 neighbor
show ipv6 ospf6 database
show ipv6 ospf6 route
show ipv6 ospf6 interface

# ISIS
show isis neighbor
show isis database
show isis route
show isis interface

# BGP
show bgp ipv6 unicast summary
show bgp ipv6 unicast neighbors
show bgp ipv6 unicast

# 路由表
show ipv6 route
show ipv6 route ospf6
show ipv6 route isis
show ipv6 route bgp

# BFD
show bfd peers
```

## 生成文件结构

```
ospf6_torus3x3/
├── ospf6_torus3x3.clab.yaml    # ContainerLab配置
├── configs/                     # 备用配置目录
└── etc/                         # 路由器配置
    ├── router_00_00/
    │   ├── conf/               # FRR配置文件
    │   │   ├── daemons
    │   │   ├── zebra.conf
    │   │   ├── ospf6d.conf
    │   │   ├── isisd.conf      # 如果启用ISIS
    │   │   ├── bgpd.conf       # 如果启用BGP
    │   │   ├── bfdd.conf       # 如果启用BFD
    │   │   ├── mgmtd.conf
    │   │   ├── staticd.conf
    │   │   └── vtysh.conf
    │   └── log/                # 日志目录
    │       ├── zebra.log
    │       ├── ospf6d.log
    │       └── ...
    └── router_00_01/
        └── ...
```

## ContainerLab配置说明

生成的ContainerLab配置包含以下关键特性：

### 节点配置

```yaml
nodes:
  router_00_00:
    kind: linux
    image: docker.cnb.cool/jmncnic/frrbgpls/origin
    network-mode: none    # 关闭Docker管理网络
    binds:
      - etc/router_00_00/conf:/etc/frr
      - etc/router_00_00/log:/var/log/frr
```

### 资源限制

```yaml
topology:
  defaults:
    cpu-set: 0-6          # CPU亲和性
    memory: 512MB         # 内存限制
```

### 管理网络

```yaml
mgmt:
  network: ospf6-torus3x3-mgmt
  ipv4-subnet: 172.23.0.0/24
  ipv6-subnet: 3fff:172:23::/64
```

注意：虽然配置了管理网络，但由于`network-mode: none`，容器实际不会连接到管理网络。

## 故障排查

### 容器无法启动

```bash
# 查看容器日志
docker logs clab-ospf6-torus3x3-router_00_00

# 检查镜像
docker images | grep frr

# 重新拉取镜像
docker pull docker.cnb.cool/jmncnic/frrbgpls/origin
```

### 路由协议未收敛

```bash
# 检查守护进程状态
docker exec clab-ospf6-torus3x3-router_00_00 vtysh -c "show daemons"

# 检查接口状态
docker exec clab-ospf6-torus3x3-router_00_00 vtysh -c "show interface"

# 检查配置
docker exec clab-ospf6-torus3x3-router_00_00 cat /etc/frr/ospf6d.conf

# 查看日志
docker exec clab-ospf6-torus3x3-router_00_00 cat /var/log/frr/ospf6d.log
```

### 网络冲突

如果遇到Docker网络冲突：

```bash
# 列出现有网络
docker network ls

# 删除未使用的网络
docker network prune

# 或修改yaml文件中的管理网络配置
# 使用不冲突的IP段
```

### 清理环境

```bash
# 销毁所有ContainerLab拓扑
containerlab destroy --all

# 清理Docker资源
docker system prune -a

# 清理生成的目录
rm -rf ospf6_*/ isis_*/ bgp_*/
```

## 性能优化建议

### 大规模拓扑

对于大型拓扑（如10x10或更大）：

1. **调整系统限制**
```bash
# 增加文件描述符限制
ulimit -n 65536

# 增加inotify限制
sudo sysctl fs.inotify.max_user_instances=8192
sudo sysctl fs.inotify.max_user_watches=524288
```

2. **优化路由协议参数**
```bash
# 使用较大的hello间隔
uv run topo-gen generate grid 10 \
  --hello-interval 5 \
  --dead-interval 20 \
  --spf-delay 50 \
  -y
```

3. **限制资源使用**
```bash
# 在yaml中调整资源限制
cpu: 0.5          # 限制每容器CPU
memory: 256MB     # 减少内存使用
```

## 开发相关

### 项目结构

```
topo_gen/
├── src/topo_gen/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py              # CLI入口
│   ├── cli_special.py      # Special拓扑CLI
│   ├── engine.py           # 拓扑生成引擎
│   ├── filesystem.py       # 文件系统操作
│   ├── links.py            # 链路计算
│   ├── config/             # 配置模块
│   ├── core/               # 核心类型和模型
│   ├── generators/         # 配置生成器
│   ├── topology/           # 拓扑算法
│   └── utils/              # 工具函数
├── docs/                   # 文档
├── pyproject.toml          # 项目配置
└── uv.lock                 # 依赖锁文件
```

### 添加新依赖

```bash
uv add <package-name>
```

### 运行测试

```bash
uv run pytest
```

## 参考资料

- [FRRouting Documentation](https://docs.frrouting.org/)
- [ContainerLab Documentation](https://containerlab.dev/)
- [uv Documentation](https://github.com/astral-sh/uv)

## 许可证

请参考项目根目录的LICENSE文件。
