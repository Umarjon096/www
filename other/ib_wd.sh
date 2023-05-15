#!/bin/bash
VIDEO_PL="/var/starko/media/mon_playlist"
AUDIO_PL="/var/starko/media/m_playlist"
VW_PL="/var/starko/media/playlist"

PLS=0
IB_PL=0

# Если у нас работает cec-menu, то выходим
if ps -p $(cat /tmp/cec-menu.pid) > /dev/null 2>&1
then
    exit;
fi

# Чекаем, что у нас есть плейлист с видео
if [ -s $VIDEO_PL ]
then
    ((PLS=PLS+1))
fi

# Чекаем, что у нас есть плейлист с музыкой
if [ -s $AUDIO_PL ]
then
    ((PLS=PLS+1))
fi

# Чекаем, что у нас есть плейлист для видеостен
if [ -s $VW_PL ]
then
    ((PLS=PLS+1))
    ((IB_PL=IB_PL+1))
fi

# Если нет ни одного плейлиста, то идем дальше
if [ $PLS -ne 0 ]
then
    MPV_PROCS=$(pgrep -c mpv)

    # Если у нас процессов меньше, чем плейлистов, то беда
    if (( PLS > MPV_PROCS ))
    then
        # Попробуем еще раз, на всякий
        sleep 5
        MPV_PROCS=$(pgrep -c mpv)
        if (( PLS > MPV_PROCS ))
        then
            # Если ничего не изменилось, то перезагрузимся
            if [ $IB_PL == 0 ]
            then
                reboot -f;
            fi
        else
            # Если изменилось и все ок, то выходим
            exit;
        fi
    else
        # Если их больше или столько же, то можно выходить
        exit;
    fi
fi

# Оказываемся здесь, только если нет плейлистов для mpv
PLAYLIST_ITEM=$(ls /var/starko/media/ | grep -w playlist)
IB_PROCESS=$(pgrep info-beamer)
if [[ ! $PLAYLIST_ITEM ]]; then
    exit;
elif [[ $PLAYLIST_ITEM && $IB_PROCESS ]]; then
    exit;
else
    sleep 5
    IB_PROCESS=$(pgrep info-beamer)
    if [[ ! $IB_PROCESS ]]; then
        reboot -f;
    fi
fi
