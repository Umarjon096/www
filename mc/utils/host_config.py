# -*- coding: utf-8 -*-
from datetime import datetime
from django.core import serializers
#from django.db.models.loading import apps.get_model
from django.apps import apps
import os
from django_starko.settings import STATIC_ROOT
from mc.utils.commands import execute_ssh, rw_execute_ssh


def modify_hostname(new_hostname):
    host_file_path = os.path.join(STATIC_ROOT, 'mc/bashes/hostname')
    with open(host_file_path, "w") as myfile:
        myfile.write('{0}\n'.format(new_hostname))

    cp_cmd = 'cp {0} /etc/hostname'.format(host_file_path)
    err = rw_execute_ssh('localhost', 'err', cp_cmd, '/etc/init.d/hostname.sh')
    return err

def set_nameservers():
    ns_file_path = os.path.join(STATIC_ROOT, 'mc/bashes/scripts/resolv.conf')
    cp_cmd = 'cp {0} /etc/resolv.conf'.format(ns_file_path)
    err = execute_ssh('localhost', cp_cmd)
    return err

def modify_time(time, new_format=False):
    # Добавил новый параметр для обратной совместимости
    if new_format:
        utime = datetime.strptime(time, "%Y-%m-%d %H:%M")
    else:
        utime = datetime.strptime(time, "%d.%m.%Y %H:%M")
    utime = utime.strftime('%Y%m%d %T')
    chng_cmd = u"date +%Y%m%d%T -s '{0}' && hwclock -w".format(utime)
    res = execute_ssh(
        "localhost",
        chng_cmd,
        type_of_return="out"
    ).replace("\n","")
    readable_res = datetime.strptime(
        res,
        "%Y%m%d%H:%M:%S"
    ).strftime("%d.%m.%Y %H:%M")
    return readable_res

def modify_network(
    ip='',
    mask='',
    gateway='',
    dns1=None,
    dns2=None,
    wip='',
    wmask='',
    wgateway='',
    eth_dhcp=False,
    wifi_dhcp=False,
    wifi_enabled=False
):
    network_tmpl_path = os.path.join(STATIC_ROOT, 'mc/bashes/scripts/dhcpcd_tmpl')
    network_path = os.path.join(STATIC_ROOT, 'mc/bashes/dhcpcd.conf')
    interfaces_tmpl_path = os.path.join(STATIC_ROOT, 'mc/bashes/scripts/interfaces_tmpl')
    interfaces_path = os.path.join(STATIC_ROOT, 'mc/bashes/interfaces')
    cp_cmd = 'cp {0} {1}'.format(network_tmpl_path, network_path)
    cp_cmd_2 = 'cp {0} {1}'.format(interfaces_tmpl_path, interfaces_path)
    err = rw_execute_ssh('localhost', 'err', cp_cmd, 'chmod 777 {0}'.format(network_path), cp_cmd_2, 'chmod 777 {0}'.format(interfaces_path))
    

    dns_mask = "{0}".format(dns1) if dns1 else ""
    if dns1 and dns2:
        dns_mask += " "
    dns_mask += ("{0}".format(dns2) if dns2 else "")
    
    with open(network_path, "a") as myfile:
        if ip and not eth_dhcp:
            short_mask = sum([bin(int(x)).count('1') for x in mask.split('.')])
            myfile.write('#eth_static_config\n')
            myfile.write('interface eth0\n')
            myfile.write('static ip_address={0}/{1}\n'.format(ip, short_mask))
            if gateway:
                myfile.write('static routers={0}\n'.format(gateway))
            if dns_mask:
                myfile.write('static domain_name_servers={0}\n'.format(dns_mask))

        if wifi_enabled and wip and not wifi_dhcp:
            wshort_mask = sum([bin(int(x)).count('1') for x in wmask.split('.')])
            myfile.write('#wlan_static_config\n')
            myfile.write('interface wlan0\n')
            myfile.write('static ip_address={0}/{1}\n'.format(wip, wshort_mask))
            if wgateway:
                myfile.write('static routers={0}\n'.format(wgateway))
            if dns_mask:
                myfile.write('static domain_name_servers={0}\n'.format(dns_mask))


    # with open(interfaces_path, "a") as myfile:
    #     if eth_dhcp:
    #         myfile.write('auto eth0\n')
    #         myfile.write('iface eth0 inet dhcp\n')
    #     if ip and not eth_dhcp:
    #         myfile.write('#eth_static_config\n')
    #         myfile.write('auto eth0\n')
    #         myfile.write('iface eth0 inet static\n')
    #         myfile.write('address {0}\n'.format(ip))
    #         myfile.write('netmask {0}\n'.format(mask))
    #         if gateway:
    #             myfile.write('gateway {0}\n'.format(gateway))
    #         if dns_mask:
    #             myfile.write('dns-nameservers {0}\n'.format(dns_mask))
    #     if wifi_dhcp or not wifi_enabled:
    #         myfile.write('auto wlan0\n')
    #         myfile.write('iface wlan0 inet dhcp\n')
    #         if wifi_enabled:
    #             myfile.write('    wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf\n')
    #     if wip and not wifi_dhcp and wifi_enabled:
    #         myfile.write('#wlan_static_config\n')
    #         myfile.write('auto wlan0\n')
    #         myfile.write('iface wlan0 inet manual\n')
    #         myfile.write('    wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf\n')
    #         myfile.write('address {0}\n'.format(wip))
    #         myfile.write('netmask {0}\n'.format(wmask))
    #         if gateway:
    #             myfile.write('gateway {0}\n'.format(wgateway))
    #         if dns_mask:
    #             myfile.write('dns-nameservers {0}\n'.format(dns_mask))


    cp_cmd = 'cp {0} /etc/dhcpcd.conf'.format(network_path)
    cp_cmd_2 = 'cp {0} /etc/network/interfaces'.format(interfaces_path)
    err += rw_execute_ssh('localhost', 'err', cp_cmd, cp_cmd_2, 'reboot')

    return err

def modify_wifi(wnew_ssid="", wnew_psk=""):
    from mc.utils.wpa import SchemeWPA
    all_wifis = SchemeWPA.all()
    for wifi in all_wifis:
        wifi.delete()
    if wnew_ssid:
        scheme = SchemeWPA('wlan0', wnew_ssid, {"ssid": wnew_ssid, "psk": wnew_psk})
        scheme.save()
    cp_cmd = 'cp {0} /etc/wpa_supplicant/wpa_supplicant.conf'.format(
        os.path.join(STATIC_ROOT, 'mc/bashes/scripts/wpa_supplicant.conf'))
    err = rw_execute_ssh('localhost', 'err', cp_cmd)

def create_conf_backup():
    global_conf = {}
    models_dict = {}
    dump_models = [
        'Host', 'vWallPixel', 'Monitor', 'Setting', 'SyncSchedule', 'SyncScheduleOption', 'Blackout'
    ]

    for rec in dump_models:
        model = apps.get_model('mc', rec)
        data = serializers.serialize("json", model.objects.all())
        models_dict[rec] = data

    user_model = apps.get_model('auth', 'User')
    user_data = serializers.serialize("json", user_model.objects.all())
    models_dict['User'] = user_data

    global_conf['models'] = models_dict

    cur_ip = execute_ssh('localhost',"ifconfig eth0 | grep inet | awk '{print $2}' | cut -d ':' -f2", 'out')
    cur_mask = execute_ssh('localhost',"ifconfig eth0 | grep Mask | awk '{print $4}' | cut -d ':' -f2", 'out')
    cur_gateway = execute_ssh('localhost',"netstat -rn | grep ^0.0.0.0 | awk '{print $2}'", 'out')
    cur_hostname = execute_ssh('localhost','hostname', 'out')

    dnses = execute_ssh('localhost', "cat /etc/resolv.conf |grep -i nameserver|cut -d ' ' -f2", 'out')
    dnses_arr = dnses.split('\n')
    dnses_len = len(dnses_arr)
    dns1 = dnses_arr[0] if dnses_len > 0 else None
    dns2 = dnses_arr[1] if dnses_len > 1 else None

    global_conf['network'] = {
       'ip': cur_ip.split('\n')[0],
       'mask': cur_mask.split('\n')[0],
       'gateway': cur_gateway.split('\n')[0],
       'hostname': cur_hostname,
       'dns1': dns1,
       'dns2': dns2
    }

    return global_conf

def reload_conf(conf_obj):
    network_settings = conf_obj['network']

    models = conf_obj['models']
    hosts = models['Host']

    host_model = apps.get_model('mc', 'Host')
    host_model.objects.all().delete()
    for deserialized_object in serializers.deserialize("json", hosts):
        deserialized_object.save()

    for model in models:
        if model != 'Host' and model != 'User':
            real_model = apps.get_model('mc', model)
            real_model.objects.all().delete()
            for deserialized_object in serializers.deserialize("json", models[model]):
                deserialized_object.save()
        if model == 'User':
            real_model = apps.get_model('auth', model)
            real_model.objects.all().delete()
            for deserialized_object in serializers.deserialize("json", models[model]):
                deserialized_object.save()

    modify_hostname(network_settings['hostname'])
    modify_network(network_settings['ip'], network_settings['mask'], network_settings['gateway'], network_settings.get('dns1'), network_settings.get('dns2'))