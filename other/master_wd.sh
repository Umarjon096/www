#!/bin/bash
if [ ! -s /var/starko/vw_master_pl ]
then
    echo "Nothing to do here"
    exit
fi

if [ `ls -1 /tmp/master-* 2>/dev/null | wc -l ` -gt 1 ];
then
    kill $(pgrep -f 'python3 /var/starko/mpv-videowall/master.py')
    rm /tmp/master-*
    python3 /var/starko/mpv-videowall/master.py
    exit
fi

PIDFILE=$(ls -1 /tmp/master-*)

if [ $? -ne 0 ]; then
    python3 /var/starko/mpv-videowall/master.py
    exit
fi

PID=$(echo $PIDFILE | sed -e 's/.*-\(.*\)\..*/\1/')

if ! kill -0 $PID > /dev/null 2>&1; then
    python3 /var/starko/mpv-videowall/master.py
else
    echo "Already running"
    exit
fi
