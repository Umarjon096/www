# -*- coding: utf-8 -*-
"""Читаем и обрабатываем вывод cec-client"""
import re
import subprocess


CEC_COMMAND = ["cec-client"]


def execute(cmd):
    """Вызываем команду и читаем из нее вывод"""
    popen = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        universal_newlines=True
    )

    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line

    popen.stdout.close()
    return_code = popen.wait()

    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


def listen_to_cec(func):
    """Вызываем функцию, если была отжата кнопка"""
    for line in execute(CEC_COMMAND):
        try:
            key = re.search("key released: .*? \((.+?)\)", line).group(1)
            func(int(key))

        except AttributeError:
            pass


def some_callback(key):
    """Функция для тестов"""
    print(key ** 2)


def main():
    """Главная"""
    listen_to_cec(some_callback)


if __name__ == "__main__":
    main()
