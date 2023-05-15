# -*- coding: utf-8 -*-
import json
import os
import re
import socket
import subprocess
import sys
import platform
import time
from datetime import datetime, date, timedelta

from django_starko.settings import MEDIA_ROOT, MC_PATCH_FOLDER, BASE_DIR
from mc.models import Host, HostDiag, HostDiagState, HostDiagArchive, Blackout, Monitor
from mc.utils.commands import get_uuid, execute_ssh, multiple_execute_ssh, key_check_uuid

PI_MODELS = {
    "900021": "Opteo A+",
    "900032": "Opteo B+",
    "a01040": "Opteo 2B",
    "a01041": "Opteo 2B",
    "a02042": "Opteo 2B",
    "a21041": "Opteo 2B",
    "a22042": "Opteo 2B",
    "9020e0": "Opteo 3A+",
    "a02082": "Opteo 3B",
    "a22082": "Opteo 3B",
    "a32082": "Opteo 3B",
    "a52082": "Opteo 3B",
    "a22083": "Opteo 3B",
    "a020d3": "Opteo 3B+",
    "a03111": "Opteo 4B",
    "b03111": "Opteo 4B",
    "b03112": "Opteo 4B",
    "c03111": "Opteo 4B",
    "c03112": "Opteo 4B",
    "d03114": "Opteo 4B",
    "900061": "Opteo CM",
    "a020a0": "Opteo CM3",
    "a220a0": "Opteo CM3",
    "a02100": "Opteo CM3+",
    "900092": "Opteo Zero",
    "900093": "Opteo Zero",
    "920092": "Opteo Zero",
    "920093": "Opteo Zero",
    "9000C1": "Opteo Zero W"
}



class BytestringEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode('utf-8')
        return super().default(obj)
    


def diagnose_host(host):
    """
    Функция для сбора диагностической информации с 1го хоста
    :param ip: айпи адрес хоста
    :return:
    """
    ver_file_path = os.path.join(MEDIA_ROOT, MC_PATCH_FOLDER, ".service", ".ver")
    cat_cmd = "cat {0}".format(ver_file_path)

    # список диагностических команд
    diag_reqs = [
        "vcgencmd measure_temp",
        "vcgencmd hdmi_status_show",
        "vcgencmd hdmi_status_show",  # Оставим для 4 пихи
        "pgrep -c info-beamer",
        "pgrep -c chromium",
        cat_cmd,
        "dmesg | grep 'critical'",
        "date",
        "uptime -p",
        "cat /var/www/django_starko/.key",
        # "cat /var/lib/mpd/.asoundrc | grep device | awk '{print $2}' | sed -r 's/\"//g'",
        "grep \" device\" /etc/asound.conf | awk {'print $2'}",
        "ps -eo comm,etimes|grep info-beamer |awk '{print $2}'",
        "awk '{print $1}' /proc/uptime",
        "grep Revision /proc/cpuinfo | awk {'print $3'}",
        "uname -r"
    ] if not host.is_nuc else [
        "sensors | grep ^Core | awk '{print $3}'",
        "cat /sys/class/drm/card0-HDMI-A-1/status",
        "cat /sys/class/drm/card0-HDMI-A-2/status",
        "pgrep -c pqiv",
        "pgrep -c mpv",
        cat_cmd,
        "dmesg | grep 'critical medium error'",
        "date",
        "uptime -p",
        "cat /sys/class/drm/card0-VGA-1/status"
    ]

    diag_res_raw = multiple_execute_ssh(host.ip, 'out', *diag_reqs)
    diag_res_raw = list(diag_res_raw)
    for x in diag_res_raw:
        print(x)
    temp_mask = re.compile('\d{1,}\.?\d{0,}')
    #temp_mask = re.compile(b'\d{1,}\.?\d{0,}')
    print(temp_mask)
    if not host.is_nuc:
        mb_connected = Monitor.objects.filter(host=host, music_box=True).exists()

        total = {
            # "sensors": temp_mask.findall(diag_res_raw[0].decode("utf-8"))[0],
            "sensors": temp_mask.findall(diag_res_raw[0])[0],
            #"sensors": temp_mask.findall(diag_res_raw[0].decode())[0].decode(),
            "mon_1": "connected" if "1" in str(diag_res_raw[1]) else None,
            "mon_2": "connected" if mb_connected else "",
            "pqiv": diag_res_raw[3],
            "mpv": "1" if diag_res_raw[4] else "0",
            "ver": diag_res_raw[5] if diag_res_raw[5] else "1.0",
            "critical_error": True if diag_res_raw[6] else False,
            "host_time": diag_res_raw[7],
            "uptime": diag_res_raw[8],
            "key": diag_res_raw[9],
            "bluetooth": True if diag_res_raw[10] else False,
            "ib_uptime": int(diag_res_raw[11]) if diag_res_raw[11] else 0,
            "uptime_secs": int(float(diag_res_raw[12])) if diag_res_raw[12] else 0,
            "diag_time": int(time.time()),
            "device_model": PI_MODELS.get(
                diag_res_raw[13].strip(),
                "Unknown"
            ),
            "kernel_version": diag_res_raw[14]
        }
    else:
        pattern = re.compile("connected")
        hdmi_1 = True if pattern.match(diag_res_raw[1]) else False
        hdmi_2 = True if pattern.match(diag_res_raw[2]) else False
        total = {
            "sensors": diag_res_raw[0],
            "mon_1": "connected" if hdmi_1 else "disconnected",
            "mon_2": "connected" if hdmi_2 else "disconnected",
            "pqiv": diag_res_raw[3],
            "mpv": diag_res_raw[4],
            "ver": diag_res_raw[5] if diag_res_raw[5] else "1.0",
            "critical_error": True if diag_res_raw[6] else False,
            "host_time": diag_res_raw[7],
            "uptime": diag_res_raw[8],
            "key": "0",
            "bluetooth": False
        }

    #encod = BytestringEncoder()
    #encoded_data = encod.encode(total)
    #return JsonResponse(context, content_type='application/json', encoder=BytestringEncoder)
    #return encoded_data
    return total


def ping(ip, timeout=1):
    ping_str = "-n 1" if platform.system().lower() == "windows" else "-c 1"
    return os.system("ping -w " + str(timeout) + " " + ping_str + " " + ip) == 0


def add_resync(resync_objects, host_json, host_diag_json):
    if host_json['vw_mon_id']:
        target_dict = resync_objects['vw']
        target_id = host_json['vw_mon_id']
    elif host_json['sync_group']:
        target_dict = resync_objects['sg']
        target_id = host_json['sync_group']
    else:
        return
    if target_id not in target_dict:
        target_dict[target_id] = {
            'first_diag_time': host_diag_json['diag_time'],
            'min_uptime': host_diag_json['uptime_secs'],
            'max_uptime': host_diag_json['uptime_secs'],
            'min_ib': host_diag_json['ib_uptime'],
            'max_ib': host_diag_json['ib_uptime']
        }
    else:
        dict_to_upd = target_dict[target_id]
        delta_w_first = host_diag_json['diag_time'] - dict_to_upd['first_diag_time']
        dict_to_upd['min_uptime'] = min(dict_to_upd['min_uptime'], host_diag_json['uptime_secs']-delta_w_first)
        dict_to_upd['max_uptime'] = max(dict_to_upd['max_uptime'], host_diag_json['uptime_secs']-delta_w_first)
        dict_to_upd['min_ib'] = min(dict_to_upd['min_ib'], host_diag_json['ib_uptime']-delta_w_first)
        dict_to_upd['max_ib'] = max(dict_to_upd['max_ib'], host_diag_json['ib_uptime']-delta_w_first)


def really_resync(uptime_data):
    if uptime_data['min_uptime'] < 60:
        return False
    min_u = uptime_data['min_ib']
    max_u = uptime_data['max_ib']
    print ('MINMAX TIMES: ', min_u, max_u)
    if max_u < 360:
        return False
    if min_u and max_u:
        delta = max_u - min_u
        if delta > 6:
            print('RESYNC')
            return True


def check_resync(resync_objects):
    for mon_id, data in resync_objects['vw'].iteritems():
        resync = really_resync(data)
        if resync:
            mon_obj = Monitor.objects.get(pk=mon_id)
            p = subprocess.Popen(
                [sys.executable, os.path.join(BASE_DIR, 'manage.py'), 'apply_host_by_id', str(mon_obj.host_id), 'False'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
    for sg_id, data in resync_objects['sg'].iteritems():
        resync = really_resync(data)
        if resync:
            mon_obj = Monitor.objects.filter(sync_group=sg_id).first()
            p = subprocess.Popen(
                [sys.executable, os.path.join(BASE_DIR, 'manage.py'), 'apply_host_by_id', str(mon_obj.host_id), 'False'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
    return


def diagnose_all_hosts():
    hosts = Host.objects.all()
    master_uuid = get_uuid()
    resync_objects = {'vw': {},
                      'sg': {}}
    for host in hosts:
        # создадим архивную запись диагностики
        hd = HostDiag()
        host_uuid = None
        # и поищем/создадим последнее состояние диагностики
        try:
            hds = HostDiagState.objects.get(host=host)
        except HostDiagState.DoesNotExist:
            hds = HostDiagState(host=host)
        try:
            hd.ping = ping(host.ip)
            if hd.ping:
                diag_obj = diagnose_host(host)
                
                # add_resync(resync_objects, host.as_json(), diag_obj)
                host_uuid = get_uuid(host.ip)
                diag_obj['uuid'] = host_uuid
                diag_obj['license'] = key_check_uuid(diag_obj.get('key'), diag_obj.get('uuid'))
                encod = BytestringEncoder()
                diag_obj = encod.encode(diag_obj)
                #hd.health = json.dumps(diag_obj)
                #hd.health = json.dumps(diag_obj.decode("utf-8"))
                #hd.health = json.dumps(diag_obj, ensure_ascii=False).encode('utf8').decode('utf8')
                #hd.health = json.dumps(diag_obj, ensure_ascii=False)
                #hd.health = json.dumps(diag_obj, ensure_ascii=False, encoding='utf-8')
                #diag_obj_str = {k: v.decode() if isinstance(v, bytes) else v for k, v in diag_obj.items()}
                #for k, v in diag_obj.items():
                #    diag_obj[k] = str(v)
                hd.health = json.dumps(diag_obj, ensure_ascii=False, cls=BytestringEncoder)


        except socket.error:
            hd.ping = False

        hd.webserver = False
        if host_uuid == master_uuid:
            # проверим nginx
            # is_run = execute_ssh(host.ip, 'service nginx status|grep active|grep running', 'out')
            # is_run = subprocess.check_output("service nginx status|grep active|grep running", shell=True).decode("utf-8").replace('\n', '')


            # Выполнение команды и получение вывода
            is_run = subprocess.run(['service', 'nginx', 'status'], capture_output=True, text=True)

            # Проверка статуса завершения команды
            if is_run.returncode == 0:
                # Разбивка вывода на строки и поиск нужной информации
                output_lines = is_run.stdout.split('\n')
                for line in output_lines:
                    if 'active' in line and 'running' in line:
                        # Вывод нужной информации
                        print(line)
            else:
                # Обработка ошибки, если команда завершилась с ошибкой
                print('Ошибка выполнения команды')


            hd.webserver = True if is_run else False
            # если с nginx все ок, проверим на всяк uwsgi
            if hd.webserver:
                # uwsgi_status = execute_ssh(host.ip, 'pgrep -c uwsgi', 'out')
                uwsgi_status = subprocess.check_output("pgrep -c uwsgi", shell=True).decode("utf-8").replace('\n', '')
                hd.webserver = True if uwsgi_status else False

        # hda = HostDiagArchive(host=host, ping=hd.ping, webserver=hd.webserver, health=hd.health)
        # hda.save()
        hds.ping = hd.ping
        hds.webserver = hd.webserver
        hds.health = hd.health

        hds.save()
    # check_resync(resync_objects)
    return True


def mons_equals_players(string_health):
    """
    Функция сличает кол-во подключенных мониторов и запущенных плееров на объектах
    :param string_health:
    :return: Тру, если кол-во равно, Фалсе если не равно
    """
    if is_blackout_now():
        return True

    health = json.loads(string_health)
    pattern = re.compile("connected")
    mon_1 = 1 if pattern.match(health.get("mon_1")) else 0
    mon_2 = 1 if pattern.match(health.get("mon_2")) else 0
    total_mons = mon_1 + mon_2
    total_qiv = int(health["pqiv"]) if health["pqiv"] else 0
    total_mpv = int(health["mpv"]) if health["mpv"] else 0
    total_players = total_qiv + total_mpv

    return total_players == total_mons


def monitor_fail_sentinel(hds):
    if hds.health:
        cur_equality = mons_equals_players(hds.health)
        # т.к. новое состояние мы еще не сохранили(!), посмотрим на предыдущее состояние диагностики
        try:
            prev_hds = HostDiagState.objects.get(host=hds.host)
        except HostDiagState.DoesNotExist:
            return
        if prev_hds.health:
            prev_equality = mons_equals_players(hds.health)

            if not cur_equality and not prev_equality:
                # если у нас в двух подряд диагностиках не совпадает кол-во плееров с реальным
                p = subprocess.Popen(
                    [sys.executable, os.path.join(BASE_DIR, 'manage.py'), 'apply_host_by_id', str(hds.host_id)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT)


def get_diag_obj():
    hosts = Host.objects.all().prefetch_related('hostdiagstate_set').order_by('ip')
    hosts_json = []
    for host in hosts:
        host_uuid = get_uuid(host.ip)
        hd_set = host.hostdiagstate_set.all()
        if hd_set:
            diag_state = hd_set[0]
            host_json = diag_state.as_sync_json()
            host_json['uuid'] = host_uuid
            host_json['license'] = (json.loads(diag_state.health)).get(
                'license') if diag_state.health else False  # TODO Facepalm. понять и простить
            hosts_json.append(host_json)

    return hosts_json


def is_mon_ok(mon_obj):
    '''
    Возвращает 3 параметра: есть ли пинг до коробки, причину отсутствия пинга и есть ли лицензия
    :param mon_obj:
    :return:
    '''
    ping, reason, license = False, None, False
    try:
        diag_state = HostDiagState.objects.get(host_id=mon_obj.host_id)
        if not diag_state.ping:
            ping = False
            reason = 'host'
            return ping, reason, license
        if diag_state.health:
            health = json.loads(diag_state.health)
            # мониторы
            pattern = re.compile("connected")
            if mon_obj.host.is_nuc:
                if mon_obj.host_slot == 0:
                    ping = True if pattern.match(health.get("mon_1")) else False
                    reason = 'mon'
                else:
                    ping = True if pattern.match(health.get("mon_2")) else False
                    reason = 'mon'
            else:
                if not mon_obj.music_box:
                    ping = True if pattern.match(health.get("mon_1")) else False
                    reason = 'mon'
                else:
                    ping = True if pattern.match(health.get("mon_2")) else False
                    reason = 'mon'
            license = health.get('license') if not mon_obj.host.is_nuc else True
    except HostDiagState.DoesNotExist:
        return True, 'host', True
    return ping, reason, license


def is_blackout_now():
    now = datetime.now()
    now_day_of_week = now.isoweekday()

    bls = Blackout.objects.all().order_by("day_of_week")

    for bl in bls:
        delta_days = [[0, 0]]
        add_day_to_end = 0
        # если время окончания меньше времени начала, значит окончание - в следующем дне!
        if bl.time_begin > bl.time_end:
            delta_days.append([-1, 0])
            delta_days.append([0, 1])

        for delta in delta_days:
            dt_begin_bl = datetime.combine(date.today(), datetime.min.time()) + timedelta(hours=bl.time_begin.hour,
                                                                                          minutes=bl.time_begin.minute,
                                                                                          days=delta[0])

            dt_end_bl = datetime.combine(date.today(), datetime.min.time()) + timedelta(hours=bl.time_end.hour,
                                                                                        minutes=bl.time_end.minute,
                                                                                        days=delta[1])

            # если блэкаут наступил
            if (dt_begin_bl <= now < dt_end_bl) and (bl.day_of_week == 0 or (bl.day_of_week == now_day_of_week)):
                return True

    return False
