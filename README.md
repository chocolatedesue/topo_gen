# Topo Gen

基于 uv 管理的现代化## 快速开始

### 1. 生成并部署拓扑

```bash
# 生成 20x20 的 Torus 拓扑 (400 节点)
uv run topo-gen generate torus 20 -y

# 启用 LSA-only 测试模式 (除 router_00_00 外延迟 SPF 计算)
uv run topo-gen generate torus 20 --lsa-only -y

# 使用 Containerlab 部署 (默认使用 Docker)
sudo containerlab deploy -t ospf6_torus20x20/ospf6_torus20x20.clab.yaml
```

> [!TIP]
> **关于运行环境 (Runtime)**
> - 本项目生成的配置包含 `network-mode: none`，目前 **Docker** 支持最为完善。
> - 若需使用 **Podman**，请确保您的环境支持对应网络模式，或在生成配置时进行相应调整（注：Podman 某些版本在使用 `none` 模式时可能存在兼容性问题）。

### 2. 常用管理命令

```bash
# 检查拓扑状态
sudo containerlab inspect -t ospf6_torus20x20/ospf6_torus20x20.clab.yaml

# 销毁拓扑
sudo containerlab destroy -t ospf6_torus20x20/ospf6_torus20x20.clab.yaml -c
```

## 环境依赖 (推荐 Nix)

本项目推荐使用 Nix 管理 Podman 和其他工具。详细配置方案请参考：
- [Nix 环境指南](docs/NIX_GUIDE.md)
- [完整操作文档](docs/README.md)

## 常用命令

*   **生成 Grid 拓扑**: `uv run topo-gen generate grid 4 -y`
*   **查看状态**: `sudo containerlab inspect --runtime podman -t ...`
*   **销毁拓扑**: `sudo containerlab destroy --runtime podman -t ...`
*   **清理环境**: `sudo containerlab destroy -a -y --runtime podman`

---
更多高级用法请查看 [docs/README.md](docs/README.md)
