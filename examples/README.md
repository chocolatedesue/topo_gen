# Examples Directory

This directory contains example outputs from monitoring and testing tools.

## Contents

- **CSV files**: Resource monitoring data
- **PNG files**: Visualization graphs
- **Log files**: Test execution logs

## Note

Files in this directory are gitignored and meant for local testing/demonstration purposes only.

To regenerate examples, run:

```bash
# Resource monitoring example
cd ..
./tools/monitor_resources.sh clab-ospf6-grid5x5-router_00_00

# Visualization
./tools/plot_resources.py resource_usage.csv -o examples/example_graph.png
```
