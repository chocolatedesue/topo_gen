# Topo Gen

基于 uv 管理的现代化 OSPFv3/ISIS/BGP 拓扑生成器。

## 快速开始

```bash
# 生成拓扑
uv run topo-gen generate grid 5 -y

# 启用 LSA-only 测试模式 (除 router_00_00 外延迟 SPF 计算)
uv run topo-gen generate torus 20 --lsa-only -y

# 部署拓扑 (使用 Docker)
sudo containerlab deploy -t ospf6_torus20x20/ospf6_torus20x20.clab.yaml

# 销毁拓扑
sudo containerlab destroy -t ospf6_torus20x20/ospf6_torus20x20.clab.yaml -c
```

> [!TIP]
> **关于运行环境 (Runtime)**
> - 本项目生成的配置包含 `network-mode: none`，目前 **Docker** 支持最为完善。
> - 若需使用 **Podman**，请确保您的环境支持对应网络模式。

## 目录结构

```
.
├── src/topo_gen/      # 核心源代码
├── docs/              # 文档
│   ├── QUICKSTART.md  # 快速开始指南
│   └── monitoring.md  # 监控工具文档
├── scripts/           # OSPF 分析和调试脚本
│   ├── analyze_ospf6_spf.sh
│   └── apply_ospf6_debug.sh
├── tools/             # 资源监控工具
│   ├── monitor_resources.sh  # Docker stats 监控
│   └── plot_resources.py     # 可视化脚本
└── examples/          # 示例输出 (gitignored)
```

## 监控工具

新增容器资源监控功能：

```bash
# 监控路由器资源使用
./tools/monitor_resources.sh clab-ospf6-grid5x5-router_00_00

# 生成可视化图表
uv run ./tools/plot_resources.py resource_usage.csv -o graph.png
```

详见 [docs/monitoring.md](docs/monitoring.md)

## 文档

- [快速开始](docs/QUICKSTART.md)
- [监控工具](docs/monitoring.md)
- [Nix 环境](docs/NIX_GUIDE.md)

---

更多高级用法请查看 [docs/README.md](docs/README.md)
