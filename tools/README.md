# Tools Directory

Container resource monitoring and visualization tools.

## Tools

### `monitor_resources.sh`
Real-time Docker container resource monitoring with CSV export.

**Usage**:
```bash
./tools/monitor_resources.sh [OPTIONS] CONTAINER [CONTAINER...]

OPTIONS:
    -i, --interval SECONDS  Sampling interval (default: 1)
    -o, --output FILE       Output CSV file (default: resource_usage.csv)
    -h, --help              Show help
```

**Example**:
```bash
# Monitor single container
./tools/monitor_resources.sh clab-ospf6-grid5x5-router_00_00

# Monitor multiple containers
./tools/monitor_resources.sh \
  clab-ospf6-grid5x5-router_00_00 \
  clab-ospf6-grid5x5-router_00_01
```

### `plot_resources.py`
Visualize resource usage data from CSV files.

**Usage**:
```bash
python3 ./tools/plot_resources.py [OPTIONS] CSV_FILE

OPTIONS:
    -o, --output FILE   Output image file (PNG, PDF, SVG)
    -t, --title TEXT    Custom plot title
```

**Example**:
```bash
# Generate PNG graph
python3 ./tools/plot_resources.py resource_usage.csv -o graph.png

# Use with uv
uv run ./tools/plot_resources.py resource_usage.csv -o graph.png
```

**Dependencies**:
```bash
uv pip install matplotlib pandas
```

## Documentation

See [docs/monitoring.md](../docs/monitoring.md) for comprehensive usage guide.
