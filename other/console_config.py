# -*- coding: utf-8 -*-
import sys, os
import locale
import time
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_starko.settings")
django.setup()

from dialog import Dialog
from mc.utils import modify_wifi, modify_network
from mc.utils.commands import multiple_execute_ssh

cur_setup = ["ifconfig eth0 | grep -w inet | awk '{print $2}'",
                 "ifconfig eth0 | grep mask | awk '{print $4}'",
                 "netstat -rn | grep eth0 | grep ^0.0.0.0 | awk '{print $2}'",
                 "hostname",
                 "ifconfig wlan0 | grep -w inet | awk '{print $2}'",
                 "ifconfig wlan0 | grep mask | awk '{print $4}'",
                 "netstat -rn | grep wlan0 | grep ^0.0.0.0 | awk '{print $2}'",
                 "grep -i nameserver /etc/resolv.conf | cut -d ' ' -f2 | sed -n 1p",
                 "grep -i nameserver /etc/resolv.conf | cut -d ' ' -f2 | sed -n 2p",
                 "grep -w '#eth_static_config' /etc/dhcpcd.conf",
                 "iwconfig wlan0 | grep ESSID | cut -d ':' -f2 | sed 's/\s*\"\s*//g'",
                 "grep -w '#wlan_static_config' /etc/dhcpcd.conf", ]

cur_setup_arr = multiple_execute_ssh('localhost', 'out', *cur_setup)

cur_ip = cur_setup_arr[0].replace('\n','')
cur_mask = cur_setup_arr[1].replace('\n','')
cur_gw = cur_setup_arr[2].replace('\n','')
cur_hostname = cur_setup_arr[3].replace('\n','')
wcur_ip = cur_setup_arr[4].replace('\n','')
wcur_mask = cur_setup_arr[5].replace('\n','')
wcur_gw = cur_setup_arr[6].replace('\n','')
cur_dns1 = cur_setup_arr[7].replace('\n','')
cur_dns2 = cur_setup_arr[8].replace('\n','')
eth_dhcp_status = cur_setup_arr[9].replace('\n','')
cur_wlan = cur_setup_arr[10].replace('\n','')

new_ip, new_mask, new_gateway, wnew_ip, wnew_mask, wnew_gateway = (None,)*6
eth_dhcp, wifi_dhcp = True, True

def clearquit():
  #os.system('clear')
  sys.exit(0)

# This is almost always a good thing to do at the beginning of your programs.
locale.setlocale(locale.LC_ALL, '')

d = Dialog(dialog="dialog")

button_names = {d.OK:     "OK",
                d.CANCEL: "Cancel",
                d.HELP:   "Help",
                d.EXTRA:  "Extra"}

code, tag = d.menu(u'''Current params ethernet (ip/mask/gateway):
{}/{}/{}

Wifi: {}
{}/{}/{}
'''.format(cur_ip, cur_mask, cur_gw, 'on SSID: '+cur_wlan if cur_wlan else 'off', wcur_ip, wcur_mask, wcur_gw),
                   choices=[('eth', u"setup ethernet"),
                            ("wifi", u"setup wifi")])

if code == d.ESC:
    d.msgbox("You got out of the menu by pressing the Escape key.")
else:
    if tag == 'eth':
        dcode, tag = d.menu(u'Turn on DHCP?',
        choices=[
            ('DHCP', u'auto address'),
            ('static', u'input static')
        ])
        if (dcode == d.CANCEL or dcode == d.ESC):
                clearquit()
        if tag == 'static':
            code, values = d.form(u'Specify addresses', [
                                    # title, row_1, column_1, field, row_1, column_20, field_length, input_length
                                    ('IP Address', 1, 1, cur_ip, 1, 20, 15, 15),
                                    # title, row_2, column_1, field, row_2, column_20, field_length, input_length
                                    ('Netmask', 2, 1, cur_mask, 2, 20, 15, 15),
                                    # title, row_3, column_1, field, row_3, column_20, field_length, input_length
                                    ('Gateway', 3, 1, cur_gw, 3, 20, 15, 15)
                                    ], width=70)
            if (code == d.CANCEL or code == d.ESC):
                clearquit()
            new_ip = values[0]
            new_mask = values[1]
            new_gateway = values[2]
            eth_dhcp = False
            
        mcode = d.msgbox(u"Apply params?")
        if (mcode == d.CANCEL or mcode == d.ESC):
            clearquit()
    elif tag == 'wifi':
        w_code, w_values = d.form(u'Specify network', [
                                    (u'Name (SSID)', 1, 1, '', 1, 20, 15, 15),
                                    (u'Password', 2, 1, '', 2, 20, 15, 15),
                                    ], width=70)
        if (w_code == d.CANCEL or w_code == d.ESC):
            clearquit()
        dcode, tag = d.menu(u'Turn on DHCP?',
        choices=[
            ('DHCP', u'auto address'),
            ('static', u'input static')
        ])
        if (dcode == d.CANCEL or dcode == d.ESC):
                clearquit()
        if tag == 'static':
            code, values = d.form(u'Specify addresses', [
                                    # title, row_1, column_1, field, row_1, column_20, field_length, input_length
                                    ('IP Address', 1, 1, wcur_ip, 1, 20, 15, 15),
                                    # title, row_2, column_1, field, row_2, column_20, field_length, input_length
                                    ('Netmask', 2, 1, wcur_mask, 2, 20, 15, 15),
                                    # title, row_3, column_1, field, row_3, column_20, field_length, input_length
                                    ('Gateway', 3, 1, wcur_gw, 3, 20, 15, 15)
                                    ], width=70)
            if (code == d.CANCEL or code == d.ESC):
                clearquit()
            wnew_ip = values[0]
            wnew_mask = values[1]
            wnew_gateway = values[2]
            wifi_dhcp = False
        mcode = d.msgbox(u"Apply params?")
        if (mcode == d.CANCEL or mcode == d.ESC):
            clearquit()
        modify_wifi(w_values[0], w_values[1])
    modify_network(new_ip, new_mask, new_gateway, None, None, wnew_ip, wnew_mask, wnew_gateway, eth_dhcp, wifi_dhcp)

#d.infobox("Bye bye...", width=0, height=0, title="This is the end")
#time.sleep(2)

sys.exit(0)
