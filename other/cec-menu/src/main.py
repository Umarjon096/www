# -*- coding: utf-8 -*-
"""Набор скриптов для меню, управляемого клавиатурой и hdmi-cec"""
import os
import signal
import curses
import sys
import subprocess
import locale

from commands import Command, UP, DOWN, RIGHT, LEFT, ENTER, BACK
from time import sleep
from wifi import Cell

import keyboard

from network import NetworkData
from cec_custom import listen_to_cec
from curses_keyboard import Keyboard, WHITE_ON_BLUE, NUMERIC


PIDFILE = "/tmp/cec-menu.pid"

MAIN_ADDITIONAL = [
    {
        "y": 0,
        "x": 0,
        "value": " $$$$$$\\             $$\\"
    },
    {
        "y": 1,
        "x": 0,
        "value": "$$  __$$\\            $$ |"
    },
    {
        "y": 2,
        "x": 0,
        "value": "$$ /  $$ | $$$$$$\\ $$$$$$\\    $$$$$$\\   $$$$$$\\"
    },
    {
        "y": 3,
        "x": 0,
        "value": "$$ |  $$ |$$  __$$\\\\_$$  _|  $$  __$$\\ $$  __$$\\"
    },
    {
        "y": 4,
        "x": 0,
        "value": "$$ |  $$ |$$ /  $$ | $$ |    $$$$$$$$ |$$ /  $$ |"
    },
    {
        "y": 5,
        "x": 0,
        "value": "$$ |  $$ |$$ |  $$ | $$ |$$\\ $$   ____|$$ |  $$ |"
    },
    {
        "y": 6,
        "x": 0,
        "value": " $$$$$$  |$$$$$$$  | \\$$$$  |\\$$$$$$$\\ \\$$$$$$  |"
    },
    {
        "y": 7,
        "x": 0,
        "value": " \\______/ $$  ____/   \\____/  \\_______| \\______/"
    },
    {
        "y": 8,
        "x": 0,
        "value": "          $$ |"
    },
    {
        "y": 9,
        "x": 0,
        "value": "          $$ |"
    },
    {
        "y": 10,
        "x": 0,
        "value": "          \\__|    "
    }
]


class Option(object):
    """Выбираемые опции в окнах"""
    DELIMITER = " - "

    def __init__(self, name, action, additional=None):
        self._name = name
        self._action = action
        self._additional = additional

    @property
    def name(self):
        """Возвращаем имя с разделителем"""
        if self._additional is None:
            return self._name

        return self._name + self.DELIMITER + self._additional

    def add_to_name(self, value):
        """Заменяем дополнительную информацию"""
        self._additional = value

    def __len__(self):
        return len(self.name)

    def get(self):
        """Абстрактный метод для получения действия опции"""
        raise NotImplementedError

    def set_action(self, action):
        """Привязка действия после инициализации"""
        self._action = action


class OptionAction(Option):
    """Опция, в которой находится конкретное действие"""
    def get(self):
        """Вызываем заложенное действие"""
        try:
            return self._action()
        except AttributeError:
            return None


class OptionMenu(Option):
    """Опция, в которой находится следующее меню"""
    def get(self):
        """Вовзращает заложенное меню"""
        try:
            return self._action
        except AttributeError:
            return None


class Window(object):
    """Меню программы, на котором находятся опции"""
    DEFAULT_BACK = OptionMenu("Назад", BACK)

    def __init__(
            self,
            title,
            options,
            curses_ready,
            stdscr_ready,
            back=None,
            additional=None
    ):
        self.title = title
        self.options = options
        self.additional = additional

        if back is None:
            self.back_action = self.DEFAULT_BACK
        else:
            self.back_action = back

        self.options.append(self.back_action)

        self.curses = curses_ready
        self.stdscr = stdscr_ready

        self._active = 0

        self._init_dimensions()

    def _init_dimensions(self):
        """Задаем размеры окна"""
        self._height = len(self.options)
        self._width = max(map(len, self.options))

        self._start_y = int((self.curses.LINES - self._height) / 2)
        self._start_x = int((self.curses.COLS - self._width) / 2)

    @property
    def active(self):
        """Обертка для геттера"""
        return self._active

    @active.setter
    def active(self, value):
        value = int(value)

        if value < 0:
            value = 0

        elif value >= len(self.options):
            value = len(self.options) - 1

        self._active = value
        self._draw_self()

    def draw(self):
        """Публичный метод для отрисовки"""
        self._draw_self()

    def run(self, command):
        """Выполняет полученную команду"""
        if len(command) == 1:
            return

        return command.action(self)

    def up(self):
        """Переход к предыдущей опции"""
        self.active -= 1

    def down(self):
        """Переход к следующей опции"""
        self.active += 1

    def back(self):
        """Получена команда НАЗАД"""
        return BACK

    def enter(self):
        """Выполняем текущую опцию"""
        return self.options[self.active].get()

    def left(self):
        """Заглушка"""
        return None

    def right(self):
        """Заглушка"""
        return None

    def _draw_self(self):
        self.stdscr.clear()
        if self.additional:
            for string in self.additional:
                self.stdscr.addstr(
                    string["y"],
                    string["x"],
                    string["value"]
                )

        self.stdscr.addstr(
            self._start_y - 2,
            self._start_x,
            self.title
        )

        for i, option in enumerate(self.options[:-1]):
            self.stdscr.addstr(
                self._start_y + i,
                self._start_x,
                option.name,
                self.curses.color_pair(WHITE_ON_BLUE) if i == self._active else 0
            )

        self.stdscr.addstr(
            self._start_y + len(self.options),
            self._start_x,
            self.options[-1].name,
            self.curses.color_pair(WHITE_ON_BLUE) if len(self.options) - 1 == self._active else 0
        )

        self.stdscr.refresh()
        self.stdscr.clear()


class KeyboardWindow(Window):
    """Окно с экранной клавиатурой"""
    INPUT_MARGIN = 3

    def __init__(
            self,
            title,
            action,
            curses_ready,
            stdscr_ready,
            initial="",
            keyboard=None
    ):
        self.title = title
        self.curses = curses_ready
        self.stdscr = stdscr_ready
        self._action = action
        self._input = initial

        self.keyboard = Keyboard(
            self.curses,
            self.stdscr,
            keys=keyboard
        )

        self._init_dimensions()

        self.keyboard.set_start(
            self._start_y + self.INPUT_MARGIN,
            self._start_x
        )

    @property
    def window_input(self):
        """Получаем введенное значение"""
        return self._input

    def _init_dimensions(self):
        """Задаем размеры окна"""
        k_width, k_height = self.keyboard.size
        self._height = self.INPUT_MARGIN + k_height
        self._width = k_width

        self._start_y = int((self.curses.LINES - self._height) / 2)
        self._start_x = int((self.curses.COLS - self._width) / 2)

    def _draw_self(self):
        """Отрисовываем окно"""
        self.stdscr.clear()

        self.stdscr.addstr(
            self._start_y,
            int(self.curses.COLS / 2 - len(self.title) / 2),
            self.title
        )

        self.stdscr.addstr(
            self._start_y + 1,
            int(self.curses.COLS / 2 - len(self.title) / 2),
            self._input,
            self.curses.color_pair(WHITE_ON_BLUE)
        )

        self.keyboard.draw()

        self.stdscr.refresh()
        self.stdscr.clear()

    def run(self, command):
        """Выполняет полученную команду"""
        if len(command) == 1:
            if command in self.keyboard:
                self._input += command
            return

        else:
            output = self.keyboard.receive_command(command)

        if output is None:
            return

        if output == BACK:
            return output

        if len(output) == 1:
            self._input += output
            return

        if output == "backspace":
            self._input = self._input[:-1]
            return

        if output == "enter":
            return self._action(self._input)

        return output


class ConfirmWindow(Window):
    """Выводим все строки, подтверждение и выполняем функцию, если ок"""
    def __init__(
            self,
            title,
            for_check,
            action,
            curses_ready,
            stdscr_ready
    ):
        self.title = title

        if len(for_check) == 0:
            raise ValueError("Nothing to check")

        self._for_check = for_check

        self._action = action

        self.curses = curses_ready
        self.stdscr = stdscr_ready

        self.confirm = False

        self._init_dimensions()

    @property
    def for_check(self):
        """Получаем текущий список"""
        return self._for_check

    @for_check.setter
    def for_check(self, values):
        """Выставляем список снаружи"""
        if len(values) == 0:
            raise ValueError("Nothing to check")

        self._for_check = values

    def _init_dimensions(self):
        """Вычисляем размеры и начальную позицию окна"""
        self._width = max(max(map(len, self._for_check)), len(self.title))
        self._height = len(self._for_check) + 5

        self._start_y = int((self.curses.LINES - self._height) / 2)
        self._start_x = int((self.curses.COLS - self._width) / 2)

    def _draw_self(self):
        """Отрисовываем себя"""
        self.stdscr.clear()

        self.stdscr.addstr(
            self._start_y,
            self._start_x,
            self.title
        )

        for i, check in enumerate(self._for_check):
            self.stdscr.addstr(
                self._start_y + i + 2,
                self._start_x,
                check
            )

        self.stdscr.addstr(
            self._start_y + self._height,
            self._start_x,
            "Отмена",
            self.curses.color_pair(WHITE_ON_BLUE) if not self.confirm else 0
        )

        self.stdscr.addstr(
            self._start_y + self._height,
            self._start_x +self._width - 3,
            "Ок",
            self.curses.color_pair(WHITE_ON_BLUE) if self.confirm else 0
        )

        self.stdscr.refresh()
        self.stdscr.clear()

    def run(self, command):
        """Выполняем полученную команду"""
        if command in (LEFT, RIGHT):
            self.confirm = not self.confirm
            return None

        if command == ENTER:
            if self.confirm:
                return self._action()

            return BACK

        if command == BACK:
            return BACK

        return None


class App(object):
    """Хранит переходы между окнами и передает им команды"""
    DEFAULT_EXIT = sys.exit

    def __init__(
            self,
            window,
            back=None
    ):
        self.windows = [window]

        self.back = back or self.DEFAULT_EXIT

        window.draw()

    def receive_command(self, command):
        """Передает полученную команду текущему окну"""
        window = self.windows[-1]

        output = window.run(command)

        if output == BACK:
            self.windows.pop()
        elif output is not None:
            self.windows.append(output)

        if len(self.windows) == 0:
            self.back()
        else:
            self.windows[-1].draw()


def prepare_curses():
    """Инициализация curses"""
    screen = curses.initscr()
    screen.timeout(1000)
    curses.start_color()
    curses.curs_set(0)
    curses.init_pair(WHITE_ON_BLUE, curses.COLOR_BLUE, curses.COLOR_WHITE)
    return screen


def exit_loop():
    """Колбэк для выхода из бесконечного цикла"""
    os.kill(os.getpid(), signal.SIGINT)


# Коды можно подсмотреть в cectypes.h сырцов libcec
REMOTE_COMMANDS = {
    # Должно работать всегда
    0: ENTER,
    1: UP,
    2: DOWN,
    3: LEFT,
    4: RIGHT,

    # Поддержка цифр для клавиатур
    32: "0",
    33: "1",
    34: "2",
    35: "3",
    36: "4",
    37: "5",
    38: "6",
    39: "7",
    40: "8",
    41: "9",

    # Доп клавиши делают логичные действия
    13: BACK,
    43: ENTER,
}

KEYBOARD_COMMANDS = {
    "up": UP,
    "down": DOWN,
    "enter": ENTER,
    "left": LEFT,
    "right": RIGHT,
    "backspace": BACK
}


def remote_press(key_pressed, application):
    """Колбэк для libcec"""
    new_command = REMOTE_COMMANDS.get(key_pressed, None)

    if new_command is not None:
        application.receive_command(new_command)


def keyboard_press(event, application):
    """Колбэк для событий клавиатуры"""
    key = event.name

    if len(key) > 1:
        new_command = KEYBOARD_COMMANDS.get(key, None)
    else:
        new_command = key

    if new_command is not None:
        application.receive_command(new_command)


def clear_terminal_history():
    """Чистим историю, чтобы не нажать чего клавиатурой"""
    subprocess.call(["bash", "-c", "history -c"])


def resize_terminal(new_size="16x32"):
    """Меняем размер шрифта в терминале"""
    # Команда:
    # grep FONTSIZE /etc/default/console-setup | cut -d'"' -f 2
    old = subprocess.check_output(
        " ".join([
            "grep",
            "FONTSIZE",
            "/etc/default/console-setup",
            "|",
            "cut",
            "-d'\"'",
            "-f",
            "2"
        ]),
        shell=True
    )

    # Команда:
    # sed -i '/FONTSIZE/s/".*"/"16x32"/' /etc/default/console-setup
    # && /etc/init.d/console-setup.sh restart
    subprocess.check_output(
        " ".join([
            "sed",
            "-i",
            "'/FONTSIZE/s/\".*\"/\"" + new_size.strip() + "\"/'",
            "/etc/default/console-setup",
            "&&",
            "/etc/init.d/console-setup.sh",
            "restart"
        ]),
        shell=True
    )

    return old


def set_eth_option(
        output,
        struct,
        option,
        eth_window
):
    """Выставляем значение в структуре и возвращаемся назад"""
    setattr(struct, option, output)

    eth_window.for_check = struct.as_list()

    return BACK


def prepare_wifis():
    """Получаем список доступных сетей и упаковываем в список опций"""
    ap_list = []

    all_wifi = Cell.all("wlan0")

    for wifi_ap in all_wifi:
        if wifi_ap.encryption_type in ("wpa", "wpa2"):
            quality = 0
            try:
                raw_quality = list(map(float, wifi_ap.quality.split("/")))
                quality = int(raw_quality[0] / raw_quality[1] * 100)

            except (AttributeError, IndexError, ZeroDivisionError):
                quality = 0

            ap_list.append({"ssid": wifi_ap.ssid, "quality": quality})

    return sorted(ap_list, key=lambda ap: ap["quality"], reverse=True)


def set_ssid(ssid, network, option):
    """Устанавливаем сеть wifi"""
    network.ssid = ssid

    option.add_to_name(ssid)

    return BACK


def set_psk(psk, network, option):
    """Устанавливаем пароль для wifi"""
    network.psk = psk

    option.add_to_name("*" * len(psk))

    return BACK


def set_dns(value, network, option, primary):
    """Отображаем изменения в DNS"""
    if primary:
        network.dns1 = value
    else:
        network.dns2 = value

    option.add_to_name(value)

    return BACK


def set_static_config(value, method, network, option, wifi=False):
    """Отображаем изменения в опциях"""
    setattr(network, method, value)

    option.add_to_name(value)

    return BACK


def toggle_dhcp(option, network, wifi=False):
    """Тригерим DHCP"""
    if wifi:
        option.add_to_name("Выкл" if network.dhcp_wifi else "Вкл")
        network.dhcp_wifi = not network.dhcp_wifi

    else:
        option.add_to_name("Выкл" if network.dhcp_eth else "Вкл")
        network.dhcp_eth = not network.dhcp_eth


def modify_network(network, wifi):
    """Применяем настройки и выходим"""
    network.modify_network(wifi)
    exit_loop()


def confirm_eth(network):
    """Подтверждаем актуальные настройки eth"""
    return ConfirmWindow(
        u"Проверьте настройки соединения",
        network.as_list_eth(),
        lambda: modify_network(network, False),
        curses,
        stdscr
    )


def confirm_wifi(network):
    """Подтверждаем актуальные настройки wifi"""
    return ConfirmWindow(
        u"Проверьте настройки соединения",
        network.as_list_wifi(),
        lambda: modify_network(network, True),
        curses,
        stdscr
    )


def make_rw_fs():
    """Делаем файловую систему read-write или же падаем"""
    subprocess.check_output(["mount", "-o", "remount,rw", "/"])


def make_ro_fs():
    """Делаем файловую систему read-only"""
    subprocess.check_output(["mount", "-o", "remount,ro", "/"])


def get_ip():
    """Получаем текущий IP, если он есть"""
    current_ip = subprocess.check_output(
        "hostname -I",
        shell=True
    ).decode("utf-8").strip()

    return "IP: " + current_ip if current_ip else u"Нет подключения"


def create_pidfile():
    """Создаем PID файл, чтобы можно было отслеживать его работу"""
    pid = str(os.getpid())

    if os.path.isfile(PIDFILE):
        print("{} already exists, exiting.".format(PIDFILE))
        sys.exit(1)

    with open(PIDFILE, "w") as pidfile:
        pidfile.write(pid)


if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding("utf8")
    locale.resetlocale()
    make_rw_fs()

    create_pidfile()

    raw_wifi_list = prepare_wifis()

    clear_terminal_history()
    old_size = resize_terminal()

    stdscr = prepare_curses()

    MAIN_ADDITIONAL.append({
        "y": curses.LINES - 3,
        "x": 0,
        "value": get_ip()
    })

    network_data = NetworkData()

    wifi_ssid_option = OptionMenu(
        network_data.SSID_NAME,
        None,
        network_data.ssid
    )

    wifi_options_list = []

    for wifi_point in raw_wifi_list:
        wifi_options_list.append(OptionAction(
            wifi_point["ssid"] + " - " + str(wifi_point["quality"]) + "%",
            lambda ssid=wifi_point["ssid"]: set_ssid(
                ssid,
                network_data,
                wifi_ssid_option
            )
        ))

    if len(wifi_options_list) == 0:
        wifi_options_list.append(OptionMenu(u"Не найдено сетей WIFI", None))

    wifi_ssid_option.set_action(Window(
        u"Выберите wifi",
        wifi_options_list,
        curses,
        stdscr
    ))

    wifi_psk_option = OptionMenu(u"Пароль WIFI", None, "")

    wifi_psk_keyboard = KeyboardWindow(
        u"Введите пароль",
        lambda w_input: set_psk(w_input, network_data, wifi_psk_option),
        curses,
        stdscr
    )

    wifi_psk_option.set_action(wifi_psk_keyboard)

    wifi_dhcp_option = OptionAction(
        network_data.DHCP_WIFI_NAME,
        None,
        "Вкл" if network_data.dhcp_wifi else "Выкл"
    )

    wifi_ip_option = OptionMenu(
        network_data.IP_WIFI_NAME,
        None,
        network_data.ip_wifi
    )

    wifi_ip_keyboard = KeyboardWindow(
        network_data.IP_WIFI_NAME,
        lambda w_input: set_static_config(
            w_input,
            "ip_wifi",
            network_data,
            wifi_ip_option,
            True
        ),
        curses,
        stdscr,
        network_data.ip_wifi,
        NUMERIC
    )

    wifi_ip_option.set_action(wifi_ip_keyboard)

    wifi_mask_option = OptionMenu(
        network_data.MASK_WIFI_NAME,
        None,
        network_data.mask_wifi
    )

    wifi_mask_keyboard = KeyboardWindow(
        network_data.MASK_WIFI_NAME,
        lambda w_input: set_static_config(
            w_input,
            "mask_wifi",
            network_data,
            wifi_mask_option,
            True
        ),
        curses,
        stdscr,
        network_data.mask_wifi,
        NUMERIC
    )

    wifi_mask_option.set_action(wifi_mask_keyboard)

    wifi_gateway_option = OptionMenu(
        network_data.GATEWAY_WIFI_NAME,
        None,
        network_data.gateway_wifi
    )

    wifi_gateway_keyboard = KeyboardWindow(
        network_data.GATEWAY_WIFI_NAME,
        lambda w_input: set_static_config(
            w_input,
            "gateway_wifi",
            network_data,
            wifi_gateway_option,
            True
        ),
        curses,
        stdscr,
        network_data.gateway_wifi,
        NUMERIC
    )

    wifi_gateway_option.set_action(wifi_gateway_keyboard)

    wifi_dhcp_option.set_action(lambda: toggle_dhcp(
        wifi_dhcp_option,
        network_data,
        True
    ))

    dns1_option = OptionMenu(
        network_data.DNS1_NAME,
        None,
        network_data.dns1
    )

    dns1_keyboard = KeyboardWindow(
        network_data.DNS1_NAME,
        lambda w_input: set_dns(w_input, network_data, dns1_option, True),
        curses,
        stdscr,
        network_data.dns1,
        NUMERIC
    )

    dns1_option.set_action(dns1_keyboard)

    dns2_option = OptionMenu(
        network_data.DNS2_NAME,
        None,
        network_data.dns2
    )

    dns2_keyboard = KeyboardWindow(
        network_data.DNS2_NAME,
        lambda w_input: set_dns(w_input, network_data, dns2_option, False),
        curses,
        stdscr,
        network_data.dns2,
        NUMERIC
    )

    dns2_option.set_action(dns2_keyboard)

    confirm_wifi_option = OptionAction(
        u"Принять изменения",
        lambda: confirm_wifi(network_data)
    )

    wifi_options = [
        wifi_ssid_option,
        wifi_psk_option,
        wifi_dhcp_option,
        wifi_ip_option,
        wifi_mask_option,
        wifi_gateway_option,
        dns1_option,
        dns2_option,
        confirm_wifi_option
    ]

    eth_dhcp_option = OptionAction(
        network_data.DHCP_ETH_NAME,
        None,
        "Вкл" if network_data.dhcp_eth else "Выкл"
    )

    eth_ip_option = OptionMenu(
        network_data.IP_ETH_NAME,
        None,
        network_data.ip_eth
    )

    eth_ip_keyboard = KeyboardWindow(
        network_data.IP_ETH_NAME,
        lambda w_input: set_static_config(
            w_input,
            "ip_eth",
            network_data,
            eth_ip_option,
            True
        ),
        curses,
        stdscr,
        network_data.ip_eth,
        NUMERIC
    )

    eth_ip_option.set_action(eth_ip_keyboard)

    eth_mask_option = OptionMenu(
        network_data.MASK_ETH_NAME,
        None,
        network_data.mask_eth
    )

    eth_mask_keyboard = KeyboardWindow(
        network_data.MASK_ETH_NAME,
        lambda w_input: set_static_config(
            w_input,
            "mask_eth",
            network_data,
            eth_mask_option,
            True
        ),
        curses,
        stdscr,
        network_data.mask_eth,
        NUMERIC
    )

    eth_mask_option.set_action(eth_mask_keyboard)

    eth_gateway_option = OptionMenu(
        network_data.GATEWAY_ETH_NAME,
        None,
        network_data.gateway_eth
    )

    eth_gateway_keyboard = KeyboardWindow(
        network_data.GATEWAY_ETH_NAME,
        lambda w_input: set_static_config(
            w_input,
            "gateway_eth",
            network_data,
            eth_gateway_option,
            True
        ),
        curses,
        stdscr,
        network_data.gateway_eth,
        NUMERIC
    )

    eth_gateway_option.set_action(eth_gateway_keyboard)

    eth_dhcp_option.set_action(lambda: toggle_dhcp(
        eth_dhcp_option,
        network_data,
        False
    ))

    confirm_eth_option = OptionAction(
        u"Принять изменения",
        lambda: confirm_eth(network_data)
    )

    eth_options = [
        eth_dhcp_option,
        eth_ip_option,
        eth_mask_option,
        eth_gateway_option,
        dns1_option,
        dns2_option,
        confirm_eth_option
    ]

    wifi_menu = Window(
        u"Укажите параметры беспроводного соединения",
        wifi_options,
        curses,
        stdscr
    )

    eth_menu = Window(
        u"Укажите параметры проводного соединения",
        eth_options,
        curses,
        stdscr
    )

    main_options = [
        OptionMenu(u"Беспроводное соединение", wifi_menu),
        OptionMenu(u"Проводное соединение", eth_menu)
    ]

    main_menu = Window(
        u"Подключиться к сети",
        main_options,
        curses,
        stdscr,
        OptionMenu("Выход", BACK),
        MAIN_ADDITIONAL
    )

    try:
        app = App(main_menu, back=exit_loop)

        # Замалчиваем, если клавиатура не подключена
        try:
            keyboard.on_release(lambda event: keyboard_press(
                event,
                app
            ))
        except:
            pass

        listen_to_cec(lambda key: remote_press(key, app))

    except KeyboardInterrupt:
        pass

    finally:
        clear_terminal_history()
        curses.endwin()
        resize_terminal(old_size)
        os.system("clear")
        os.unlink(PIDFILE)
        sleep(1)
        subprocess.check_output(["reboot"])
