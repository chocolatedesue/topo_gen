#!/bin/bash
#
# Container Resource Monitoring Script
# 
# Monitors CPU and memory usage of Docker containers and exports to CSV
# Usage: ./monitor_resources.sh [OPTIONS] CONTAINER [CONTAINER...]
#

set -euo pipefail

# Default values
INTERVAL=1
OUTPUT_FILE="resource_usage.csv"
CONTAINERS=()

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Usage message
usage() {
    cat << EOF
Usage: $0 [OPTIONS] CONTAINER [CONTAINER...]

Monitor Docker container CPU and memory usage and export to CSV.

OPTIONS:
    -i, --interval SECONDS  Sampling interval in seconds (default: 1)
    -o, --output FILE       Output CSV file (default: resource_usage.csv)
    -h, --help              Show this help message

EXAMPLES:
    # Monitor single container
    $0 clab-ospf6_grid5x5-router_00_00

    # Monitor multiple containers
    $0 clab-ospf6_grid5x5-router_00_00 clab-ospf6_grid5x5-router_00_01

    # Custom interval and output file
    $0 -i 2 -o custom.csv clab-ospf6_grid5x5-router_00_00

EOF
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--interval)
            INTERVAL="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        -*)
            echo -e "${RED}Unknown option: $1${NC}" >&2
            usage
            ;;
        *)
            CONTAINERS+=("$1")
            shift
            ;;
    esac
done

# Validate arguments
if [ ${#CONTAINERS[@]} -eq 0 ]; then
    echo -e "${RED}Error: At least one container name is required${NC}" >&2
    usage
fi

# Validate interval is a number
if ! [[ "$INTERVAL" =~ ^[0-9]+$ ]]; then
    echo -e "${RED}Error: Interval must be a positive integer${NC}" >&2
    exit 1
fi

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker command not found${NC}" >&2
    exit 1
fi

# Verify containers exist
for container in "${CONTAINERS[@]}"; do
    if ! docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        echo -e "${RED}Error: Container '${container}' not found or not running${NC}" >&2
        echo -e "${YELLOW}Available containers:${NC}"
        docker ps --format '{{.Names}}'
        exit 1
    fi
done

# Initialize CSV file with headers
echo "Timestamp,Container,CPU%,MemUsage,MemLimit,Mem%" > "$OUTPUT_FILE"

echo -e "${GREEN}Starting monitoring...${NC}"
echo -e "Containers: ${CONTAINERS[*]}"
echo -e "Interval: ${INTERVAL}s"
echo -e "Output: ${OUTPUT_FILE}"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""

# Cleanup function
cleanup() {
    echo -e "\n${GREEN}Monitoring stopped.${NC}"
    echo -e "Data saved to: ${OUTPUT_FILE}"
    
    # Show statistics
    if [ -f "$OUTPUT_FILE" ]; then
        RECORD_COUNT=$(($(wc -l < "$OUTPUT_FILE") - 1))
        echo -e "Total records: ${RECORD_COUNT}"
    fi
    
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

# Monitoring loop
SAMPLE_COUNT=0
while true; do
    TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S")
    
    # Get stats for all containers
    for container in "${CONTAINERS[@]}"; do
        # Use docker stats with --no-stream to get a single snapshot
        STATS=$(docker stats --no-stream --format "{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}}" "$container" 2>/dev/null)
        
        if [ -n "$STATS" ]; then
            # Parse the output
            CPU=$(echo "$STATS" | cut -d',' -f1 | tr -d '%')
            MEM_USAGE=$(echo "$STATS" | cut -d',' -f2 | cut -d'/' -f1 | xargs)
            MEM_LIMIT=$(echo "$STATS" | cut -d',' -f2 | cut -d'/' -f2 | xargs)
            MEM_PERC=$(echo "$STATS" | cut -d',' -f3 | tr -d '%')
            
            # Write to CSV
            echo "${TIMESTAMP},${container},${CPU},${MEM_USAGE},${MEM_LIMIT},${MEM_PERC}" >> "$OUTPUT_FILE"
            
            # Display progress
            ((SAMPLE_COUNT++))
            if [ $((SAMPLE_COUNT % 10)) -eq 0 ]; then
                echo -e "${GREEN}[${TIMESTAMP}]${NC} Collected ${SAMPLE_COUNT} samples..."
            fi
        else
            echo -e "${RED}Warning: Failed to get stats for ${container}${NC}" >&2
        fi
    done
    
    sleep "$INTERVAL"
done
