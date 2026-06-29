#!/bin/bash

THRESHOLD=80

echo "-----$(date)------"

df -h | awk 'NR>1 {print $5 " " $1}' | while read output
do
	usage=$(echo $output | awk '{print $1}' | tr -d '%')
	partition=$(echo $output | awk '{print $2}')

	if [ "$usage" -ge "$THRESHOLD" ]; then
		echo "WARNING: $partition is ${usage}% full"
	else
		echo "OK: $partition is ${usage}% used"
	fi
done

echo " "
