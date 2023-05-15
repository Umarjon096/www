#!/usr/bin/env python3

import json
import logging
import os
import socket
import struct
import subprocess
import sys

from typing import Dict, List


def ipc_command(ipc: open, command: List[object]) -> object:
    req_id = ipc_command.request_id
    ipc_command.request_id += 1
    line = '{"command":%s,"request_id":%d}\n' % (json.dumps(command), req_id)
    ipc.write(line)
    ipc.flush()
    for line in ipc:
        obj = json.loads(line)
        if 'err' in obj and obj['error'] != 'success':
            logging.error('mpv error: %r' % obj['error'])
        if obj.get('request_id') == req_id:
            return obj.get('data')


ipc_command.request_id = 0


def clamp(value: float, low: float, high: float) -> float:
    return min(max(value, low), high)


MEDIA_PATH = "/var/starko/media/"


def parse_media(playlist_path: str) -> Dict[str, int]:
    """Получаем пути до файлов и их длительности"""
    media = {}
    prev = 0

    with open(playlist_path, "r") as file:
        for line in file.readlines():
            name, duration = line.split(",")
            media[prev] = name
            prev += int(duration)

    return media


def get_cur_file(position: float, playlist: Dict[str, int]) -> str:
    """Получаем файл для текущего времени"""
    for i, key in enumerate(sorted(playlist, reverse=True)):
        if key <= position:
            return playlist[key], key, len(playlist) - i - 1


def main(argv: List[str]) -> int:
    logging.basicConfig(level=logging.INFO)

    if len(argv) < 4:
        sys.stdout.write(
            'Usage: ./slave.py bind port playlist [mpv_args ...]\n\n'
        )
        return 1

    logging.info("Setting listening address to '%s:%s" % (argv[1], argv[2]))
    addr = (argv[1], int(argv[2]))
    logging.info("Setting media file to '%s'" % argv[3])
    media = parse_media(argv[3])
    media_length = sum(media.keys())
    mpv_args = argv[4:]

    logging.info("Listening on '%s:%s'" % (argv[1], argv[2]))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(addr)
    ipc_path = "/tmp/mpv-video"
    logging.info('Starting mpv on %s' % ipc_path)
    subprocess.Popen([
        'mpv',
        '--idle=yes',
        '--keep-open=always'
    ] + mpv_args)
    ipc = None

    while True:
        buf, master = sock.recvfrom(8)
        target, = struct.unpack("!d", buf)

        if target >= media_length:
            target = target - media_length

        if ipc is None:
            if os.path.exists(ipc_path):
                ipc_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                ipc_sock.connect(ipc_path)
                ipc = ipc_sock.makefile("rw")
                ipc_command(ipc, ["set_property", "audio-pitch-correction", "yes"])
                ipc_command(ipc, ["set_property", "autosync", "1"])
                for key in sorted(media):
                    ipc_command(ipc, [
                        "loadfile",
                        MEDIA_PATH + media[key],
                        "append"
                    ])

            else:
                logging.error("IPC socket not ready, retrying")
                continue

        current_file = ipc_command(ipc, ["get_property", "filename"])

        if target == 0.0:
            ipc_command(ipc, ["set_property", "speed", 1])
            ipc_command(ipc, ["set_property", "time-pos", 0])
            ipc_command(ipc, ["set_property", "pause", "no"])

        else:
            pos = ipc_command(ipc, ["get_property", "time-pos"])
            if pos is None:
                pos = 0

            new_file, file_start, file_number = get_cur_file(target, media)
            target = target - file_start
            if current_file != new_file:
                ipc_command(ipc, [
                    "playlist-play-index",
                    file_number
                ])
                ipc_command(ipc, ["set_property", "speed", 1])
                ipc_command(ipc, ["set_property", "time-pos", 0])
                ipc_command(ipc, ["set_property", "pause", "no"])

            if pos is not None and -3 < target - pos < 3:
                ipc_command(ipc, [
                    "set_property",
                    "speed",
                    clamp((target - pos) / 2 + 1, 0.5, 2)
                ])

            else:
                hr_seek = ipc_command(ipc, ["get_property", "hr-seek"])

                if hr_seek in (False, "no"):
                    ipc_command(ipc, ["set_property", "speed", 0.5])
                    ipc_command(ipc, ["set_property", "time-pos", target + 3])

                else:
                    ipc_command(ipc, ["set_property", "speed", 1])
                    ipc_command(ipc, ["set_property", "time-pos", target])

            ipc_command(ipc, ["set_property", "pause", "no"])

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
