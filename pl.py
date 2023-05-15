# https://github.com/willprice/python-omxplayer-wrapper
from omxplayer import OMXPlayer
from time import sleep
import sys
from os import remove
import argparse
import subprocess

if __name__ == '__main__':

    subprocess.Popen('pkill -f omxplayer', shell=True)
    try:
        remove('/tmp/omxplayerdbus.starko')
        remove('/tmp/omxplayerdbus.starko.pid')
    except OSError:
        pass

    parser = argparse.ArgumentParser(description='OMXPlayer launcher')
    parser.add_argument('playlist', metavar='pl', type=str,
                       help='playlist path')
    parser.add_argument('--res', dest='res', type=str, default='1900x1480',
                       help='resolution')
    parser.add_argument('--shuffle', dest='shuffle', type=bool, default=False,
                       help='shuffle')
    parser.add_argument('--stream', dest='is_stream', type=bool, default=False,
                       help='is this stream')

    main_args = parser.parse_args()
    print(main_args)

    file_name = main_args.playlist
    fp = open(file_name)
    pl_files = fp.read().splitlines()

    resolution = main_args.res.split('x')
    shuffle = main_args.shuffle
    is_stream = main_args.is_stream
    x_res = resolution[0]
    y_res = resolution[1]

    args=['--adev=alsa', '--no-osd', '--no-keys', '--audio_queue=3', '--win=0,0,{0},{1}'.format(x_res, y_res)]
    files = pl_files if pl_files else []

    durations = []
    players = []

    #loop infinite
    player = None
    try:
        while True:
            for f in files:
                player = OMXPlayer(f, args=args)
                if not is_stream:
                    sleep(player.duration())
                    player.quit()
                else:
                    while True:
                        sleep(3600)

    except KeyboardInterrupt:
        if player:
            player.quit()

    print('Quiting')


