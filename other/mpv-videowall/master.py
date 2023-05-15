#!/usr/bin/env python3

import logging
import socket
import struct
import sys
import time
import os
import json

from datetime import datetime

from typing import List, Tuple


def broadcast_pos(
        sock: socket.socket,
        pos: float,
        clients: List[Tuple[str, int]]
) -> List[int]:
    data = struct.pack('!d', pos)
    sent = []
    for client in clients:
        sent.append(sock.sendto(data, client))
    for client, written in zip(clients, sent):
        if written != 8:
            logging.error("Cannot send to '%s:%d'" % client)
    return sent


def get_current_length(playlists: List[dict]) -> int:
    """Получаем длину текущего плейлиста"""
    now = datetime.now()

    for pl in sorted(playlists, key=lambda pl: pl["start"]):
        if now >= pl["start"]:
            return pl["length"]


MASTER_PLAYLIST = "/var/starko/vw_master_pl"


def main(argv: List[str]) -> int:
    logging.basicConfig(level=logging.INFO)

    pid = str(os.getpid())

    pid_file = "/tmp/master-{}.pid".format(pid)

    with open(pid_file, "w") as pidfile:
        pidfile.write(pid)

    clients = None
    playlists = None

    if os.path.isfile(MASTER_PLAYLIST):
        with open(MASTER_PLAYLIST, "r") as master_pl:
            data = json.load(master_pl)
            clients = [(addr, 4444) for addr in data["ips"]]
            playlists = [
                {
                    "start": datetime.strptime(pl["start"], "%H:%M"),
                    "length": pl["length"]
                } for pl in data["pls"]
            ]

    length = get_current_length(playlists)

    # for addr, port in zip(argv[2::2], argv[3::2]):
    #     logging.info("Adding client '%s:%s'" % (addr, port))
    #     clients.append((addr, int(port)))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    try:
        while True:  # Loop playback
            length = get_current_length(playlists)
            start_time = time.monotonic()
            pos = 0
            broadcast_pos(sock, 0, clients)
            logging.info('Position: 0.000000000')
            timer = 0
            while pos < length:
                time.sleep(1)
                pos = time.monotonic() - start_time
                broadcast_pos(sock, pos, clients)
                logging.info('Position: %.9f' % pos)

                if timer >= 60:
                    length = get_current_length(playlists)
                    timer = 0
                else:
                    timer += 1

    finally:
        os.unlink(pid_file)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
