"""
Пример скрипта для работы с mpv из других скриптов Python
"""

import json
import os
import socket


IPC_PATH = "/tmp/mpv-video"


def ipc_command(command: str, socket_file: str) -> str:
    """Отправляем команду в сокет"""
    if not os.path.exists(socket_file):
        raise FileNotFoundError("MPV is not started")

    try:
        ipc_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        ipc_sock.connect(socket_file)

        command += "\n"

        ipc_sock.sendall(command.encode("utf-8"))

        data = ipc_sock.recv(1024)

        return data.decode("utf-8")

    finally:
        ipc_sock.close()


def main():
    response = ipc_command(
        '{ "command": ["screenshot"], "request_id": 123, "async": true }',
        IPC_PATH
    )

    print(response)


if __name__ == "__main__":
    main()
