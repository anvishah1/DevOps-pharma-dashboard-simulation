#!/bin/bash

LOG_FILE="/home/anvi2026/capstone-project/disk_warning_log.txt"
TEMP_FILE="/home/anvi2026/capstone-project/disk_warning_log.tmp"

if [ ! -f "$LOG_FILE" ]; then
    exit 0
fi

awk '
/^-----/ {
    n++
    block[n] = $0 ORS
    next
}

n > 0 {
    block[n] = block[n] $0 ORS
}

END {
    if (n == 0) {
        exit 1
    }

    start = n - 2

    if (start < 1) {
        start = 1
    }

    for (i = start; i <= n; i++) {
        printf "%s", block[i]
    }
}
' "$LOG_FILE" > "$TEMP_FILE"

if [ -s "$TEMP_FILE" ]; then
    mv "$TEMP_FILE" "$LOG_FILE"
else
    rm -f "$TEMP_FILE"
fi
