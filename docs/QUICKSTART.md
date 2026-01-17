# 快速开始指南

## 5分钟快速上手

### 1. 安装uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 克隆并安装

```bash
git clone <repository-url>
cd topo_gen
uv sync
```

### 3. 生成拓扑

```bash
# 生成3x3 OSPF6 Torus拓扑
uv run topo-gen generate torus 3 -y
```

### 4. 部署

```bash
cd ospf6_torus3x3
containerlab deploy -t ospf6_torus3x3.clab.yaml
```

### 5. 验证

```bash
# 进入路由器
docker exec -it clab-ospf6-torus3x3-router_00_00 vtysh

# 查看邻居
show ipv6 ospf6 neighbor

# 查看路由
show ipv6 route ospf6
```

## 常用示例

### Grid拓扑 + ISIS

```bash
uv run topo-gen generate grid 4 --enable-isis -y
cd isis_grid4x4
containerlab deploy -t isis_grid4x4.clab.yaml
```

### Torus拓扑 + OSPF6 + BGP

```bash
uv run topo-gen generate torus 5 --enable-bgp -y
cd ospf6_torus5x5
containerlab deploy -t ospf6_torus5x5.clab.yaml
```

### 多区域OSPF

```bash
uv run topo-gen generate grid 6 --multi-area --area-size 3 -y
```

## 销毁拓扑

```bash
cd ospf6_torus3x3
containerlab destroy -t ospf6_torus3x3.clab.yaml
```

## 下一步

查看完整文档：[docs/README.md](README.md)
