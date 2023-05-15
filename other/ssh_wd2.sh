#!/usr/bin/expect -f
spawn ssh root@127.0.0.1
expect "assword:"
send "ph0nenumber\r"
expect "root@opteo"
send "exit\r"
interact