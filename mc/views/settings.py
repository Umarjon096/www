# -*- coding: utf-8 -*-
import logging
from django.core.validators import URLValidator, RegexValidator
from django.utils.timezone import localtime

import csv
import json
import pytz
import os
import re
from datetime import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.forms import Select


from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from django.template.response import TemplateResponse
from django.shortcuts import render, redirect
from transliterate import translit

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from wifi import Cell

from django_starko.settings import MEDIA_ROOT, MEDIA_URL, MC_PATCH_FOLDER, BASE_DIR, ALLOWED_TZS

from mc.models import Host, Monitor, Setting, SavedUrl, HostDiagState, SyncScheduleOption, SyncStateArchive, RebootsData
from mc.utils import execute_ssh, modify_time, add_memory_data_to_context, \
    modify_hostname, modify_network, get_uuid, get_logo, get_device_model, \
    delete_folder_files, get_mon_res, create_conf_backup, get_version, \
    reload_conf, apply_all_hosts_blackout, get_key_and_licences, write_key, send_diag_request, all_hosts_reboot, \
    get_ntp_srvrs, set_ntp_srvrs, get_key, key_check_uuid, modify_wifi, diagnose_all_hosts, patch_peasants, BytestringEncoder
from mc.utils.wpa import SchemeWPA
from mc.utils import multiple_execute_ssh
from mc.utils.settings import is_updating

logger = logging.getLogger(__name__)

from datetime import datetime

def su_test(u):
    return u.is_superuser


@user_passes_test(su_test, login_url="login")
@login_required
@add_memory_data_to_context
def admin_page(request):
    return TemplateResponse(request, "mc/admin.html")


@user_passes_test(su_test, login_url="login")
@login_required
def common(request):
    name = Setting.objects.get(code="ent_name").value
    address = Setting.objects.get(code="ent_address").value
    reboot = Setting.objects.get(code="reboot").value
    fade_time = Setting.objects.get(code="fade_time").value
    updating = is_updating()
    logo = get_logo()

    context = {
        "ent_name": name,
        "ent_address": address,
        "reboot": reboot,
        "fade_time": fade_time,
        "is_updating": updating,
        "logo_url": logo
    }
    return JsonResponse(context)


class ResponseAfter(HttpResponse):
    """Обертка, чтобы вызывать функцию после отклика сервера"""
    def __init__(self, then_callback, *args, **kwargs):
        super(ResponseAfter, self).__init__(*args, **kwargs)
        self.then_callback = then_callback

    def close(self):
        super(ResponseAfter, self).close()
        self.then_callback()


class Network(View):
    """Конфигурация сети"""
    @method_decorator(user_passes_test(su_test, login_url="login"))
    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(Network, self).dispatch(*args, **kwargs)

    def get(self, request):
        cur_setup = [
            "ifconfig eth0 | grep -w inet | awk '{print $2}'",
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
            "grep -w '#wlan_static_config' /etc/dhcpcd.conf",
            "cat /sys/class/net/eth0/address",
            "cat /sys/class/net/wlan0/address"
        ]

        cur_setup_arr = multiple_execute_ssh('localhost', 'out', *cur_setup)

        cur_ip = cur_setup_arr[0]
        cur_mask = cur_setup_arr[1]
        cur_gw = cur_setup_arr[2]
        cur_hostname = cur_setup_arr[3]
        wcur_ip = cur_setup_arr[4]
        wcur_mask = cur_setup_arr[5]
        wcur_gw = cur_setup_arr[6]
        cur_dns1 = cur_setup_arr[7]
        cur_dns2 = cur_setup_arr[8]
        eth_dhcp_status = cur_setup_arr[9]
        # Проверяем, что если нет подключенного WIFI, то вернется пустая строка
        #cur_wlan = "" if cur_setup_arr[10].startswith("off/any") else cur_setup_arr[10]
        if cur_setup_arr[10].startswith("off/any"):
            cur_wlan = ""
        else:
            cur_wlan = cur_setup_arr[10]
        wifi_enabled = cur_setup_arr[4]
        wlan_dhcp_status = cur_setup_arr[11]

        cur_wifi = ""
        cur_wifi_psk = ""
        try:
            all_wifis = SchemeWPA.all()
            for wifi in all_wifis:
                cur_wifi = wifi.name
                cur_wifi_psk = wifi.options.get('psk')
        except:
            #logger.exception('ERROR: Can\'t read WIFI setting, probably not hardware')
            print('ERROR: Can\'t read WIFI setting, probably not hardware')
            #logger.exception(e.message)
        context = {
            "ip":  cur_ip,
            "mask": cur_mask,
            "gateway": cur_gw,
            "wlan_psk": cur_wifi_psk,
            "wlan_ip": wcur_ip,
            "wlan_mask": wcur_mask,
            "wlan_gateway": wcur_gw,
            "hostname": cur_hostname,
            "dns_primary": cur_dns1,
            "dns_secondary": cur_dns2,
            "dhcp": False if cur_setup_arr[9] else True,
            "wlan_name": cur_wlan,
            "wlan": True if cur_setup_arr[4] else False,
            "wlan_dhcp": False if cur_setup_arr[11] else True,
            "mac_eth": cur_setup_arr[12],
            "mac_wlan": cur_setup_arr[13]
        }
        #encod = BytestringEncoder()
        #encoded_data = encoder.encode(context)
        return JsonResponse(context, content_type='application/json', encoder=BytestringEncoder)

    def post(self, request):
        try:
            new_ip = request.POST["new_ip"]
            new_mask = request.POST["new_mask"]
            new_gateway = request.POST["new_gateway"]
            new_hostname = request.POST["new_hostname"]
            dns1 = request.POST["new_dns1"]
            dns2 = request.POST["new_dns2"]
            wifi_switch = True if request.POST["wifi_switch"] == "1" else False
            wnew_ip = request.POST["wnew_ip"]
            wnew_mask = request.POST["wnew_mask"]
            wnew_gateway = request.POST["wnew_gateway"]
            wnew_ssid = request.POST["wnew_ssid"]
            wnew_psk = request.POST["wnew_psk"]
            eth_dhcp = True if request.POST["eth_dhcp"] == "1" else False
            wifi_dhcp = True if request.POST["wifi_dhcp"] == "1" else False

            modify_hostname(new_hostname)

            if wnew_ssid and wifi_switch:
                modify_wifi(wnew_ssid, wnew_psk)
            else:
                modify_wifi()

            # Выполнится после того, как ответит
            def do_after():
                modify_network(
                    new_ip,
                    new_mask,
                    new_gateway,
                    dns1,
                    dns2,
                    wnew_ip,
                    wnew_mask,
                    wnew_gateway,
                    eth_dhcp,
                    wifi_dhcp,
                    wifi_switch
                )

            return ResponseAfter(do_after, request, status=200)

        except:
            #from django.http.response import JsonResponse
            return JsonResponse({'status':400})
            #return HttpResponse(status=400)
            


class DatetimeConfig(View):
    """Настройки даты и времени"""
    SERVER_VALIDATOR = RegexValidator(regex=re.compile(
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+"
        r"(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}(?<!-)\.?)|"
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|"  # ...or ipv4
        r"\[?[A-F0-9]*:[A-F0-9:]+\]?)"  # ...or ipv6
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)\Z",
        re.IGNORECASE
    ))

    def __init__(self, *args, **kwargs):
        super(DatetimeConfig, self).__init__(*args, **kwargs)
        # Используем словарь вместо switch
        self.methods_map = {
            "new_datetime": self.new_datetime,
            "new_tz": self.new_tz,
            "new_ntps": self.new_ntps
        }

    @method_decorator(user_passes_test(su_test, login_url="login"))
    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(DatetimeConfig, self).dispatch(*args, **kwargs)

    def get(self, request):
        tz_filtered = {}
        for tz in pytz.common_timezones:
            if tz in ALLOWED_TZS:
                cur_tz = pytz.timezone(tz)
                tz_filtered[datetime.now(cur_tz).strftime('%z')] = tz
        tz_choices = [
            {
                "name": tz_filtered[key],
                "tz": key[:3] + ":" + key[3:]  # Удостовериться, что не поломается
            } for key in sorted(tz_filtered)
        ]
        cur_tz = execute_ssh(
            "localhost",
            "cat /etc/timezone",
            type_of_return="out"
        ).replace("\n", "")
        ntp_servers = get_ntp_srvrs()
        context = {
            "timezones": tz_choices,
            "ntp_servers": ntp_servers,
            "cur_tz": cur_tz
        }
        return JsonResponse(context)

    def post(self, request):
        for key, value in json.loads(request.body).items():
            try:
                self.methods_map[key](value, request)

            except KeyError:
                return HttpResponse(status=400)

            except Exception as e:
                return HttpResponse(e.message, status=500)

        return HttpResponse(status=200)

    def new_datetime(self, new_date, request):
        modify_time(new_date, True)

    def new_tz(self, new_tz, request):
        execute_ssh(
            "localhost",
            "timedatectl set-timezone {0}".format(new_tz),
            type_of_return="out"
        )
        request.session["time_zone"] = False

    def new_ntps(self, new_ntps, request):
        ntps = new_ntps.split(",")
        for ntp in ntps:
            self.SERVER_VALIDATOR(ntp)
        set_ntp_srvrs(ntps)


class KeyLicense(View):
    """Работа с лицензионными ключами"""
    @method_decorator(user_passes_test(su_test, login_url="login"))
    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(KeyLicense, self).dispatch(*args, **kwargs)

    def post(self, request):
        new_key = request.body
        if new_key:
            write_key(new_key)
        return self.send_key_and_license()

    def get(self, request):
        return self.send_key_and_license()

    def send_key_and_license(self):
        key, licence = get_key()
        return JsonResponse({"key": key, "licence": licence})


class KeyLicenseMultiple(View):
    """Работа со многими лицензионными ключами разом"""
    @method_decorator(user_passes_test(su_test, login_url="login"))
    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(KeyLicenseMultiple, self).dispatch(*args, **kwargs)

    def get(self, request):
        """Возвращаем список UUID"""
        uuids = []
        hosts = Host.objects.all()

        for host in hosts:
            uuid = get_uuid(host.ip)
            if uuid is not None:
                uuids.append(uuid)

        # Если мастера не было в списке хостов, то отдельно добавим его
        master_uuid = get_uuid()
        if master_uuid not in uuids and master_uuid is not None:
            uuids.append(master_uuid)

        content = "\n".join(uuids)

        response = HttpResponse(content)
        response["Content-Disposition"] = "attachment; filename=uuids.csv"

        return response

    def post(self, request):
        """Получаем список UUID и ключей и применяем их"""
        # reader = csv.reader(request.body.split("\n"), delimiter=",")
        reader = csv.reader(request.body.decode('utf-8').split("\n"), delimiter=",")

        keys = {}

        for row in reader:
            try:
                keys[row[0]] = row[1]

            except IndexError:
                pass

        hosts = Host.objects.all()

        for host in hosts:
            uuid = get_uuid(host.ip)

            if uuid is not None:
                try:
                    write_key(keys[uuid], host.ip)

                except KeyError:
                    pass

        # Отдельно запишем для мастера
        master_uuid = get_uuid()
        if master_uuid is not None:
            try:
                write_key(keys[master_uuid])

            except KeyError:
                pass

        return HttpResponse(status=200)


class BluetoothConfig(View):
    """Настройки Bluetooth"""
    def __init__(self, *args, **kwargs):
        super(BluetoothConfig, self).__init__(*args, **kwargs)
        # Используем словарь вместо switch
        self.methods_map = {
            "scan": self.scan,
            "pair": self.pair,
            "turn_off": self.turn_off
        }

    @method_decorator(user_passes_test(su_test, login_url="login"))
    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(BluetoothConfig, self).dispatch(*args, **kwargs)

    def get(self, request):
        cur_bt = execute_ssh(
            "localhost",
            "grep \" device\" /etc/asound.conf | awk {'print $2'}",
            "out"
        )
        context = {
            "bt_uuid": cur_bt
        }
        return JsonResponse(context)

    def post(self, request):
        data = json.loads(request.body)
        key = data["operation"]
        if key in self.methods_map:
            return self.methods_map[key](data)

    def scan(self, data):
        import bluetooth
        devices = []
        nearby_devices = bluetooth.discover_devices(lookup_names=True)

        for addr, name in nearby_devices:
            devices.append(dict(uuid=addr, name=name))

        return JsonResponse({"status": "success", "devices": devices})

    def pair(self, data):
        cur_setup = execute_ssh(
            "localhost",
            "python /home/starko/bluetoothctl.py {0}".format(
                data["uuid"]
            ),
            "out"
        )
        return JsonResponse({"status": "success"})

    def turn_off(self, data):
        cur_setup = execute_ssh(
            "localhost",
            'python /home/starko/bluetoothctl.py ""',
            "out"
        )
        return JsonResponse({"status": "success"})


@user_passes_test(su_test, login_url="login")
@login_required
def sync(request):
    global_url_json = Setting.objects.get(code="global_url").as_json()
    period_json = Setting.objects.get(code="sync_period").as_json()
    sync_type = SyncScheduleOption.objects.get(pk=1).as_json()
    context = {
        "global_url": global_url_json,
        "period": period_json,
        "sync_type": sync_type
    }
    return JsonResponse(context)


@user_passes_test(su_test, login_url="login")
@login_required
def license(request):
    reg_email = Setting.objects.get(code="reg_email").as_json()
    key, license = get_key()
    uuid = get_uuid()

    context = {
        "key_license": {
            "key": key,
            "license": license
        },
        "reg_email": reg_email,
        "uuid": uuid
    }
    return JsonResponse(context)


@user_passes_test(su_test, login_url="login")
@login_required
@csrf_exempt
def diag(request):
    # TODO Отрефакторить
    master_uuid = get_uuid()
    diagnosis = HostDiagState.objects.all()
    res_obj = {}
    diag_arr = []
    for diag in diagnosis:
        diag_obj = {}

        # #####################################
        # участок кода, актуальный при наличии данных о здоровье пациента
        ######################################
        if diag.health:
            try:
                health = json.loads(diag.health)
                health = json.loads(health)
                # температура
                pat = re.compile("\+?\-?[0-9]{1,3}.?[0-9]{1,3}")
                # print(health)
                # print(type(health))
                temps = health["sensors"]
                temp_state = 1
                print(temps)
                print(type(temps))
                if  'str' in str(type(temps)):
                    if float(temps) > 80.0:
                       temp_state = 0
                else:
                    for temp in temps:
                        if float(temp) > 80.0:
                            temp_state = 0
                # print(temps)
                diag_obj["temp"] = {
                    "value": health["sensors"],
                    "state": temp_state
                }

                # мониторы
                pattern = re.compile("connected")

                mon_1_state = 1 if pattern.match(health["mon_1"]) else 0
                mon_2_state = 1 if pattern.match(health["mon_2"]) else 0
                total_mons = mon_1_state + mon_2_state
                db_mons = Monitor.objects.filter(
                    host=diag.host,
                    music_box=False
                ).count()

                if total_mons >= db_mons:
                    mons_state = 1
                else:
                    mons_state = 0

                mons_string = u"2"
                if total_mons == 0:
                    mons_string = u"нет"
                elif total_mons == 1:
                    mons_string = u"1"

                diag_obj["mons"] = {
                    "value": mons_string,
                    "state": mons_state
                }

                # плееры
                total_qiv = int(health["pqiv"]) if health["pqiv"] else 0
                total_mpv = int(health["mpv"]) if health["mpv"] else 0
                total_players = total_qiv + total_mpv

                if total_players >= total_mons:
                    players_state = 1
                else:
                    players_state = 0

                diag_obj["players"] = {
                    "value": u"{0}".format(total_players),
                    "state": players_state
                }

                # версия системы
                diag_obj["version"] = health["ver"] if health["ver"] else None
                diag_obj["host_time"] = health.get("host_time")
                diag_obj["uptime"] = health.get("uptime")
                diag_obj["license"] = health.get("license")
                diag_obj["kernel_version"] = health.get("kernel_version")
                diag_obj["device_model"] = health.get("device_model")

            except KeyError:
                # если встретили кейэррор, значит диагностические данные хоста не валидны(
                pass
        ############################################

        # пинг
        diag_obj["ping"] = {
            "value": u"В сети",
            "state": 1
        } if diag.ping else {
            "value": u"Недоступно",
            "state": 0
        }

        diag_obj["name"] = u"{0} {1}".format(
            diag.host.name,
            diag.host.ip
        )

        diag_obj["time"] = u"{0}".format(
            localtime(diag.time).strftime("%d.%m.%Y %H:%M")
        )

        # если это мастер, посмотрим на вебсервер
        host_uuid = get_uuid(diag.host.ip)
        if host_uuid == master_uuid:
            diag_obj["webserver"] = {
                "value": u"Запущено",
                "state": 1
            } if diag.webserver else {
                "value": u"Не работает",
                "state": 0
            }
        diag_arr.append(diag_obj)

        if host_uuid == master_uuid:
            ent_data = Setting.objects.get_name_and_address()
            res_obj["name"] = u"{0} {1}".format(*ent_data)
            res_obj["webserver"] = {
                "value": u"Запущено",
                "state": 1
            } if diag.webserver else {
                "value": u"Не работает",
                "state": 0
            }

        res_obj["peasants"] = diag_arr
    context = {"data": res_obj}

    return JsonResponse(context)


@user_passes_test(su_test, login_url="login")
@login_required
def export_conf(request):
    cur_conf = create_conf_backup()
    response = JsonResponse(cur_conf)
    response["Content-Disposition"] = "attachment; filename=export.json"
    return response


@user_passes_test(su_test, login_url="login")
@login_required
@csrf_exempt
def import_conf(request):
    setup = json.loads(request.body)
    reload_conf(setup)
    return JsonResponse({"status": "success"})


@user_passes_test(su_test, login_url="login")
@login_required
def export_radio(request):
    """Выгрузка списка радиостанций в csv"""
    surls = SavedUrl.objects.all().order_by("id")

    # Собираем строку в формате csv
    content = "\n".join(
        [",".join([
            "\"" + surl.name + "\"",
            "\"" + surl.url + "\"",
            "\"" + str(int(surl.video)) + "\""
        ]) for surl in surls]
    )
    response = HttpResponse(content)
    response["Content-Disposition"] = "attachment; filename=streams.csv"
    return response


@user_passes_test(su_test, login_url="login")
@login_required
@csrf_exempt
def import_radio(request):
    """Загрузка списка радиостанций в формате csv на сервер"""
    # сначала попробуем распарсить как json-строки
    its_json = False
    for j_str in request.body.split("\n"):
        if j_str:
            try:
                j_obj = json.loads(j_str)
                try:
                    SavedUrl.objects.update_or_create(
                        url=j_obj['url'], defaults=dict(
                        name=j_obj['name'],
                        video=False)
                    )
                    its_json = True
                except SavedUrl.MultipleObjectsReturned:
                    SavedUrl.objects.filter(url=j_obj['url'])[0].delete()
            except:
                break
    if its_json:
        return JsonResponse({"status": "success"})
    reader = csv.reader(request.body.split("\n"), delimiter=",")
    for row in reader:
        try:
            SavedUrl.objects.update_or_create(
                url=row[1], defaults=dict(
                name=row[0],
                video=bool(int(row[2])))
            )
        except SavedUrl.MultipleObjectsReturned:
            SavedUrl.objects.filter(url=row[1])[0].delete()
    return JsonResponse({"status": "success"})


@user_passes_test(su_test, login_url="login")
@login_required
@csrf_exempt
def spawn_diag(request):
    if request.method == "POST":
        diagnose_all_hosts()
        return JsonResponse({"status": "success"})


class Reboot(View):
    """Перезагружаем устройства и получаем инфу об этом"""
    @method_decorator(user_passes_test(su_test, login_url="login"))
    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(Reboot, self).dispatch(*args, **kwargs)

    def post(self, request):
        """Перезагружаем всех"""
        return ResponseAfter(all_hosts_reboot)

    def get(self, request):
        """Получаем данные о последней перезагрузке"""
        hosts = Host.objects.all()
        reboots = []

        for host in hosts:
            try:
                reboot = RebootsData.objects.get(host=host)

                if not reboot.check:
                    error = execute_ssh(
                        host.ip,
                        "cat /var/www/.reboot",
                        "out"
                    )

                    # Файл пустой и существует, значит успешно перезагрузились
                    # В противном случае ничего не делаем
                    if len(error) == 0:
                        reboot.check = datetime.now()
                        reboot.save()

            except RebootsData.DoesNotExist:
                reboot = RebootsData(start=None, host=host)

            except:
                pass

            reboots.append(reboot.as_json())

        try:
            reboot = RebootsData.objects.get(host=None)

            if not reboot.check:
                error = execute_ssh(
                    "localhost",
                    "cat /var/www/.reboot",
                    "out"
                )

                if len(error) == 0:
                    reboot.check = datetime.now()
                    reboot.save()

            reboots.append(reboot.as_json())

        except RebootsData.DoesNotExist:
            pass

        return JsonResponse(reboots, safe=False)


@user_passes_test(su_test, login_url="login")
@login_required
@csrf_exempt
def patch_upload(request):
    """Загружаем файл обновления на мастер, а он уже на слейвов"""
    # TODO Отрефакторить
    lock_path = os.path.join(MEDIA_ROOT, MC_PATCH_FOLDER, ".lock")
    locked = os.path.isfile(lock_path)

    if locked:
        locked_time = datetime.fromtimestamp(os.path.getmtime(lock_path))
        time_spent = datetime.now() - locked_time

        if time_spent.total_seconds() <= 60 * 60 * 24:
            return JsonResponse({
                "status": "error",
                "msg": "Идёт установка обновления"
            })

    if request.method == "POST":
        raw_file = request.FILES["new_patch"]
        f_name = translit(raw_file.name, "ru", reversed=True)
        patch_file = os.path.join(MEDIA_ROOT, MC_PATCH_FOLDER, f_name)

        with open(patch_file, "wb+") as destination:
            for chunk in raw_file.chunks():
                destination.write(chunk)

        # если до кого-то из рабов не дойдет патч,
        # то тут мы упадем и не будем патчить никого
        patch_peasants(f_name)

        if not locked:
            open(lock_path, "a").close()

        execute_ssh("localhost", "date > /var/www/.reboot")

        return JsonResponse({
            "status": "success",
            "msg": "Файл обновления загружен"
        })

    return render(request, "admin/patch_upload.html", {"is_updating": False})


@user_passes_test(su_test, login_url="login")
@csrf_exempt
def logo_upload(request):
    # TODO Отрефакторить
    import os

    if request.method == "POST":
        f = request.FILES["new_logo"]
        f_name = translit(f.name, "ru", reversed=True)
        logo_dir = os.path.join(MEDIA_ROOT, "logo")
        if not os.path.exists(logo_dir):
            os.mkdir(logo_dir)
        fpath = os.path.join(logo_dir, f_name)

        with open(fpath, "wb+") as destination:
            for chunk in f.chunks():
                destination.write(chunk)

        dir, fname = os.path.split(fpath)
        dir = os.path.join(MEDIA_ROOT, "logo")
        new_fname = u"r_" + fname
        import cv2

        img = cv2.imread(fpath, cv2.IMREAD_UNCHANGED)
        height = img.shape[0]
        width = img.shape[1]
        if height > 125 or width > 320:
            if height > 125:
                r = 125 / float(height)
                dim = (int(width * r), int(height * r))
                resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
            width = resized.shape[1]

            if width > 320:
                r = 320 / float(width)
                dim = (int(width * r), int(height * r))
                resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

            cv2.imwrite(os.path.join(dir, new_fname), resized)

        else:
            cv2.imwrite(os.path.join(dir, new_fname), img)

        logo_url = os.path.join(MEDIA_URL, "logo", new_fname)
        try:
            set = Setting.objects.get(code="logo")
            set.value = logo_url

        except Setting.DoesNotExist:
            set = Setting(code="logo", name=u"Логотип", value=logo_url)

        set.save()

        return HttpResponse("ok")

    elif request.method == "DELETE":
        try:
            set = Setting.objects.get(code="logo")
            set.delete()

            folder = os.path.join(MEDIA_ROOT, "logo")
            delete_folder_files(folder)

        except Setting.DoesNotExist:
            pass

        return HttpResponse("ok")

    return render(request, "admin/logo_upload.html", {"is_updating": False})


@user_passes_test(su_test, login_url="login")
@csrf_exempt
def wifi_quality(request):
    res = {}
    if request.method == "GET":
        cur_wlan = Cell.all("wlan0")
        if cur_wlan:
            res["quality"] = list(cur_wlan)[0].quality
    return JsonResponse(res)


@user_passes_test(su_test, login_url="login")
@csrf_exempt
def wifi_scan(request):
    res = []
    if request.method == "GET":
        all_wifis = Cell.all("wlan0")
        for wf in all_wifis:
            if wf.encryption_type in ("wpa", "wpa2"):
                res.append({"ssid": wf.ssid, "quality": wf.quality})
    return JsonResponse(res, safe=False)


@user_passes_test(su_test, login_url="login")
@csrf_exempt
def mon_res_list(request):
    if request.method == "POST":
        host = request.POST.get("host")
        slot = request.POST.get("slot")

        if not (host and slot):
            res = []

        else:
            res = get_mon_res(host, slot)

        return HttpResponse(json.dumps(res))


@user_passes_test(su_test, login_url="login")
@login_required
@csrf_exempt
def ntp_srv_ctl(request):
    if request.method == "POST":
        if request.POST["status"] == "1":
            execute_ssh(
                "localhost",
                "systemctl enable ntp & service ntp start",
                type_of_return="out"
            )

        else:
            execute_ssh(
                "localhost",
                "systemctl disable ntp & service ntp stop",
                type_of_return="out"
            )

    return JsonResponse({"status": "ok"})


@user_passes_test(su_test, login_url="login")
@login_required
@csrf_exempt
def about(request):
    """Вкладка Об устройстве"""
    about_commands = [
        "uname -r",
        "grep '[[:space:]]ro[[:space:],]' /proc/mounts"
    ]

    about_data =['as', 'ass']# multiple_execute_ssh("localhost", "out", *about_commands)
    
    if str(about_data[1]).find('/dev/root') != -1:
    #if "/dev/root" in about_data[1]:
            fs_status = "read-only"
    else:
        fs_status = "read-write"
   
    #fs_status = "read-only" if "/dev/root" in about_data[1] else "read-write"
    response1 = {
        "version": get_version(),
        "uuid": get_uuid(),
        "kernel": about_data[0],
        "device": get_device_model(),
        "fs": fs_status
    }
    return JsonResponse(response1)


class Spotify(View):
    """Включение/отключение spotifyd на хосте"""
    @method_decorator(user_passes_test(su_test, login_url="login"))
    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(Spotify, self).dispatch(*args, **kwargs)

    def get(self, request, host_id):
        host = Host.objects.get(id=host_id)

        username = execute_ssh(
            host.ip,
            "grep username /etc/spotifyd.conf | awk {'print $3'}",
            "out"
        )

        return JsonResponse({"username": username})

    def post(self, request):
        data = json.loads(request.body)

        try:
            host_id = data["host_id"]
            host = Host.objects.get(id=host_id)

        except KeyError:# as Host.DoesNotExist:
            return HttpResponse(status=400)

        commands = []
        state = False

        try:
            hostname = data["hostname"].encode("utf-8").strip().replace(" ", "_")
            username = data["username"]
            password = data["password"]

            commands = [
                "mount -o remount,rw /",
                "sed -i '/username =/c\\username = {}' /etc/spotifyd.conf".format(
                    username
                ),
                "sed -i '/password =/c\\password = {}' /etc/spotifyd.conf".format(
                    password
                ),
                "sed -i '/device_name =/c\\device_name = {}' /etc/spotifyd.conf".format(
                    hostname
                ),
                "systemctl enable spotifyd",
                "systemctl start spotifyd",
                # Выключаем монитор на всякий
                "echo 'standby 0' | cec-client -d 1 -s RPI & vcgencmd display_power 0",
                "sync;mount -o remount,ro /"
            ]

            state = True

        except KeyError:
            commands = [
                "mount -o remount,rw /",
                "sed -i '/username =/c\\username = ' /etc/spotifyd.conf",
                "sed -i '/password =/c\\password = ' /etc/spotifyd.conf",
                "sed -i '/device_name =/c\\device_name = ' /etc/spotifyd.conf",
                "systemctl stop spotifyd",
                "systemctl disable spotifyd",
                # Включаем монитор, если он был выключен
                "vcgencmd display_power 1 & echo 'on 0' | cec-client -d 1 -s RPI",
                "sync;mount -o remount,ro /"
            ]

        multiple_execute_ssh(host.ip, "out", *commands)

        return JsonResponse({"on": state})
