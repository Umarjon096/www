#!/bin/bash
if [ ! -S /tmp/mpv-audio ]; then
    exit
fi

if [ -e /home/starko/bt_auto_connect ]; then
        BT=$(cat /var/lib/mpd/.asoundrc | grep device | awk '{print $2}' | sed -r 's/"//g')
fi
echo $BT
if [[ $BT ]]; then
        CONNECTED=$(echo -e "info $BT
        quit" | bluetoothctl | grep Connected | awk '{print $2}')
    echo $CONNECTED
        if [[ "$CONNECTED" != "yes" ]]; then
                sudo -H -u starko bash -c /home/starko/bt_auto_connect
        fi
fi
PL_POS_1=$(echo '{"command": ["get_property", "stream-pos"]}' | socat - /tmp/mpv-audio |grep -o '[0-9]*')
sleep 5
PL_POS_2=$(echo '{"command": ["get_property", "stream-pos"]}' | socat - /tmp/mpv-audio |grep -o '[0-9]*')
if [ $PL_POS_1 ] && [ $PL_POS_1 == $PL_POS_2 ]; then
        pkill -KILL -u starko
        exit
fi
PLAYLIST_ITEM=$(ls /var/starko/media/ | grep m_playlist)
RADIO_PROCESS=$(echo '{"command": ["get_property", "pause"]}' | socat - /tmp/mpv-audio | grep '"data":false')
if [[ ! $PLAYLIST_ITEM ]]; then
        exit
elif [[ $PLAYLIST_ITEM && $RADIO_PROCESS ]]; then
        exit
else
        PLAYLIST_URL=$(cat /var/starko/media/m_playlist | grep http:// | head -n 1)
        URL_AVAILABLE=$(curl -s --head $PLAYLIST_URL | head -n 1 | grep "HTTP/1.[01] [23]..")
        if [[ $PLAYLIST_URL && $URL_AVAILABLE ]]; then
                pkill -KILL -u starko
        elif [[ !$PLAYLIST_URL ]]; then
                pkill -KILL -u starko
        fi
fi