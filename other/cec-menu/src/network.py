# -*- coding: utf-8 -*-
"""Классы и функции для работы с настройкой ethernet"""
import subprocess


DHCPCD_TEMPLATE = """# A sample configuration for dhcpcd.
# See dhcpcd.conf(5) for details.

# Allow users of this group to interact with dhcpcd via the control socket.
#controlgroup wheel

# Inform the DHCP server of our hostname for DDNS.
hostname

# Use the hardware address of the interface for the Client ID.
clientid
# or
# Use the same DUID + IAID as set in DHCPv6 for DHCPv4 ClientID as per RFC4361.
#duid

# Persist interface configuration when dhcpcd exits.
persistent

# Rapid commit support.
# Safe to enable by default because it requires the equivalent option set
# on the server to actually work.
option rapid_commit

# A list of options to request from the DHCP server.
option domain_name_servers, domain_name, domain_search, host_name
option classless_static_routes
# Most distributions have NTP support.
option ntp_servers
# Respect the network MTU.
# Some interface drivers reset when changing the MTU so disabled by default.
#option interface_mtu

# A ServerID is required by RFC2131.
require dhcp_server_identifier

# Generate Stable Private IPv6 Addresses instead of hardware based ones
slaac private

# A hook script is provided to lookup the hostname if not set by the DHCP
# server, but it should not be run by default.
nohook lookup-hostname

interface eth0
"""

DHCPCD_PATH = "/etc/dhcpcd.conf"
WPA_PATH = "/etc/wpa_supplicant/wpa_supplicant.conf"

IP_ETH = "ifconfig eth0 | grep -w inet | awk '{print $2}'"
MASK_ETH = "ifconfig eth0 | grep mask | awk '{print $4}'"
GATEWAY_ETH = "netstat -rn | grep eth0 | grep ^0.0.0.0 | awk '{print $2}'"
DHCP_ETH = "grep -w '#eth_static_config' /etc/dhcpcd.conf"

IP_WIFI = "ifconfig wlan0 | grep -w inet | awk '{print $2}'"
MASK_WIFI = "ifconfig wlan0 | grep mask | awk '{print $4}'"
GATEWAY_WIFI = "netstat -rn | grep wlan0 | grep ^0.0.0.0 | awk '{print $2}'"
DHCP_WIFI = "grep -w '#wlan_static_config' /etc/dhcpcd.conf"

SSID = "grep 'ssid=' /etc/wpa_supplicant/wpa_supplicant.conf | cut -d \\\" -f2"

DNS1 = "grep -i nameserver /etc/resolv.conf | cut -d ' ' -f2 | sed -n 1p"
DNS2 = "grep -i nameserver /etc/resolv.conf | cut -d ' ' -f2 | sed -n 2p"


def get_network_config(command):
    """Получаем текущую настройку сети полученной командой"""
    try:
        return subprocess.check_output(command, shell=True).decode("utf-8").strip()
    except subprocess.CalledProcessError:
        return ""


def get_ip_eth():
    """IP адрес ethernet"""
    return get_network_config(IP_ETH)


def get_mask_eth():
    """Маска подсети ethernet"""
    return get_network_config(MASK_ETH)


def get_gateway_eth():
    """Адрес шлюза ethernet"""
    return get_network_config(GATEWAY_ETH)


def get_dhcp_eth():
    """Статус DHCP ethernet"""
    return len(get_network_config(DHCP_ETH)) == 0


def get_ip_wifi():
    """IP адрес wifi"""
    return get_network_config(IP_WIFI)


def get_mask_wifi():
    """Маска подсети wifi"""
    return get_network_config(MASK_WIFI)


def get_gateway_wifi():
    """Адрес шлюза wifi"""
    return get_network_config(GATEWAY_WIFI)


def get_dhcp_wifi():
    """Статус dhcp wifi"""
    return len(get_network_config(DHCP_WIFI)) == 0


def get_ssid():
    """SSID текущей сети"""
    return get_network_config(SSID)


def get_dns1():
    """Первичный DNS сервер"""
    return get_network_config(DNS1)


def get_dns2():
    """Вторичный DNS сервер"""
    return get_network_config(DNS2)


class Connection(object):
    """Данные подключения"""
    def __init__(self, ip, mask, gateway, dhcp):
        self.ip = ip
        self.mask = mask
        self.gateway = gateway
        self.dhcp = dhcp


class NetworkData(object):
    """Хранит и возвращает в удобном формате настройки сети"""
    IP_ETH_NAME = u"IP-адрес eth"
    MASK_ETH_NAME = u"Маска подсети eth"
    GATEWAY_ETH_NAME = u"Адрес шлюза eth"
    DHCP_ETH_NAME = u"DHCP eth"

    IP_WIFI_NAME = u"IP-адрес wifi"
    MASK_WIFI_NAME = u"Маска подсети wifi"
    GATEWAY_WIFI_NAME = u"Адрес шлюза wifi"
    DHCP_WIFI_NAME = u"DHCP wifi"

    SSID_NAME = u"SSID сети"
    PSK_NAME = u"PSK сети"

    DNS1_NAME = u"Первичный DNS сервер"
    DNS2_NAME = u"Вторичный DNS сервер"

    def __init__(self):
        self._eth = Connection(
            get_ip_eth(),
            get_mask_eth(),
            get_gateway_eth(),
            get_dhcp_eth()
        )

        self._wifi = Connection(
            get_ip_wifi(),
            get_mask_wifi(),
            get_gateway_wifi(),
            get_dhcp_wifi()
        )

        self._ssid = get_ssid()
        self._psk = ""

        self._dns1 = get_dns1()
        self._dns2 = get_dns2()

    @property
    def ip_eth(self):
        """Геттер для IP eth"""
        return self._eth.ip

    @ip_eth.setter
    def ip_eth(self, value):
        """Сеттер для IP eth"""
        self._eth.ip = value

    @property
    def mask_eth(self):
        """Геттер для маски eth"""
        return self._eth.mask

    @mask_eth.setter
    def mask_eth(self, value):
        """Сеттер для маски eth"""
        self._eth.mask = value

    @property
    def gateway_eth(self):
        """Геттер для шлюза eth"""
        return self._eth.gateway

    @gateway_eth.setter
    def gateway_eth(self, value):
        """Сеттер для шлюза eth"""
        self._eth.gateway = value

    @property
    def dhcp_eth(self):
        """Геттер для dhcp eth"""
        return self._eth.dhcp

    @dhcp_eth.setter
    def dhcp_eth(self, value):
        """Сеттер для dhcp eth"""
        self._eth.dhcp = value

    @property
    def ip_wifi(self):
        """Геттер для IP wifi"""
        return self._wifi.ip

    @ip_wifi.setter
    def ip_wifi(self, value):
        """Сеттер для IP wifi"""
        self._wifi.ip = value

    @property
    def mask_wifi(self):
        """Геттер для маски wifi"""
        return self._wifi.mask

    @mask_wifi.setter
    def mask_wifi(self, value):
        """Сеттер для маски wifi"""
        self._wifi.mask = value

    @property
    def gateway_wifi(self):
        """Геттер для шлюза wifi"""
        return self._wifi.gateway

    @gateway_wifi.setter
    def gateway_wifi(self, value):
        """Сеттер для шлюза wifi"""
        self._wifi.gateway = value

    @property
    def dhcp_wifi(self):
        """Геттер для dhcp wifi"""
        return self._wifi.dhcp

    @dhcp_wifi.setter
    def dhcp_wifi(self, value):
        """Сеттер для dhcp wifi"""
        self._wifi.dhcp = value

    @property
    def ssid(self):
        """Геттер для ssid"""
        return self._ssid

    @ssid.setter
    def ssid(self, value):
        """Сеттер для ssid"""
        self._ssid = value

    @property
    def psk(self):
        """Геттер для psk"""
        return self._psk

    @psk.setter
    def psk(self, value):
        """Сеттер для psk"""
        self._psk = value

    @property
    def dns1(self):
        """Геттер для первичного DNS"""
        return self._dns1

    @dns1.setter
    def dns1(self, value):
        """Сеттер для первичного DNS"""
        self._dns1 = value

    @property
    def dns2(self):
        """Геттер для вторичного DNS"""
        return self._dns2

    @dns2.setter
    def dns2(self, value):
        """Сеттер для вторичного DNS"""
        self._dns2 = value

    def clear_eth(self):
        """Очищает все поля ethernet"""
        self._eth.ip = ""
        self._eth.mask = ""
        self._eth.gateway = ""
        self._eth.dhcp = True

    def clear_wifi(self):
        """Очищает все поля wifi"""
        self._wifi.ip = ""
        self._wifi.mask = ""
        self._wifi.gateway = ""
        self._wifi.dhcp = True

    def as_list_eth(self):
        """Возвращаем данные eth в виде форматированного листа"""
        eth_list = []

        eth_list.append(u"{}: {}".format(
            self.DHCP_ETH_NAME,
            "Вкл" if self._eth.dhcp else "Выкл"
        ))
        eth_list.append(u"{}: {}".format(
            self.IP_ETH_NAME,
            self._eth.ip
        ))
        eth_list.append(u"{}: {}".format(
            self.MASK_ETH_NAME,
            self._eth.mask
        ))
        eth_list.append(u"{}: {}".format(
            self.GATEWAY_ETH_NAME,
            self._eth.gateway
        ))
        eth_list.append(u"{}: {}".format(
            self.DNS1_NAME,
            self.dns1
        ))
        eth_list.append(u"{}: {}".format(
            self.DNS2_NAME,
            self.dns2
        ))

        return eth_list

    def as_list_wifi(self):
        """Возвращаем данные wifi в виде форматированного листа"""
        wifi_list = []

        wifi_list.append(u"{}: {}".format(
            self.DHCP_WIFI_NAME,
            "Вкл" if self._wifi.dhcp else "Выкл"
        ))
        wifi_list.append(u"{}: {}".format(
            self.SSID_NAME,
            self.ssid
        ))
        wifi_list.append(u"{}: {}".format(
            self.PSK_NAME,
            self.psk
        ))
        wifi_list.append(u"{}: {}".format(
            self.IP_WIFI_NAME,
            self._wifi.ip
        ))
        wifi_list.append(u"{}: {}".format(
            self.MASK_WIFI_NAME,
            self._wifi.mask
        ))
        wifi_list.append(u"{}: {}".format(
            self.GATEWAY_WIFI_NAME,
            self._wifi.gateway
        ))
        wifi_list.append(u"{}: {}".format(
            self.DNS1_NAME,
            self.dns1
        ))
        wifi_list.append(u"{}: {}".format(
            self.DNS2_NAME,
            self.dns2
        ))

        return wifi_list

    def _modify_wpa(self, working):
        """Выставляем настройки подключения к wifi"""
        if working:
            ssid = self._ssid
            psk = self._psk
        else:
            ssid = ""
            psk = ""

        wpa_string = [
            "network={\n",
            u"ssid=\"{}\"\n".format(ssid),
            "psk=\"{}\"\n".format(psk),
            "}\n"
        ]

        with open(WPA_PATH, "r") as wpa_file:
            wpa_data = list(wpa_file)

        for line in wpa_data:
            if "network={" in line:
                wpa_data = wpa_data[:-4]
                break

        wpa_data += wpa_string

        with open(WPA_PATH, "w") as wpa_file:
            wpa_file.writelines(wpa_data)

    def _modify_eth(self):
        """Дописываем данные eth"""
        eth = ""

        if self._eth.ip and not self._eth.dhcp:
            short_mask = sum(
                [bin(int(x)).count("1") for x in self._eth.mask.split(".")]
            )

            eth += "#eth_static_config\n"
            eth += "static ip_address={}/{}\n".format(
                self._eth.ip,
                short_mask
            )

            if self._eth.gateway:
                eth += "static routers={}\n".format(self._eth.gateway)

        return eth

    def _modify_wifi(self):
        """Дописываем данные wifi"""
        wifi = ""

        if self._wifi.ip and not self._wifi.dhcp:
            short_mask = sum(
                [bin(int(x)).count("1") for x in self._wifi.mask.split(".")]
            )

            wifi += "#wlan_static_config\n"
            wifi += "interface wlan0\n"
            wifi += "static ip_address={0}/{1}\n".format(
                self._wifi.ip,
                short_mask
            )

            if self._wifi.gateway:
                wifi += "static routers={}\n".format(self._wifi.gateway)

        return wifi

    def modify_network(self, wifi):
        """Сохраняем текущую структуру в файле"""
        self._modify_wpa(wifi)

        dhcpcd_conf = DHCPCD_TEMPLATE

        dhcpcd_conf += self._modify_eth()

        dhcpcd_conf += self._modify_wifi()

        dns_mask = "{} {}".format(self.dns1, self.dns2).strip()

        if dns_mask:
            dhcpcd_conf += "static domain_name_servers={}\n".format(dns_mask)

        with open(DHCPCD_PATH, "w") as dhcpcd_file:
            dhcpcd_file.write(dhcpcd_conf)
