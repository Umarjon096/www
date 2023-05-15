# CEC-MENU

Менюшка, принимающая ввод по hdmi-cec и от клавиатуры для первичной настройки RPi

## Зависимости

* Python 2.7

* cec-client

## Установка

```text
apt install cec-utils
pip install -r requirements.txt
```

Также для корректной работы нужно, чтобы в терминале был шрифт, поддерживающий кириллицу. (и возможно, чтобы локаль поддерживала юникод).

## Запуск

Без sudo не работает модуль keyboard.

```text
sudo python ./main.py
```
