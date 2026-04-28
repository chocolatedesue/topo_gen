# BIRD 配置生成

`topo_gen` 支持生成 REAL 风格的 BIRD BGP 配置：

```bash
uv run topo-gen generate grid 3 --disable-ospf6 --enable-bgp --bgp-stack bird -y
```

生成的文件位于每个节点目录：

```text
<output>/etc/router_00_00/conf/bird.conf
```

## 配置语义

- 每个节点使用自身 `router_id` 作为 BIRD `router id`。
- 每个节点通过 `protocol static` 起源自己的 loopback `/128`。
- 每个物理邻居展开为一个 `protocol bgp bgpN`。
- 邻居地址来自 topo_gen 已分配的 IPv6 点到点链路地址。
- AS 号沿用现有 BGP AS 分配逻辑，Grid/Torus/Strip 默认每节点一个 AS，Special 使用既有域划分。
- 不启用 `protocol kernel`，路由收敛验证面向 BIRD 控制面路由表，而不是 Linux FIB。

## 与 REAL 的对应关系

REAL 的 BIRD 模板使用 IPv4 `/30` 邻接和 `/24` service prefix。`topo_gen` 现有链路规划是 IPv6，因此迁移后保持控制面结构一致，但把邻接地址和起源前缀换成 IPv6：

```bird
protocol static static1 {
    ipv6;
    route 2001:db8:1000::1/128 blackhole;
}

protocol bgp bgp1 {
    local as 65000;
    neighbor 2001:db8:2000::7 as 65001;
    ipv6 {
        import all;
        export all;
    };
    hold time 0;
    startup hold time 65535;
    connect delay time 2;
}
```

如果需要同时生成 FRR 和 BIRD 配置，用：

```bash
uv run topo-gen generate torus 4 --enable-bgp --bgp-stack both -y
```

如果要直接生成可给 BIRD 容器挂载的 Containerlab 拓扑，关闭 Alpine 模式并指定 BIRD 镜像：

```bash
uv run topo-gen generate grid 3 \
  --disable-ospf6 \
  --enable-bgp \
  --bgp-stack bird \
  --no-alpine-mode \
  --container-image real-bird \
  -y
```

此模式下 `conf/` 会挂载到 `/etc/bird`，`log/` 会挂载到 `/var/log/real`。
