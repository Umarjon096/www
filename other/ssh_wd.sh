#!/bin/bash
status=$(ssh -o BatchMode=yes -o ConnectTimeout=5 127.0.0.1 echo ok 2>&1)
if [[ $status == *"Connection closed"* ]] || [[ $status == *"Connection reset"* ]] || [[ $status == *"Connection refused"* ]]; then
 echo "ssh failed, reboot"
 reboot
fi
