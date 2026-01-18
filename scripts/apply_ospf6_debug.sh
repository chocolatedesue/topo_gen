#!/bin/bash
set -e

# Apply OSPFv3 debug settings to all routers
echo "Enabling OSPFv3 performance debugging on all routers..."

for container in $(docker ps --format "{{.Names}}" | grep clab-ospf6-grid5x5-router_); do
    echo "Configuring $container..."
    docker exec $container vtysh -c "configure terminal" \
        -c "log file /var/log/frr/ospf6d.log" \
        -c "log timestamp precision 6" \
        -c "debug ospf6 spf time" \
        -c "debug ospf6 spf process" \
        -c "debug ospf6 spf database" \
        -c "debug ospf6 lsa flooding" \
        -c "debug ospf6 neighbor state" \
        -c "debug ospf6 route" \
        -c "write memory" > /dev/null
done

echo "Done! OSPFv3 debug enabled."
