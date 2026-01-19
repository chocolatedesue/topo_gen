# 拓扑生成配置文档

本文档详细说明了拓扑生成器 (`topo_gen`) 的配置数据结构。该配置用于定义网络拓扑的形状、规模、IP规划以及各路由协议（OSPFv3, ISIS, BGP, BFD）的详细参数。

配置的核心类是 `TopologyConfig`，它可以包含多个子配置对象。

## 核心配置 (TopologyConfig)

位于 `src/topo_gen/core/models/topology.py`。

| 字段名 | 类型 | 默认值 | 描述 | 约束 |
| :--- | :--- | :--- | :--- | :--- |
| `size` | int | - | 网格大小（N x N） | 2 <= size <= 100 |
| `topology_type` | string (enum) | - | 拓扑类型 | `grid` (网格), `torus` (环形), `strip` (条带), `special` (特殊) |
| `multi_area` | bool | `False` | 是否启用多区域 | - |
| `area_size` | int | `None` | 多区域模式下的区域大小 | 必须 >= 2，且不能大于 `size` |
| `network_config` | NetworkConfig | (Default) | 基础网络/IP配置 | 见下文 |
| `ospf_config` | OSPFConfig | (Default) | OSPFv3 协议配置 | 见下文 |
| `isis_config` | ISISConfig | `None` | ISIS 协议配置 | 若为 `None` 则不启用 ISIS |
| `bgp_config` | BGPConfig | `None` | BGP 协议配置 | 若为 `None` 则不启用 BGP |
| `bfd_config` | BFDConfig | (Default) | BFD 协议配置 | 见下文 |
| `special_config` | SpecialTopologyConfig | `None` | 特殊拓扑配置 | 当 `topology_type` 为 `special` 时必填 |
| `output_dir` | Path | `None` | 输出目录 | 默认为自动生成的目录名 |
| `link_delay` | str | `"10ms"` | 链路延迟模拟参数 | - |

### 守护进程与生成控制
| 字段名 | 类型 | 默认值 | 描述 |
| :--- | :--- | :--- | :--- |
| `daemons_off` | bool | `False` | 是否关闭所有守护进程（仍生成配置） |
| `bgpd_off` | bool | `False` | 仅关闭 BGP 守护进程 |
| `ospf6d_off` | bool | `False` | 仅关闭 OSPFv3 守护进程 |
| `isisd_off` | bool | `False` | 仅关闭 ISIS 守护进程 |
| `bfdd_off` | bool | `False` | 仅关闭 BFD 守护进程 |
| `no_links` | bool | `False` | 仅生成节点，不生成链路配置（Containerlab） |
| `podman` | bool | `False` | 是否为 Podman 运行时优化 |
| `dummy_gen_protocols` | Set[str] | Empty | 需要生成空配置作为主文件（原配置存为 .bak）的协议 |
| `no_config_protocols` | Set[str] | Empty | 不生成任何配置的协议 |

---

## 基础网络配置 (NetworkConfig)

位于 `src/topo_gen/core/models/network.py`。用于定义 IPv6 地址规划。

| 字段名 | 类型 | 默认值 | 描述 |
| :--- | :--- | :--- | :--- |
| `ipv6_prefix` | str | `"2001:db8:1000::"` | 全局 IPv6 前缀 |
| `loopback_prefix` | str | `"2001:db8:1000::"` | Loopback 接口地址前缀 |
| `link_prefix` | str | `"2001:db8:2000::"` | 物理链路地址前缀 |
| `subnet_mask` | int | `127` | 链路子网掩码长度 (64-128) |

---

## 协议配置

### OSPFv3 配置 (OSPFConfig)
位于 `src/topo_gen/core/models/protocols/ospf.py`。

| 字段名 | 类型 | 默认值 | 描述 |
| :--- | :--- | :--- | :--- |
| `hello_interval` | int | `5` | Hello 报文间隔 (秒) |
| `dead_interval` | int | `20` | Dead 判定间隔 (秒)，必须 > hello_interval |
| `spf_delay` | int | `500` | SPF 计算延迟 (毫秒) |
| `area_id` | str | `"0.0.0.0"` | 默认区域 ID |
| `cost` | int | `None` | (可选) 接口开销 |
| `priority` | int | `None` | (可选) 路由器优先级 |
| `retransmit_interval` | int | `5` | LSA 重传间隔 (秒) |
| `transmit_delay` | int | `1` | LSA 传输延迟 (秒) |
| `lsa_min_arrival` | int | `1000` | LSA 最小到达间隔 (毫秒) |
| `maximum_paths` | int | `64` | ECMP 最大路径数 |
| `lsa_only_mode` | bool | `False` | 是否开启 LSA-Only 模式 |

### ISIS 配置 (ISISConfig)
位于 `src/topo_gen/core/models/protocols/isis.py`。

| 字段名 | 类型 | 默认值 | 描述 |
| :--- | :--- | :--- | :--- |
| `net_address` | str | (Required) | NET 地址 (如 `49.0001.0000.0000.0001.00`) |
| `level_type` | str | `"level-2"` | ISIS 级别 (`level-1`, `level-2`, `level-1-2`) |
| `metric_style` | str | `"wide"` | 度量样式 (`narrow`, `wide`, `transition`) |
| `hello_interval` | int | `3` | Hello 间隔 (秒) |
| `hello_multiplier` | int | `3` | Hello 倍数（决定 Dead 间隔） |
| `lsp_gen_interval` | int | `5` | LSP 生成间隔 (秒) |
| `lsp_refresh_interval` | int | `65000` | LSP 刷新间隔 (秒) |
| `max_lsp_lifetime` | int | `65535` | LSP 最大生存时间 (秒) |
| `spf_interval` | int | `5` | SPF 计算间隔 (秒) |
| `isis_metric` | int | `10` | 默认接口度量 |
| `three_way_handshake` | bool | `True` | 是否启用三路握手 |

### BGP 配置 (BGPConfig)
位于 `src/topo_gen/core/models/protocols/bgp.py`。

| 字段名 | 类型 | 默认值 | 描述 |
| :--- | :--- | :--- | :--- |
| `as_number` | int | (Required) | AS 号 (1-4294967295) |
| `router_id` | str | `None` | (可选) 路由器 ID |
| `enable_ipv6` | bool | `True` | 启用 IPv6 |
| `local_preference` | int | `100` | 本地优先级 |
| `hold_time` | int | `180` | 保持时间 (秒) |
| `keepalive_time` | int | `60` | 保活时间 (秒) |
| `connect_retry_time`| int | `120` | 连接重试时间 (秒) |

### BFD 配置 (BFDConfig)
位于 `src/topo_gen/core/models/protocols/bfd.py`。

| 字段名 | 类型 | 默认值 | 描述 |
| :--- | :--- | :--- | :--- |
| `enabled` | bool | `True` | 是否启用 BFD |
| `detect_multiplier` | int | `3` | 检测倍数 |
| `receive_interval` | int | `50` | 接收间隔 (毫秒) |
| `transmit_interval` | int | `50` | 发送间隔 (毫秒) |
| `echo_mode` | bool | `True` | 启用 Echo 模式 |
| `min_ttl` | int | `254` | 最小 TTL 值 |

---

## 特殊拓扑配置 (SpecialTopologyConfig)

当 `topology_type` 设置为 `special` 时使用。

| 字段名 | 类型 | 描述 |
| :--- | :--- | :--- |
| `source_node` | Coordinate | 源节点坐标 (row, col) |
| `dest_node` | Coordinate | 目标节点坐标 (row, col) |
| `gateway_nodes` | Set[Coordinate] | 网关节点集合 |
| `internal_bridge_edges` | List[Edge] | 内部桥接边列表 |
| `torus_bridge_edges` | List[Edge] | 环形桥接边列表 |
| `base_topology` | TopologyType | 基础拓扑类型 (Grid/Torus) |
| `include_base_connections`| bool | 是否包含基础连接 |

---

## 类型说明

- **Coordinate**: `(row, col)` 形式的坐标，例如 `Coordinate(0, 0)`。
- **TopologyType**: 枚举字符串，`grid`, `torus`, `strip`, `special`。
- **Direction**: `north`, `south`, `east`, `west`。
