# -*- coding: utf-8 -*-
"""Универсальные команды для управления окнами"""
class Command(object):
    """Команды для окон"""
    def __init__(self, method):
        self._method = method

    def action(self, caller):
        """Вызывает встроенный метод у вызывателя"""
        return getattr(caller, self._method)()

    def __len__(self):
        """Перегружаем метод len"""
        return len(self._method)


UP = Command("up")
DOWN = Command("down")
LEFT = Command("left")
RIGHT = Command("right")
BACK = Command("back")
ENTER = Command("enter")
