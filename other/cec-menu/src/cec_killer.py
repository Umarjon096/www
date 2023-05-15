# -*- coding: utf-8 -*-
"""Демон, слушающий CEC, который убивает необходимый процесс"""
import datetime
import os
import signal
import subprocess
import sys

from cec_custom import listen_to_cec


# Если интервал нажатия меньше TIME_DELTA секунд,
# то запомним это
TIME_DELTA = 10

# Будем реагировать на ОК
KEY_CODE = 0

PROCESS_NAME = "mpv info-beamer starko-beamer"
PID_FILE = "/tmp/cec-menu.pid"


def kill_info_beamer(key, keys_pressed):
    """Засекаем 3 нажатия и убиваем mpv"""

    # Реагируем только на KEY_CODE
    if key != KEY_CODE:
        return

    now = datetime.datetime.now()

    if len(keys_pressed) > 0:
        if (now - keys_pressed[-1]).total_seconds() <= TIME_DELTA:
            keys_pressed.append(now)

            if len(keys_pressed) == 3:
                try:
                    subprocess.check_output(" ".join([
                        "killall",
                        PROCESS_NAME
                    ]), shell=True)

                finally:
                    sys.exit()

            else:
                return

    keys_pressed[:] = [now]


def main():
    """Главная"""
    # Список, в который будем заносить все нажатия
    key_presses = []

    # Удаляем PID файл, если он почему-то остался
    try:
        os.remove(PID_FILE)
    except OSError:
        pass

    try:
        listen_to_cec(lambda key: kill_info_beamer(key, key_presses))
        while True:
            pass

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
