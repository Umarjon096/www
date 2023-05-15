# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import datetime
import hashlib
import json
import os
import paramiko
import re
import errno
import subprocess

from numpy.compat import unicode

from django_starko.settings import MC_SSH_PORT, MC_HOSTS_USER, MC_HOSTS_PASSWORD, MEDIA_ROOT, MC_LOCAL_BUFFER_DIR, \
    MC_PATCH_FOLDER, BASE_DIR, MC_NGINX_TMP, SSH_TIMEOUT
from mc.models import File, Item, Host, Monitor, HostDiagState


IPC_AUDIO = "/tmp/mpv-audio"
IPC_VIDEO = "/tmp/mpv-video"


def execute_ssh(host_ip, command, type_of_return='err'):
    """
    функция выполняет переданную командную строку на указанном хосте из под MC_HOSTS_USER'a
    :param host_ip: хост
    :param command: bash команда
    :return: стандартный вывод команды
    """

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(
        host_ip,
        port=MC_SSH_PORT,
        username=MC_HOSTS_USER,
        password=MC_HOSTS_PASSWORD,
        timeout=SSH_TIMEOUT
    )

    _stdin, stdout, stderr = ssh.exec_command(command)
    outtext = None

    if type_of_return == "err":
        outtext = stderr.read()

    elif type_of_return == "out":
        outtext = stdout.read()

    ssh.close()
    if isinstance(outtext, bytes):
            outtext = outtext.decode('utf-8')

    return outtext


def multiple_execute_ssh(ip, type_of_return='out', *args):
    '''
    функция выполняет кучу переданных консольных команд на указанном хосте из под MC_HOSTS_USER'a
    :param ip: хост
    :param command: bash команда
    :return: стандартный вывод команды
    '''

    print(ip)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        ip,
        port=MC_SSH_PORT,
        username=MC_HOSTS_USER,
        password=MC_HOSTS_PASSWORD,
        timeout=SSH_TIMEOUT
    )

    res_arr = []
    for command in args:
        stdin, stdout, stderr = ssh.exec_command(command)
        outtext = None
        if type_of_return == 'err':
            outtext = stderr.read()
            if isinstance(outtext, bytes):
                outtext = outtext.decode('utf-8')
        elif type_of_return == 'out':
            outtext = stdout.read()
            if isinstance(outtext, bytes):
                outtext = outtext.decode('utf-8')
        res_arr.append(outtext)

    ssh.close()
    return tuple(res_arr)


def rw_execute_ssh(ip, type_of_return='out', *args):
    new_args = list(args)
    new_args.insert(0, 'mount -o remount,rw /')
    new_args.append('mount -o remount,ro /')
    return multiple_execute_ssh(ip, type_of_return, *new_args)


def umount_mount(ip, hostname):
    '''
    функция выполняет команды маунт/анмаунт, подключая рабочие папки хостов
    :param ip:
    :param hostname:
    :return:
    '''
    umount_cmd = 'umount {0}/{1}'.format(MEDIA_ROOT, hostname)
    mount_cmd = 'mount {0}:{1} {2}/{3}'.format(ip, MC_LOCAL_BUFFER_DIR, MEDIA_ROOT, hostname)
    out_text = execute_ssh('localhost', umount_cmd)
    out_text += execute_ssh('localhost', 'rmdir {0}/{1}'.format(MEDIA_ROOT, hostname))
    out_text += execute_ssh('localhost', 'mkdir {0}/{1}'.format(MEDIA_ROOT, hostname))
    out_text += execute_ssh('localhost', mount_cmd)
    return out_text


def copy_cmd_text(files_arr, to_dir):
    """
    функция генерирует команду на копирование списка файлов
    :param files_arr: список файлов (полные пути)
    :param to_dir: куда копировать
    :return: текст команды
    """
    cmd_text = 'cp '
    for file in files_arr:
        cmd_text += '"{0}"'.format(file)
        cmd_text += ' '

    cmd_text += to_dir
    return cmd_text


def copy_file(to_ip, from_path, to_path):
    '''
    функция копирует файл на удаленый хост
    :param to_ip: удаленный хост
    :param from_path: путь до файла на локальном хосте
    :param to_path: куда сохранить файл на удаленном
    :return: ничего не возвращает
    '''
    from scp import SCPClient
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(
        to_ip,
        username=MC_HOSTS_USER,
        password=MC_HOSTS_PASSWORD,
        timeout=SSH_TIMEOUT
    )

    scp = SCPClient(ssh.get_transport(), socket_timeout=120.0)
    scp.put(from_path, to_path)
    ssh.close()


def link_files(from_paths, to_path):
    for file_path in from_paths:
        #https://stackoverflow.com/questions/1250079/how-to-escape-single-quotes-within-single-quoted-strings
        file_path_corr = file_path.replace("'", """'"'"'""")
        basename_corr = os.path.basename(file_path).replace("'", """'"'"'""")
        subprocess.check_output([u"chmod 777 '{0}' ".format(file_path_corr)], shell=True).decode("utf-8") #ДА, БЛЯДЬ, ДА!
        subprocess.check_output(
            [u"ln -s -f '{0}' '{1}/{2}'".format(file_path_corr, to_path, basename_corr)],
            shell=True).decode("utf-8")


def delete_folder_files(folder_path):
    for the_file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


def delete_file(fpath):
    if os.path.isfile(fpath):
        os.unlink(fpath)


def delete_unused_files():
    for file in File.objects.all():
        delete_item_files(file.id)


def delete_item_files(file_id):
    try:
        file = File.objects.get(pk=file_id)
        items_referencing = Item.objects.filter(file_id=file_id).count()
        if not items_referencing or not os.path.exists(file.data.path):
            file.thumbnail.delete()
            file.data.delete()
            file.delete()
            # os.remove(item.local_path)
            #dir, fname = os.path.split(item.thumb_url)
            #thumb_path = os.path.join(MEDIA_ROOT,'thumbnails',fname)
            #os.remove(thumb_path)
    except OSError:
        None


def delete_not_db_files():
    from os import listdir
    from os.path import isfile, join
    onlyfiles = [f for f in listdir(MEDIA_ROOT) if isfile(join(MEDIA_ROOT, f))]
    for file in onlyfiles:
        fpaths_local = [tmpl.format(file).decode('utf-8') for tmpl in ['./{0}', '{0}', MEDIA_ROOT+'/{0}']]
        print('FP', fpaths_local)
        f_exists = File.objects.filter(data__in=fpaths_local).exists()
        print('FE', f_exists)
        if not f_exists:
            fpath = os.path.join(MEDIA_ROOT, file).decode('utf-8')
            t = os.path.getmtime(fpath)
            a = datetime.fromtimestamp(t)
            b = datetime.now()
            file_age = (b - a).total_seconds()
            if file_age > 3600:
                os.remove(fpath)


def delete_nginx_tmp():
    """
    Сервисная функция для очистки больших прервавшихся загрузок
    Смотрит в темп директорию нгинкса, сравнивает последнее время изменения файла, все что старше 5 минут трет к х-ам
    :return:
    """
    from os import listdir
    from os.path import isfile, join, isdir
    if not isdir(MC_NGINX_TMP):
        return

    onlyfiles = [f for f in listdir(MC_NGINX_TMP) if isfile(join(MC_NGINX_TMP, f))]
    for file in onlyfiles:
        fpath = os.path.join(MC_NGINX_TMP, file).decode('utf-8')
        t = os.path.getmtime(fpath)
        a = datetime.fromtimestamp(t)
        b = datetime.now()
        file_age = (b - a).total_seconds()
        if file_age > 300:
            os.remove(fpath)


def get_ntp_srvrs():
    # ntp_filepath = os.path.join(BASE_DIR, '.ntp_srvrs')
    # if os.path.exists(ntp_filepath):
    #     with open(ntp_filepath) as f:
    #         ntp_string = f.readline().replace('\n', '')
    #         ntp_commas = ','.join(ntp_string.split(' '))
    #         return ntp_commas
    # else:
    #     return ''
    ntp_raw = subprocess.check_output("sed -n '/#s_s/,/#s_e/{/#s_s/b;/#s_e/b;p}' /etc/chrony/chrony.conf",
                                     shell=True)
    ntp_raw = str(ntp_raw).replace('server ','').replace(' iburst','').replace('\n', ',')
    return ntp_raw[:-1]


def set_ntp_srvrs(servers):
    write_str = ''
    for server in servers:
        if server:
            write_str += 'server {0} iburst\\n'.format(server)
    err = rw_execute_ssh('localhost', 'err', "sed -n -i '/#s_s/{p;:a;N;/#s_e/!ba;s/.*\\n/"+write_str+"/};p' /etc/chrony/chrony.conf", "service chrony restart")



def write_key(new_key, ip="localhost"):
    """Пишем лицензию в файл указанного хоста"""
    command = u"echo {} > {}".format(
        new_key,
        "/var/www/django_starko/.key"
    )

    execute_ssh(ip, command, "out")


def key_check():
    try:
        uuid = get_uuid()
        hshhh = hashlib.sha224('hexadragon{0}'.format(uuid)).hexdigest()
        with open(os.path.join(BASE_DIR, '.key')) as f:
            key = f.readline().replace('\n', '')
            if key == hshhh:
                return True
            else:
                return False
    except:
        return False


def key_check_uuid(key, uuid):
    key = key.replace("\n", "")
    # key = key.decode('utf-8').replace("\n", "")

    uuid = uuid.replace("\n", "")


    #hshhh = hashlib.sha224("hexadragon{0}".format(uuid)).hexdigest()
    hshhh = hashlib.sha224("hexadragon{0}".format(uuid).encode()).hexdigest()

    return key == hshhh


def get_key():
    key_path = os.path.join(BASE_DIR, '.key')
    key, valid = None, False
    if os.path.exists(key_path):
        with open(key_path) as f:
            key = f.readline().replace('\n', '')
    if key:
        uuid = get_uuid()
        #hshhh = hashlib.sha224('hexadragon{0}'.format(uuid)).hexdigest()
        hshhh = hashlib.sha224('hexadragon{0}'.format(uuid).encode()).hexdigest()
        if key == hshhh:
            valid = True

    return key, valid


def get_key_and_licences():
    key_path = os.path.join(BASE_DIR, '.key')
    key = None
    licences = 0
    if os.path.exists(key_path):
        with open(key_path) as f:
            key = f.readline().replace('\n', '')
    if key:
        uuid = get_uuid()
        i = 0
        while i <= 100:
            i += 1
            test_sha = hashlib.sha224('hexadragon{0}+{1}'.format(uuid, i)).hexdigest()
            if test_sha == key:
                licences = i

    return key, licences


def get_uuid(ip='localhost'):
    if (ip=='localhost'):
        uuid = subprocess.check_output("cat /proc/cpuinfo | grep ^Serial | awk {'print $3'}", shell=True).decode("utf-8").replace('\n', '')
        return uuid
    uuid_raw = execute_ssh(ip, "cat /proc/cpuinfo | grep ^Serial | awk {'print $3'}", 'out')
    return uuid_raw.replace('\n', '')


def get_volume(ip='localhost'):
    try:
        err = execute_ssh(ip, "ls {}".format(IPC_AUDIO), "out")

        if not err:
            return None

        volume_json = execute_ssh(
            ip,
            "echo '{\"command\": [\"get_property\", \"volume\"]}' | socat - " + IPC_AUDIO,
            'out'
        )

        volume_data = json.loads(volume_json)

        if volume_data["error"] != "success":
            return None
        else:
            return float(volume_data["data"])

    except:
        return None


def set_volume(ip='localhost', new_volume=75):
    try:
        err = execute_ssh(ip, "ls {}".format(IPC_AUDIO), "out")

        if not err:
            return None

        execute_ssh(
            ip,
            "echo {0} > /var/starko/.vol && echo '{{\"command\": [\"set_property\", \"volume\", {0}]}}' | socat - {1}".format(
                new_volume,
                IPC_AUDIO
            ),
            'out'
        )

        return get_volume(ip)
    except:
        return None


def process_mpv_json(raw_json):
    """Обрабатываем вывод mpv"""
    try:
        data = json.loads(raw_json)

        if "/var/starko/media/" in data["data"]:
            return data["data"].replace("/var/starko/media/", "")

        if data["error"] == "success":
            for key in data["data"].keys():
                if "name" in key or "title" in key:
                    return data["data"][key]

        return None

    except:
        return None


def current_song(ip="localhost"):
    try:
        err = execute_ssh(ip, "ls {}".format(IPC_AUDIO), "out")
        if err:
            meta_json = execute_ssh(
                ip,
                "echo '{\"command\": [\"get_property\", \"metadata\"]}' | socat - " + IPC_AUDIO,
                "out"
            )

            song = process_mpv_json(meta_json)

            if song is not None:
                return song

            path_json = execute_ssh(
                ip,
                "echo '{\"command\": [\"get_property\", \"path\"]}' | socat - " + IPC_AUDIO,
                "out"
            )

            song = process_mpv_json(path_json)

            if song is not None:
                return song

        current_spotify_raw = execute_ssh(
            ip,
            "systemctl status spotifyd | tail -1",
            "out"
        )

        if "loaded" in current_spotify_raw:
            return re.findall(r"<(.*?)>", current_spotify_raw)[0]

        else:
            return ""

    except:
        return ""


def current_image(ip="localhost"):
    """Делаем скрин mpv и возвращаем путь до него"""
    try:
        err = execute_ssh(ip, "ls {}".format(IPC_VIDEO), "out")

        if not err:
            return None

        raw_response = execute_ssh(
            ip,
            "rm -f /var/www/static/screen/* && echo '{{\"command\": [\"screenshot\"]}}' | socat - {} && ls /var/www/static/screen/".format(IPC_VIDEO),
            "out"
        )

        for line in raw_response.split("\n"):
            if ".jpg" in line:
                return line.replace("\n", "")

        return None

    except:
        return None


def is_master():
    if Host.objects.count():
        return True
    else:
        return False


def get_timezone_etc_timezone():
    if os.path.exists("/etc/timezone"):
        try:
            tz = open("/etc/timezone", 'w').read().strip()
            try:
                return tz
            except IOError as ei:
                return None

        # Problem reading the /etc/timezone file
        except IOError as eo:
            return None

def get_conf_obj():
    hosts = Host.objects.all().order_by('id')
    hosts_json = []
    hosts_without_uuid = []  # это спец объект для вычисления сха ключа, т.к. UUID мы можем не получить от коробки, а сха от этого поменяться не должен
    master_uuid = get_uuid()
    for host in hosts:
        hds = HostDiagState.objects.get(host=host)
        host_uuid = get_uuid(host.ip) if hds.ping else None
        host_json = host.as_json()
        monitors = Monitor.objects.filter(host=host).order_by('id')
        monitors_json = [mon.as_json() for mon in monitors]
        host_json['monitors'] = monitors_json

        if host_uuid == master_uuid:
            host_json['is_master'] = True
        else:
            host_json['is_master'] = False
        hosts_without_uuid.append(deepcopy(host_json))
        host_json['uuid'] = host_uuid
        hosts_json.append(host_json)


    return hosts_json, hosts_without_uuid


def get_version():
    ver_file_path = os.path.join(MEDIA_ROOT, MC_PATCH_FOLDER, '.service', '.ver')
    try:
        with open(ver_file_path) as f:
            ver = f.readline().replace('\n', '')
            return ver
    except:
        if MEDIA_ROOT:
            with open(ver_file_path, "a") as myfile:
                myfile.write("1.0")
                myfile.write('\n')
        return "1.0"


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def get_mon_res(host_id, mon_slot_id, return_first=False):
    """
    возвращает макс.разрешение монитора, подключенного к слоту mon_slot хоста host
    """
    cmd_dmt = "tvservice -m DMT"
    cmd_cea = "tvservice -m CEA"
    cmd_xrandr = "xrandr -d :0"
    host = Host.objects.get(id=host_id)

    if host.is_nuc:
        cmd_tmpl = "cat /sys/class/drm/card0-HDMI-A-{0}/modes"
        hdmi_num = 1 if int(mon_slot_id) == 0 else 2
        cmd_str = cmd_tmpl.format(hdmi_num)
        host = Host.objects.get(id=host_id)

        try:
            raw_res = execute_ssh(host.ip, cmd_str, type_of_return="out")
            no_empty_res = filter(lambda a: a != "", raw_res.split("\n"))
            no_i_res = [i.replace("i", "") for i in no_empty_res]
            arr_res = list(set(no_i_res))
            arr_res.sort(key=lambda a: int(a.split("x")[0]), reverse=True)

        except:
            return []

        if return_first:
            if len(arr_res):
                return arr_res[0]
            else:
                return None

        return arr_res

    else:
        raw_res = ""

        try:
            raw_res = execute_ssh(host.ip, cmd_xrandr, type_of_return="out")
            pat = re.compile("\d+x\d+")
            no_i_res = pat.findall(raw_res)

        except:
            return []

        #no_i_res += ["3840x2160", "2560x1440", "1920x1080p", "1920x1080i", "1280x720p"]
        no_i_res = list(set(no_i_res))
        no_i_res.sort(key=lambda a: int(a.split("x")[0]), reverse=True)

        if return_first:
            if len(no_i_res):
                return no_i_res[0]
            else:
                return None

    return no_i_res


def get_mon_default_res(host_id, mon_slot_id):
    """
    возвращает макс.разрешение монитора, подключенного к слоту mon_slot хоста host
    """
    cfg_res = get_mon_res(host_id, mon_slot_id, return_first=True)
    if not cfg_res:
        cfg_res = '1920x1080'
    return cfg_res
