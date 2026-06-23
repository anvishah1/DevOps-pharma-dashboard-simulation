#!/bin/bash

echo "---SERVER HEALTH REPORT ---"

disk=$(df -h / | awk 'NR==2 {print $5}' | tr -d  '%')
if [ $disk -lt 80 ]; then
	echo "Disk: OK($disk%)"
elif [ $disk -ge 80 ] && [ $disk -le 90 ]; then
	echo "Disk: WARNING ($disk%)"
else
	echo "Disk: CRITICAL ($disk%)"
fi

mem=$(free | awk 'NR==2 {printf "%.0f", $3/$2 * 100}')
if [ $mem -lt 75 ]; then
	echo "Memory: OK ($mem%)"
elif [ $mem -ge 75 ] && [ $mem -le 90 ]; then
	echo "Memory: WARNING ($mem%)"
else
	echo "Memory: CRITICAL ($mem%)"
fi

cpu=$(top -bn2 | awk -F',' '/Cpu\(s\)/ {idle=$4} END {print 100-idle}' | cut -d'.' -f1)
cpu=${cpu%.*}
if [ $cpu -lt 70 ]; then
        echo "CPU: OK ($cpu%)"
elif [ $cpu -ge 70 ] && [ $cpu -le 85 ]; then
        echo "CPU: WARNING ($cpu%)"
else
        echo "CPU: CRITICAL ($cpu%)"
fi

service=$(systemctl is-active nginx)
if [ "$service" = "active" ]; then
	echo "Nginx: OK(active)"
else
	echo "Nginx: CRITICAL(inactive)"
fi

ping -c 1 google.com > /dev/null 2>&1
if [ $? -eq 0 ]; then
	echo "Network: OK"
else
	echo "Network: CRITIAL"
fi


