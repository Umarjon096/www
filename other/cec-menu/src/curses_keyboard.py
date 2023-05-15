# -*- coding: utf-8 -*-
"""Клавиатура, работающая в curses"""
from commands import Command, BACK, LEFT, RIGHT, UP, DOWN, ENTER


WHITE_ON_BLUE = 1


class Pos(object):
    """Позиция клавиши"""
    def __init__(self, pos_y, pos_x):
        self._pos_y = pos_y
        self._pos_x = pos_x

    @property
    def pos_y(self):
        """Геттер для позиции"""
        return self._pos_y

    @property
    def pos_x(self):
        """Геттер для позиции"""
        return self._pos_x

    def __eq__(self, other):
        return self.pos_y == other.pos_y and self.pos_x == other.pos_x


class Key(object):
    """Клавиша клавиатуры"""
    def __init__(
            self,
            pos,
            values,
            length=1,
            action=None
    ):
        self.pos = pos

        if len(values) == 1:
            self.values = [values[0], values[0], values[0], values[0]]

        elif len(values) == 2:
            self.values = [values[0], values[1], values[0], values[1]]

        elif len(values) == 3:
            self.values = [values[0], values[1], values[0], values[2]]

        elif len(values) == 4:
            self.values = values

        else:
            raise ValueError("Too many values")

        self.length = length
        self.values = list(map(lambda x: x.ljust(length), self.values))

        self.action = action

    def click(self, state):
        """Возвращает клавишу в завимиости от состояния"""
        return self.action or self.values[state]

    def draw(self, start, state, curses, stdscr, active):
        """Отрисовываем клавишу в зависимости от состояния"""
        stdscr.addstr(
            start.pos_y + self.pos.pos_y,
            start.pos_x + self.pos.pos_x,
            self.values[state],
            curses.color_pair(WHITE_ON_BLUE) if active else 0
        )

    def __contains__(self, item):
        """Перегружаем оператор in"""
        if self.action is not None:
            return False

        for val in self.values:
            if val == item:
                return True

        return False


QWERTY = [
    [
        Key(Pos(0, 3), ["`", "~", u"ё", u"Ё"]),
        Key(Pos(0, 5), ["1", "!"]),
        Key(Pos(0, 7), ["2", "@", "\""]),
        Key(Pos(0, 9), ["3", "#", "№"]),
        Key(Pos(0, 11), ["4", "$", ""]),
        Key(Pos(0, 13), ["5", "%"]),
        Key(Pos(0, 15), ["6", "^", ":"]),
        Key(Pos(0, 17), ["7", "&", "?"]),
        Key(Pos(0, 19), ["8", "*"]),
        Key(Pos(0, 21), ["9", "("]),
        Key(Pos(0, 23), ["0", ")"]),
        Key(Pos(0, 25), ["-", "_"]),
        Key(Pos(0, 27), ["=", "+"]),
        Key(Pos(0, 29), ["<-"], length=2, action="backspace")
    ],
    [
        Key(Pos(2, 0), [u"Рус", u"Рус", "Eng", "Eng"], length=4, action="lang"),
        Key(Pos(2, 5), ["q", "Q", u"й", u"Й"]),
        Key(Pos(2, 7), ["w", "W", u"ц", u"Ц"]),
        Key(Pos(2, 9), ["e", "E", u"у", u"У"]),
        Key(Pos(2, 11), ["r", "R", u"к", u"К"]),
        Key(Pos(2, 13), ["t", "T", u"е", u"Е"]),
        Key(Pos(2, 15), ["y", "Y", u"н", u"Н"]),
        Key(Pos(2, 17), ["u", "U", u"г", u"Г"]),
        Key(Pos(2, 19), ["i", "I", u"ш", u"Ш"]),
        Key(Pos(2, 21), ["o", "O", u"щ", u"Щ"]),
        Key(Pos(2, 23), ["p", "P", u"з", u"З"]),
        Key(Pos(2, 25), ["[", "{", u"х", u"Х"]),
        Key(Pos(2, 27), ["]", "}", u"ъ", u"Ъ"]),
        Key(Pos(2, 29), ["\\", "|", "/"])
    ],
    [
        Key(Pos(4, 0), ["Caps"], length=4, action="caps"),
        Key(Pos(4, 5), ["a", "A", u"ф", u"Ф"]),
        Key(Pos(4, 7), ["s", "S", u"ы", u"Ы"]),
        Key(Pos(4, 9), ["d", "D", u"в", u"В"]),
        Key(Pos(4, 11), ["f", "F", u"а", u"А"]),
        Key(Pos(4, 13), ["g", "G", u"п", u"П"]),
        Key(Pos(4, 15), ["h", "H", u"р", u"Р"]),
        Key(Pos(4, 17), ["j", "J", u"о", u"О"]),
        Key(Pos(4, 19), ["k", "K", u"л", u"Л"]),
        Key(Pos(4, 21), ["l", "L", u"д", u"Д"]),
        Key(Pos(4, 23), [";", ":", u"ж", u"Ж"]),
        Key(Pos(4, 25), ["'", "\"", u"э", u"Э"]),
        Key(Pos(4, 27), ["Enter"], length=5, action="enter"),
    ],
    [
        Key(Pos(6, 0), ["Shift"], length=5, action="shift"),
        Key(Pos(6, 6), ["z", "Z", u"я", u"Я"]),
        Key(Pos(6, 8), ["x", "X", u"ч", u"Ч"]),
        Key(Pos(6, 10), ["c", "C", u"с", u"С"]),
        Key(Pos(6, 12), ["v", "V", u"м", u"М"]),
        Key(Pos(6, 14), ["b", "B", u"и", u"И"]),
        Key(Pos(6, 16), ["n", "N", u"т", u"Т"]),
        Key(Pos(6, 18), ["m", "M", u"ь", u"Ь"]),
        Key(Pos(6, 20), [",", "<", u"б", u"Б"]),
        Key(Pos(6, 22), [".", ">", u"ю", u"Ю"]),
        Key(Pos(6, 24), ["/", "?", ".", ","]),
        Key(Pos(6, 26), ["Shift"], length=5, action="shift"),
    ],
    [
        Key(Pos(8, 13), ["Space", u"Пробел"], length=6, action="space")
    ],
    [
        Key(Pos(10, 0), ["Назад"], length=5, action="back"),
        Key(Pos(10, 26), [u"Ок"], length=5, action="enter")
    ]
]

NUMERIC = [
    [
        Key(Pos(0, 5), ["1"]),
        Key(Pos(0, 7), ["2"]),
        Key(Pos(0, 9), ["3"])
    ],
    [
        Key(Pos(2, 5), ["4"]),
        Key(Pos(2, 7), ["5"]),
        Key(Pos(2, 9), ["6"])
    ],
    [
        Key(Pos(4, 5), ["7"]),
        Key(Pos(4, 7), ["8"]),
        Key(Pos(4, 9), ["9"])
    ],
    [
        Key(Pos(6, 5), ["."]),
        Key(Pos(6, 7), ["0"]),
        Key(Pos(6, 9), ["<-"], length=2, action="backspace")
    ],
    [
        Key(Pos(8, 0), [u"Назад"], length=5, action="back"),
        Key(Pos(8, 11), [u"Ок"], length=2, action="enter")
    ]
]


class Keyboard(object):
    """Экранная клавиатура"""
    def __init__(
            self,
            curses_ready,
            stdscr_ready,
            start=None,
            keys=None
    ):
        if keys is None:
            self.keys = QWERTY
        else:
            self.keys = keys

        self.start = start

        self.curses = curses_ready
        self.stdscr = stdscr_ready

        self.active = self.keys[0][0]

        self._rus = False
        self._shift = False
        self._caps = False

        self.commands = {
            UP: self._up,
            DOWN: self._down,
            RIGHT: self._right,
            LEFT: self._left,
            ENTER: self._press,
            BACK: self._backspace
        }

        self.specials = {
            "backspace": self._backspace,
            "lang": self._lang,
            "caps": self._caps_press,
            "enter": self._enter,
            "shift": self._shift_press,
            "space": self._space,
            "back": self._back
        }

    def set_start(self, start_y, start_x):
        """Выставляем начальное значение, если не выставили сразу"""
        self.start = Pos(start_y, start_x)

    @property
    def state(self):
        """Состояние клавиатуры"""
        state = 0

        if self._rus:
            state += 2

        if self._shift ^ self._caps:
            state += 1

        return state

    @property
    def size(self):
        """Возвращает ширину и высоту"""
        width = 0

        for row in self.keys:
            current = row[-1]
            if current.pos.pos_x + current.length > width:
                width = current.pos.pos_x + current.length

        height = self.keys[-1][0].pos.pos_y

        return (width, height)

    def draw(self):
        """Публичный метод для отрисовки"""
        self._draw_self()

    def _draw_self(self):
        """Отрисовываем все клавиши"""
        for line in self.keys:
            for key in line:
                key.draw(
                    self.start,
                    self.state,
                    self.curses,
                    self.stdscr,
                    self.active.pos == key.pos
                )

    def receive_command(self, command):
        """Получаем команды для клавиатуры"""
        if command in self.commands:
            return self.commands[command]()

        return None

    def _dist_x(self, key):
        """Считаем расстояние по оси x до клавиши"""
        return abs(key.pos.pos_x - self.active.pos.pos_x)

    def _closest_x(self, row):
        """Находим ближайшую по оси x"""
        closest = row[0]
        closest_dist = self._dist_x(closest)

        for key in row:
            if closest_dist == 0:
                break

            dist = self._dist_x(key)

            if dist <= closest_dist:
                closest = key
                closest_dist = dist
            else:
                break

        return closest

    def _current(self):
        """Находим текущую строку активной клавиши"""
        for i, line in enumerate(self.keys):
            if self.active in line:
                return i

        raise KeyError("Can't find active row")

    def _up(self):
        """Двигаем курсор вверх"""
        current = self._current()

        if current <= 0:
            return

        top = self.keys[current - 1]

        self.active = self._closest_x(top)

    def _down(self):
        """Двигаем курсор вниз"""
        current = self._current()

        if current + 1 >= len(self.keys):
            return

        bottom = self.keys[current + 1]

        self.active = self._closest_x(bottom)

    def _left(self):
        """Двигаем курсор влево"""
        row = self.keys[self._current()]

        index = row.index(self.active)

        if index <= 0:
            return

        self.active = row[index - 1]

    def _right(self):
        """Двигаем курсор вправо"""
        row = self.keys[self._current()]

        index = row.index(self.active)

        if index + 1 >= len(row):
            return

        self.active = row[index + 1]

    def _press(self):
        """Кликаем по клавише"""
        output = self.active.click(self.state)

        if len(output) == 1:
            if self._shift:
                self._shift = False

            return output

        return self.specials[output]()

    def _backspace(self):
        """Клавиша backspace"""
        return "backspace"

    def _lang(self):
        """Меняем язык"""
        self._rus = not self._rus

    def _caps_press(self):
        """Нажимаем Caps Lock"""
        self._caps = not self._caps

    def _enter(self):
        """Нажимаем enter (надо ли?)"""
        return "enter"

    def _shift_press(self):
        """Нажимаем Shift"""
        self._shift = not self._shift

    def _space(self):
        """Нажимаем пробел"""
        return " "

    def _back(self):
        """Возвращаемся назад"""
        return BACK

    def __contains__(self, item):
        """Перегружаем оператор in"""
        for line in self.keys:
            for key in line:
                if item in key:
                    return True

        return False
