#!/bin/sh

# controlled by Cron

read PM10 < /home/chip/PM10
echo -n "PM10 = "
echo "$PM10"

/home/chip/CHIPPushover.sh "$PM10"