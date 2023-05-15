#!/bin/bash

sed -n '/#s_s/,/#s_e/{/#s_s/b;/#s_e/b;p}' /etc/chrony/chrony.conf | awk {'print $2'} | xargs -I {} host {} | awk '/has address/ { print $4}' | xargs -I {} chronyc add server {} iburst
