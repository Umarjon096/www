#!/bin/bash

# Если у нас не указано имя пользователя, то нет смысла проверять дальше
ACTIVE="$(grep username /etc/spotifyd.conf)"
if [ "${ACTIVE}" = "username =" ]; then
    echo "No username, quitting..."
    exit
fi

STATUS="$(systemctl is-active spotifyd)"
if [ "${STATUS}" = "active" ]; then
    LOG="$(systemctl status spotifyd | tail -1)"
    if [[ $LOG == *"Country"* ]] || [[ $LOG == *"loaded"* ]] || [[ $LOG == *"Loading"* ]]; then
        echo "Works fine, quitting..."
        exit
    else
        echo "Restarting active..."
        systemctl restart spotifyd
    fi
else
    echo "Restarting inactive..."
    systemctl restart spotifyd
fi
