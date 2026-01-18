#!/bin/bash

LOG_FILE=$1

if [ -z "$LOG_FILE" ]; then
    echo "Usage: $0 <path_to_ospf6d.log>"
    exit 1
fi

echo "=== OSPFv3 SPF Performance Analysis ==="
echo "Log File: $LOG_FILE"

# Count SPF runs
SPF_COUNT=$(grep "SPF processing" $LOG_FILE | wc -l)
echo "Total SPF Executions: $SPF_COUNT"

echo ""
echo "=== Last 10 SPF Runs (Time in usec) ==="
grep "SPF runtime" $LOG_FILE | tail -n 10 | awk '{
    for(i=1;i<=NF;i++) {
        if ($i == "runtime:") {
            sec = $(i+1)
            usec = $(i+3)
            print "SPF Run: " sec " sec " usec " usec"
        }
    }
}'

echo ""
echo "=== Top 5 Slowest SPF Runs ==="
grep "SPF runtime" $LOG_FILE | awk '{
    for(i=1;i<=NF;i++) {
        if ($i == "runtime:") {
            sec = $(i+1)
            usec = $(i+3)
            total_usec = sec * 1000000 + usec
            print total_usec " usec (" $0 ")"
        }
    }
}' | sort -nr | head -n 5

echo ""
echo "=== SPF Trigger Reasons ==="
grep "Reason:" $LOG_FILE | awk -F "Reason:" '{print $2}' | sort | uniq -c | sort -nr

echo ""
echo "=== LSA Database Size (at SPF time) ==="
grep "SPF on DB" $LOG_FILE | tail -n 5

