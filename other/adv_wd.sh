#!/bin/bash

AUDIO_PL="/var/starko/media/m_playlist"
VIDEO_PL="/var/starko/media/mon_playlist"
WALL_PL="/var/starko/media/playlist"
ADV_PL="/var/starko/media/adv_playlist"

PLS=0

IS_BLACKOUT=$(cat .current |grep is_blackout...true)

if [[ $IS_BLACKOUT ]]; then
    exit
fi

if [ ! -S /tmp/mpv-audio ]; then
    exit
fi

if [ -s $AUDIO_PL ]
then
    ((PLS=PLS+1))
fi

if [ -s $VIDEO_PL ]
then
    ((PLS=PLS+1))
fi

if [ -s $WALL_PL ]
then
    ((PLS=PLS+1))
fi

if [ -s $ADV_PL ]
then
    ((PLS=PLS+1))
fi

PL_POS_1=$(echo '{"command": ["get_property", "pause"]}' | socat - /tmp/mpv-audio | grep '"data":true')

if [[ $PL_POS_1 ]]; then

    MPV_PROCESSES=$(pgrep -c mpv)
    if [[ $MPV_PROCESSES < $PLS ]]; then
        echo '{"command": ["set_property", "pause", false]}' | socat - /tmp/mpv-audio
    fi
fi

PLAYLIST_ITEM=$(ls /var/starko/media/ | grep -w adv_playlist)
if [[ $PLAYLIST_ITEM ]]; then
    readarray ar < /var/starko/media/adv_playlist
    pl_len=${#ar[@]}
    first_play=1;
    adv_at_once=0;
    cur_time=$(date +"%s");
    for i in ${!ar[@]}; do
      t=${ar[i]}
      #printf '%s\n' "$t"
      IFS=: arrIN=(${t//:/:})
      aLen=${#arrIN[@]}
      if (( aLen > 1 )) || (($adv_at_once==1)); then
        first_play=0;
        if (( aLen > 1 )); then
            last_adv_time=${arrIN[1]};
        fi
        diff=$(($cur_time - $last_adv_time));
        # printf '%s\n' "$diff"
        if (( $diff > $1 )) || (($adv_at_once==1)); then
            track=${arrIN[0]};
            track=${track%$'\n'}
            track_line=$((i+1));
            # printf '%s\n' "$pl_len"
            # printf '%s\n' "$track_line"
            if (($pl_len == $track_line)); then
             next_track_line=1;
             next_track_name=${ar[0]};
             IFS=: arrOne=(${next_track_name//:/:})
             aOneLen=${#arrOne[@]}
             if (( aOneLen > 1 )); then
                next_track_name=${arrOne[0]};
             fi
             next_track_name=${next_track_name%$'\n'}
             else
             next_track_line=$(($track_line + 1));
             next_track_name=${ar[$track_line]};
             next_track_name=${next_track_name%$'\n'}
            fi
            # printf '%s\n' "$next_track_name"
            # printf '%s\n' "$track"
            sed -i "${track_line}s/.*/${track}/" /var/starko/media/adv_playlist
            sed -i "${next_track_line}s/.*/${next_track_name}:${cur_time}/" /var/starko/media/adv_playlist
            if [ ! -S /tmp/mpv-audio ]
            then
                exit
            fi
            echo '{"command": ["set_property", "pause", true]}' | socat - /tmp/mpv-audio
            mpv --audio-device=alsa/default:CARD=Headphones /var/starko/media/${next_track_name}
            if (($2==1)) && (($next_track_line!=1)); then
                adv_at_once=1;
            else
                adv_at_once=0;
            fi

        fi
      fi
    done
    if (($first_play==1)); then
        next_track_line=1;
        next_track_name=${ar[0]};
        next_track_name=${next_track_name%$'\n'}
        # printf '%s\n' "$next_track_name"
        # printf '%s\n' "1s/.*/${next_track_name}:${cur_time}/"
        sed -i "1s/.*/${next_track_name}:${cur_time}/" /var/starko/media/adv_playlist
        # mpc pause
        # omxplayer --no-keys -o alsa:hw:0,0 /var/starko/media/${next_track_name}
    fi
fi

#while sleep 2; do ./do-something.sh; done &
