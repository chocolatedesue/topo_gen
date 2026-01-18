# Container Resource Monitoring

Tools for monitoring CPU and memory usage of router containers during OSPF tests.

## Quick Start

### 1. Monitor Resources

Monitor a single router in real-time:

```bash
./monitor_resources.sh clab-ospf6_grid5x5-router_00_00
```

Monitor multiple routers for comparison:

```bash
./monitor_resources.sh \
  clab-ospf6_grid5x5-router_00_00 \
  clab-ospf6_grid5x5-router_00_01
```

**Output**: CSV file `resource_usage.csv` with timestamp, container name, CPU%, memory usage, and memory%

### 2. Visualize Results

Generate a plot from the collected data:

```bash
# Using system Python with dependencies
python plot_resources.py resource_usage.csv -o usage_graph.png

# Using uv (recommended)
uv run plot_resources.py resource_usage.csv -o usage_graph.png
```

**Output**: PNG image showing CPU and memory usage over time

---

## Tools Overview

### `monitor_resources.sh`

Real-time container resource monitoring with CSV export.

**Features**:
- Monitor single or multiple containers simultaneously
- Configurable sampling interval
- CSV output with timestamps
- Graceful shutdown (Ctrl+C)
- Container validation

**Usage**:
```bash
./monitor_resources.sh [OPTIONS] CONTAINER [CONTAINER...]

OPTIONS:
    -i, --interval SECONDS  Sampling interval (default: 1)
    -o, --output FILE       Output CSV file (default: resource_usage.csv)
    -h, --help              Show help
```

**Examples**:
```bash
# Basic usage
./monitor_resources.sh clab-ospf6_grid5x5-router_00_00

# Custom interval (every 2 seconds)
./monitor_resources.sh -i 2 clab-ospf6_grid5x5-router_00_00

# Custom output file
./monitor_resources.sh -o test_data.csv clab-ospf6_grid5x5-router_00_00

# Background monitoring (run for 60 seconds)
./monitor_resources.sh clab-ospf6_grid5x5-router_00_00 &
MONITOR_PID=$!
sleep 60
kill $MONITOR_PID
```

### `plot_resources.py`

Visualize resource usage data from CSV files.

**Features**:
- Dual-axis plots (CPU% and Memory%)
- Multi-container support (one subplot per container)
- Statistics display (average and max values)
- Multiple output formats (PNG, PDF, SVG)

**Dependencies**:
```bash
# Install with uv
uv pip install matplotlib pandas
```

**Usage**:
```bash
python plot_resources.py [OPTIONS] CSV_FILE

OPTIONS:
    -o, --output FILE   Output image file
    -t, --title TEXT    Custom plot title
```

**Examples**:
```bash
# Display plot interactively
python plot_resources.py resource_usage.csv

# Save to PNG
python plot_resources.py resource_usage.csv -o graph.png

# Save to PDF with custom title
python plot_resources.py resource_usage.csv -o graph.pdf -t "LSA-only Test"
```

---

## Common Workflows

### Testing LSA-only Mode

Monitor the non-frozen router (`router_00_00`) during LSA-only tests:

```bash
# 1. Generate and deploy topology
uv run topo-gen generate grid 5 --lsa-only -y
sudo containerlab deploy -t ospf6_grid5x5/clab.yml

# 2. Start monitoring
./monitor_resources.sh -o lsa_only_test.csv clab-ospf6_grid5x5-router_00_00 &
MONITOR_PID=$!

# 3. Wait for convergence (or run your tests)
sleep 120

# 4. Stop monitoring
kill $MONITOR_PID

# 5. Generate visualization
uv run plot_resources.py lsa_only_test.csv -o lsa_only_graph.png -t "Router 00_00 - LSA-only Mode"
```

### Comparing Frozen vs Non-frozen Routers

Compare resource usage between a normal router and a frozen router:

```bash
# Monitor both routers
./monitor_resources.sh -o comparison.csv \
  clab-ospf6_grid5x5-router_00_00 \
  clab-ospf6_grid5x5-router_00_01 &

sleep 120
kill %1

# Visualize comparison
uv run plot_resources.py comparison.csv -o comparison.png
```

**Expected Results**:
- `router_00_00` (normal): Higher CPU usage due to SPF calculations
- `router_00_01` (frozen): Lower CPU usage (no SPF due to throttle)

### Stress Testing

Monitor resource spikes during network events:

```bash
# Start monitoring
./monitor_resources.sh -o stress_test.csv clab-ospf6_grid5x5-router_00_00 &

# Trigger link flap
docker exec clab-ospf6_grid5x5-router_01_01 ip link set eth1 down
sleep 5
docker exec clab-ospf6_grid5x5-router_01_01 ip link set eth1 up

# Continue monitoring for 60 seconds
sleep 60
kill %1

# Visualize
uv run plot_resources.py stress_test.csv -o stress_test.png
```

---

## CSV Format

The monitoring script generates CSV files with the following columns:

| Column      | Description                          | Example           |
|-------------|--------------------------------------|-------------------|
| Timestamp   | UTC timestamp                        | 2026-01-18 02:00:00 |
| Container   | Container name                       | clab-ospf6_grid5x5-router_00_00 |
| CPU%        | CPU usage percentage                 | 12.5              |
| MemUsage    | Current memory usage with unit       | 45.2MiB           |
| MemLimit    | Memory limit with unit               | 1.5GiB            |
| Mem%        | Memory usage percentage              | 3.01              |

**Example**:
```csv
Timestamp,Container,CPU%,MemUsage,MemLimit,Mem%
2026-01-18 02:00:00,clab-ospf6_grid5x5-router_00_00,12.5,45.2MiB,1.5GiB,3.01
2026-01-18 02:00:01,clab-ospf6_grid5x5-router_00_00,15.3,45.5MiB,1.5GiB,3.03
```

---

## Troubleshooting

### Container not found

**Error**: `Container 'xxx' not found or not running`

**Solution**: Verify container name and status
```bash
# List running containers
docker ps --format '{{.Names}}'

# Check if containerlab topology is deployed
sudo containerlab inspect -t ospf6_grid5x5/clab.yml
```

### Permission denied

**Error**: `Permission denied` when running Docker commands

**Solution**: Run with sudo or add user to docker group
```bash
# Add user to docker group (requires logout/login)
sudo usermod -aG docker $USER

# Or use sudo
sudo ./monitor_resources.sh clab-ospf6_grid5x5-router_00_00
```

### Missing Python dependencies

**Error**: `ModuleNotFoundError: No module named 'matplotlib'`

**Solution**: Install dependencies
```bash
uv pip install matplotlib pandas
```

### Plot not displaying

If the plot doesn't display in a headless environment (SSH without X11):

```bash
# Always save to file instead
python plot_resources.py data.csv -o output.png
```

---

## Performance Impact

The monitoring tools have minimal performance impact:

- **`docker stats`**: ~0.5% CPU overhead
- **Sampling interval**: 1 second is safe for most scenarios
- **CSV writing**: Negligible I/O impact

For extremely large topologies (100+ containers), consider:
- Increasing sampling interval to 2-5 seconds
- Monitoring only critical routers
- Using dedicated monitoring containers

---

## Related Tools

For production environments, consider:

- **Prometheus + cAdvisor**: For persistent metrics storage
- **Grafana**: For real-time dashboards
- **InfluxDB**: For time-series data

The scripts in this project are designed for quick testing and development workflows.
