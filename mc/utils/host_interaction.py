# -*- coding: utf-8 -*-
import socket
import subprocess
from datetime import datetime, timedelta, time
import json
import logging
import os
import cv2
from django_starko.settings import MEDIA_ROOT, MC_LOCAL_BUFFER_DIR, \
    STATIC_ROOT, MC_PATCH_FOLDER, MC_LOCAL_FILES_DIR, MC_LOCAL_FILES_ROOT, MC_WORK_USER, MC_WORK_USER_PASSWORD, \
    DEBUG
from mc.models import Item, Host, Monitor, Playlist, Blackout, Setting, vWallPixel, RebootsData
from mc.utils import get_uuid, delete_file, copy_file, execute_ssh, make_sure_path_exists, get_mon_default_res, \
    link_files
from mc.utils.diag import is_mon_ok
from mc.utils.media import resize_img

logger = logging.getLogger(__name__)


def apply_all_hosts():
    hosts = Host.objects.all()
    for host in hosts:
        try:
            apply_host(host)
        except Exception as e:
            logger.error('Host {0} was not applied'.format(host.name))
            logger.error(e)


def apply_all_hosts_blackout():
    hosts = Host.objects.all()
    for host in hosts:
        try:
            apply_host(host, copy_files=False)
        except Exception as e:
            logger.error('Host {0} was not applied'.format(host.name))
            logger.error(e)

def calc_vw_borders(vw_x, vw_y, x, y, border):
    half_border = round(border/2)
    top = 0 if y == 1 else half_border
    left = 0 if x == 1 else half_border
    bottom = 0 if y == vw_y else half_border
    right = 0 if x == vw_x else half_border
    return left, right, top, bottom

def treat_video_wall(mon):
    try:
        fade_time = Setting.objects.get(code='fade_time').value
    except Setting.DoesNotExist:
        fade_time = 0.4

    copy_files = True
    err = u''
    pl_files_to_clean = []
    master_script = {
        "ips": [],
        "pls": []
    }
    pl_length = 0

    vw_pixels = vWallPixel.objects.filter(monitor=mon)

    #массив для хранения мониторной части скрипта запуска
    mon_scripts = []

    pls = Playlist.objects.filter(monitor=mon).exclude(item=None).order_by('-time_begin')
    #массив для хранения плейлистной части скрипта запуска
    pl_scripts = []
    pl_string = None
    for pl in pls:
        master_script["pls"].append({
            "length": 0,
            "start": pl.time_begin.strftime('%H:%M')
        })

        cur_pl = master_script["pls"][-1]

        pl_filename = 'pl_{0}'.format(pl.id)
        pl_filepath = os.path.join(STATIC_ROOT, 'mc/bashes/{0}'.format(pl_filename))

        item_abs_addr = []
        item_local_addr = []

        items_arr = []

        for item in Item.objects.filter(playlist=pl).order_by('sequence'):
            if not os.path.exists(item.file.data.path):
                continue
            _, fname = os.path.split(item.file.data.path)
            item_abs_addr.append(item.file.data.path)

            vid_len = None
            if item.type == 'video':
                cap = cv2.VideoCapture(item.file.data.path)
                frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                vid_len = int(frames/fps)

            item_local_addr.append(os.path.join(
                MC_LOCAL_FILES_DIR,
                os.path.basename(item.file.data.path)
            ))

            length = vid_len if vid_len else pl.interval / 1000 if pl.interval else 30

            cur_pl["length"] += int(float(length))

            items_arr.append({
                'name': fname,
                'type': 'vid' if item.type == 'video' else 'img' if item.type == 'image' else 'aud',
                'len': length
            })

        for host in vw_pixels:
            if item_abs_addr and copy_files:
                copy_file(host.ip_address, item_abs_addr, MC_LOCAL_BUFFER_DIR)

        #подотрем за собой
        pl_files_to_clean.append(pl_filepath)

        pl_script = dict(
            id=pl.id,
            type=pl.content_type,
            interval=pl.interval / 1000 if pl.interval else 3,
            files=items_arr,
            shuffle=pl.shuffle,
            time_begin=pl.time_begin.strftime('%H:%M'),
            fade_time=fade_time,
            scale_factor=pl.scale_factor,
            launch_string=pl_string,
            volume=pl.volume
        )

        pl_scripts.append(pl_script)

        bl_scripts = create_bl_list()

        mon_script = dict(
            id=mon.id,
            slot=mon.host_slot,
            orientation=MON_ROTATE_CONST[mon.orientation],
            playlists=pl_scripts,
            blackouts=bl_scripts,
            music_box=mon.music_box,
            current_pl_id=None
        )

        mon_scripts.append(mon_script)

    try:
        reboot_param = Setting.objects.get(code='reboot').value
    except Setting.DoesNotExist:
        reboot_param = None
    #а этот словарь - состояние плейлиста
    result = u''
    for host in vw_pixels:
        master_script["ips"].append(host.ip_address)

        host_script = dict(
            monitors=mon_scripts,
            blackout_apply=False if copy_files else True,
            reboot_param=reboot_param,
            video_wall=True,
            video_wall_x=mon.video_wall_x,
            video_wall_y=mon.video_wall_y,
            vw_pixel_x=host.x_pos,
            vw_pixel_y=host.y_pos,
            device_ip=host.ip_address,
            border=mon.video_wall_borders,
            inverted=host.inverted,
            change_time=str(datetime.now()),
            postpone_change=str(datetime.now()+timedelta(seconds=60))
        )

        json_host_script = json.dumps(host_script)
        script_file_path = os.path.join(STATIC_ROOT, 'mc/bashes/.{}'.format(host.hostname))
        with open(script_file_path, "w") as myfile:
            myfile.write(json_host_script)
        copy_file(host.ip_address, script_file_path, os.path.join(MC_LOCAL_FILES_ROOT, '.update'))

        err += execute_ssh(host.ip_address, 'chmod -R a+r {0}'.format(MC_LOCAL_BUFFER_DIR))
        #out_text = execute_ssh(host.ip, 'killall Xorg')
        if not DEBUG:
            # delete_file(bashrc_path)
            delete_file(script_file_path)
            for pl_file in pl_files_to_clean:
                delete_file(pl_file)

        result += err if err else 'ok'
    return result, master_script


MON_ROTATE_CONST = dict(standard=0, left=90, right=270, inverted=180)

def treat_nuc(host, copy_files=True):
    command_arr = []
    err = u''
    pl_image_tmpl = 'cat {0} | pqiv -P {1},0 -ir{2} --disable-scaling >> /var/log/pqiv/pqiv.log 2>&1'
    pl_video_tmpl = 'mpv --playlist={0} --geometry={1}+{2}+0 >> /var/log/mpv/mpv.log 2>&1'
    horizontal_shift = '0'
    #mon_pre_setup_tmpl = 'xrandr -d $DISPLAY --addmode HDMI1 {left_mon_res} > /dev/null 2>&1 && xrandr -d $DISPLAY --addmode HDMI2 {right_mon_res} > /dev/null 2>&1 &'
    mon_setup_tmpl = 'xrandr -d $DISPLAY --output HDMI1 {left_mon_mode} --auto --rotate {left_mon_str} --left-of HDMI2 --output HDMI2 {right_mon_mode} --auto --rotate {right_mon_str} > /dev/null 2>&1'
    #дефолтные значения
    left_mon_str = 'normal'
    right_mon_str = 'normal'
    left_mon_res = '1920x1080'
    left_mon_mode = ''
    right_mon_mode = ''
    pl_files_to_clean = []

    #для начала получим монитор
    #а с помощью монитора получим хост
    #очистим папку медиа на хосте
    execute_ssh(host.ip, 'rm {0}'.format(os.path.join(MC_LOCAL_BUFFER_DIR, '*')))
    #принудительно выставим владельца существующим файлам плейлистов
    pls_path = os.path.join(STATIC_ROOT, 'mc/bashes/')
    execute_ssh(host.ip, 'chown -R {0}:{1} {2}'.format('www-data', 'www-data', pls_path))
    execute_ssh(host.ip, 'chmod -R a+r {0}'.format(pls_path))


    mons = Monitor.objects.filter(host=host).order_by('host_slot')
    #массив для хранения мониторной части скрипта запуска
    mon_scripts = []
    mon_count = 0

    for mon in mons:
        #для начала проверим здоровьишко монитора
        mon_health, _waste, _wasted = is_mon_ok(mon)
        #если оно не ок, то не будем на него ничего отправлять (и сдвигать обратно не придется)
        if not mon_health:
            continue

        #если разрешение не выбрано в справочнике, получим по-умолчанию
        if not mon.resolution:
            mon.resolution = get_mon_default_res(host.id, mon.host_slot)
        else:
            #если выбрано, дополним строку запуска параметрами разрешения
            if mon.host_slot == 0:
                left_mon_mode = '--mode {0}'.format(mon.resolution)
            else:
                right_mon_mode = '--mode {0}'.format(mon.resolution)


        if mon.host_slot == 0:
            if mon.orientation == 'left':
                left_mon_str = 'right'
            elif mon.orientation == 'right':
                left_mon_str = 'left'
            elif mon.orientation == 'inverted':
                left_mon_str = 'inverted'
            left_mon_res = mon.resolution
        elif mon.host_slot == 1:
            if mon.orientation == 'left':
                right_mon_str = 'right'
            elif mon.orientation == 'right':
                right_mon_str = 'left'
            elif mon.orientation == 'inverted':
                right_mon_str = 'inverted'

        if mon_count != 0:
            mon_shift_idx = 1 if left_mon_str in ('left','right') else 0
            horizontal_shift = left_mon_res.split('x')[mon_shift_idx]


        pls = Playlist.objects.filter(monitor=mon).exclude(item=None).order_by('-time_begin')
        #массив для хранения плейлистной части скрипта запуска
        pl_scripts = []
        pl_string = None
        for pl in pls:
            if Item.objects.filter(playlist=pl, type='image').exists():
                pl.content_type = 'image'
            else:
                pl.content_type = 'video'
            pl_filename = 'pl_{0}'.format(pl.id)
            pl_filepath = os.path.join(STATIC_ROOT, 'mc/bashes/{0}'.format(pl_filename))
            pl_result_filepath = os.path.join(MC_LOCAL_FILES_DIR, pl_filename)

            item_count = Item.objects.filter(playlist=pl).count()
            #пустой плейлист игнорируем
            if not item_count:
                continue

            mon_dims = mon.resolution.split('x')

            if pl.content_type == 'image':
                if item_count > 1:
                    pl_slideshow_arg = 'Fs -d {0} --fade-duration=0.3'.format(pl.interval/1000)
                else:
                    pl_slideshow_arg = ''
                pl_string = pl_image_tmpl.format(pl_result_filepath, horizontal_shift, pl_slideshow_arg)
            else:
                if mon.orientation in ('left', 'right'):
                    mon.resolution = '{0}x{1}'.format(mon_dims[1], mon_dims[0])
                pl_string = pl_video_tmpl.format(pl_result_filepath, mon.resolution, horizontal_shift)
            item_abs_addr = []
            item_local_addr = []

            #предварительно почистим папку с ресайзнутыми картинками (ибо все равно каждый раз их ресайзим
            dir = os.path.join(MEDIA_ROOT,'monitors','mon_{0}'.format(mon.id))
            make_sure_path_exists(dir)
            err += execute_ssh('localhost', 'rm {0}/* -f'.format(dir))

            for item in Item.objects.filter(playlist=pl).order_by('sequence'):
                if not os.path.exists(item.file.data.path):
                    continue
                if pl.content_type == 'image':
                    #resize картинки под разрешение монитора
                    _, fname = os.path.split(item.file.data.path)

                    rsz_width, rsz_height = (mon_dims[1], mon_dims[0]) if mon.orientation in ('left', 'right') else (mon_dims[0], mon_dims[1])
                    rsz_filepath = os.path.join(dir,fname)
                    resize_img(item.file.data.path, rsz_filepath, rsz_width, rsz_height)
                    item_abs_addr.append(rsz_filepath)
                else:
                    item_abs_addr.append(item.file.data.path)

                item_local_addr.append(os.path.join(MC_LOCAL_FILES_DIR, os.path.basename(item.file.data.path)))

            if item_abs_addr and copy_files:
                copy_file(host.ip, item_abs_addr, MC_LOCAL_BUFFER_DIR)

            with open(pl_filepath, "w") as myfile:
                for item in item_local_addr:
                    myfile.write(item.encode('utf8'))
                    myfile.write('\n')
            copy_file(host.ip, pl_filepath, MC_LOCAL_BUFFER_DIR)
            #подотрем за собой
            pl_files_to_clean.append(pl_filepath)

            pl_script = dict(
                id=pl.id,
                time_begin=pl.time_begin.strftime('%H:%M'),
                launch_string = pl_string
            )
            pl_scripts.append(pl_script)

        if not pl_scripts:
            pl_string = 'ls /var/starko/blackscreen_opteo.png |pqiv -P {0},0 -ir >> /var/log/pqiv/pqiv.log 2>&1'.format(horizontal_shift)
            pl_script = dict(
                id=0,
                time_begin='06:00',
                launch_string = pl_string
            )
            pl_scripts.append(pl_script)

        bl_scripts = create_bl_list()

        mon_script = dict(
            id=mon.id,
            slot=mon.host_slot,
            orientation=mon.orientation,
            playlists=pl_scripts,
            blackouts=bl_scripts,
            current_pl_id=None)
        mon_scripts.append(mon_script)
        if pl_string:
            command_arr.append(pl_string)

        mon_count += 1

    #mon_pre_setup_str = mon_pre_setup_tmpl.format(left_mon_res=left_mon_res, right_mon_res=right_mon_res)
    mon_setup_str = mon_setup_tmpl.format(left_mon_mode=left_mon_mode, right_mon_mode=right_mon_mode,
                                              left_mon_str=left_mon_str, right_mon_str=right_mon_str)

    from shutil import copy
    bashrc_path = os.path.join(STATIC_ROOT, 'mc/bashes/.bashrc_{0}'.format(host.id))

    copy(os.path.join(STATIC_ROOT, 'mc/bashes/scripts/bashrc_tmpl'), bashrc_path)
    with open(bashrc_path, "a") as myfile:
        myfile.write(mon_setup_str)
        myfile.write('\n')

    cur_ip = execute_ssh("localhost", "hostname -I", "out").strip().split(" ")[0]
    #а этот словарь - состояние плейлиста
    host_script = dict(
        monitors=mon_scripts,
        blackout_apply=False if copy_files else True,
        change_time=str(datetime.now()),
        master_ip=cur_ip
    )

    json_host_script = json.dumps(host_script)
    script_file_path = os.path.join(STATIC_ROOT, 'mc/bashes/.{}'.format(host.name))
    with open(script_file_path, "w") as myfile:
        myfile.write(json_host_script)
    copy_file(host.ip, script_file_path, os.path.join(MC_LOCAL_FILES_ROOT, '.update'))

    copy_file(host.ip, bashrc_path, '/var/{0}/.bashrc_tmpl'.format(MC_WORK_USER))
    err += execute_ssh(host.ip, 'chown {0}:{1} /home/{2}/.bashrc'.format(MC_WORK_USER,MC_WORK_USER_PASSWORD,MC_WORK_USER))
    err += execute_ssh(host.ip, 'chmod -R a+r {0}'.format(MC_LOCAL_BUFFER_DIR))
    #out_text = execute_ssh(host.ip, 'killall Xorg')
    if not DEBUG:
        delete_file(bashrc_path)
        delete_file(script_file_path)
        for pl_file in pl_files_to_clean:
            delete_file(pl_file)

    result = err if err else 'ok'
    return result

def apply_host(host, copy_files=True, sync_group=False, only_copy_files=False):
    try:
        fade_time = Setting.objects.get(code='fade_time').value
    except Setting.DoesNotExist:
        fade_time = 0.4

    try:
        audio_buffer = Setting.objects.get(code="audio_buffer").value
    except Setting.DoesNotExist:
        audio_buffer = 5

    try:
        video_buffer = Setting.objects.get(code="video_buffer").value
    except Setting.DoesNotExist:
        video_buffer = 5

    if (host.is_nuc):
        result_nuc = treat_nuc(host, copy_files)
        return result_nuc

    command_arr = []
    err = u''
    cur_ip = execute_ssh("localhost", "hostname -I", "out").strip().split(" ")[0]
    # дефолтные значения
    pl_files_to_clean = []

    # для начала получим монитор
    # а с помощью монитора получим хост
    # очистим папку медиа на хосте
    # и процесс для видеостен
    if copy_files:
        execute_ssh(host.ip, 'rm {0}'.format(os.path.join(MC_LOCAL_BUFFER_DIR, '*')))
        execute_ssh(host.ip, "echo -n '' > /var/starko/vw_master_pl")
        execute_ssh(host.ip, "kill $(pgrep -f 'python3 /var/starko/mpv-videowall/master.py')")
        execute_ssh(host.ip, "rm /tmp/master-*")

    #принудительно выставим владельца существующим файлам плейлистов
    pls_path = os.path.join(STATIC_ROOT, 'mc/bashes/')
    execute_ssh(host.ip, 'chown -R {0}:{1} {2}'.format('www-data', 'www-data', pls_path))
    execute_ssh(host.ip, 'chmod -R a+r {0}'.format(pls_path))

    mons = Monitor.objects.filter(host=host).order_by('host_slot')
    #массив для хранения мониторной части скрипта запуска
    mon_scripts = []
    mon_count = 0

    sync_pl_data = {
        "ips": [],
        "pls": []
    }

    for mon in mons:
        mon_res_is_default = False
        # если это видео-стена, действуем по-другому
        if mon.video_wall:
            _, script = treat_video_wall(mon)
            execute_ssh(
                mon.host.ip,
                "echo '{}' > /var/starko/vw_master_pl".format(
                    json.dumps(script)
                )
            )

            result = err if err else 'ok'
            return result

        if not sync_group and mon.sync_group:
            # тут у нас рекурсивный вызов применения плейлиста, для всех ХОСТОВ синх-группы, чтобы не попасть в вечную рекурсию, передаём в apply_host соотв. переменную (sync_group)

            sync_hosts = Host.objects.filter(monitor__sync_group=mon.sync_group).order_by('id')

            # кроме того, чтобы не запускать цикл с КАЖДОГО хоста в группе синх, будем всегда запускать только с первого по списку
            if host == sync_hosts[0]:
                # сначала копирнём файлы на каждый хост синх-группы
                for s_host in sync_hosts:
                    sync_data = apply_host(s_host, sync_group=True, only_copy_files=True)

                sync_data["ips"] = [host.ip for host in sync_hosts]
                execute_ssh(
                    mon.host.ip,
                    "echo '{}' > /var/starko/vw_master_pl".format(
                        json.dumps(sync_data)
                    )
                )

                # а потом быстренько применим каждый хост
                for s_host in sync_hosts:
                    res = apply_host(s_host, sync_group=True, copy_files=False)

            result = err if err else 'ok'
            return result
        #для начала проверим здоровьишко монитора
        mon_health, _waste, _waste2 = is_mon_ok(mon)
        #если оно не ок, то не будем на него ничего отправлять (и сдвигать обратно не придется)
        if not mon_health:
            continue
        #если разрешение не выбрано в справочнике, получим по-умолчанию
        if not mon.resolution:
            mon.resolution = get_mon_default_res(host.id, mon.host_slot)
            mon_res_is_default = True


        pls = Playlist.objects.filter(monitor=mon).exclude(item=None).order_by('-time_begin')
        #массив для хранения плейлистной части скрипта запуска
        pl_scripts = []
        pl_string = None
        # предварительно почистим папку с ресайзнутыми картинками (ибо все равно каждый раз их ресайзим
        dir = os.path.join(MEDIA_ROOT, 'monitors', 'mon_{0}'.format(mon.id))
        make_sure_path_exists(dir)
        err += execute_ssh('localhost', 'rm {0}/* -f'.format(dir))

        for pl in pls:
            sync_pl_data["pls"].append({
                "length": 0,
                "start": pl.time_begin.strftime("%H:%M")
            })

            mon_dims = mon.resolution.replace('i','').replace('p','').split('x')

            item_abs_addr = []
            item_local_addr = []
            items_arr = []

            for item in Item.objects.filter(playlist=pl).order_by('sequence'):
                if item.bitrate_violation:
                    continue

                if item.type == 'url':
                    items_arr.append({'name': item.url, 'type': 'url', 'is_site': item.is_site, 'is_script': item.is_script})
                    continue

                if not os.path.exists(item.file.data.path):
                    continue
                _, fname = os.path.split(item.file.data.path)

                if item.type == 'image':
                    #resize картинки под разрешение монитора
                    rsz_width, rsz_height = (mon_dims[1], mon_dims[0]) if mon.orientation in ('left', 'right') else (
                        mon_dims[0], mon_dims[1])
                    rsz_filepath = os.path.join(dir, fname)
                    resize_img(item.file.data.path, rsz_filepath, rsz_width, rsz_height)

                    if rsz_filepath not in item_abs_addr:
                        item_abs_addr.append(rsz_filepath)

                else:
                    if item.file.data.path not in item_abs_addr:
                        item_abs_addr.append(item.file.data.path)

                item_local_addr.append(os.path.join(
                    MC_LOCAL_FILES_DIR,
                    os.path.basename(item.file.data.path)
                ))

                item_length = item.file.duration if item.file.duration else pl.interval / 1000 if pl.interval else 30

                items_arr.append({
                    'name': fname,
                    'type': 'vid' if item.type == 'video' else 'img' if item.type == 'image' else 'aud',
                    'duration': item_length
                })

                sync_pl_data["pls"][-1]["length"] += item_length

            if item_abs_addr and copy_files:
                link_dont_copy = False
                for interface in ['eth0', 'wlan0']:

                    output = subprocess.check_output(["ifconfig {0} | grep inet | awk '{{print $2}}' | cut -d ':' -f2".format(interface)],
                                                        shell=True).decode("utf-8")
                    if host.ip == output.replace('\n', ''):
                        link_dont_copy = True

                if link_dont_copy:
                    link_files(item_abs_addr, MC_LOCAL_BUFFER_DIR)
                else:
                    copy_file(host.ip, item_abs_addr, MC_LOCAL_BUFFER_DIR)

            pl_script = dict(
                id=pl.id,
                type=pl.content_type,
                interval=pl.interval / 1000 if pl.interval else 3,
                fade_time=fade_time,
                audio_buffer=audio_buffer,
                video_buffer=video_buffer,
                files=items_arr,
                shuffle=pl.shuffle,
                is_adv=pl.is_adv,
                volume=pl.volume,
                adv_at_once=pl.adv_at_once,
                time_begin=pl.time_begin.strftime('%H:%M'),
                scale_factor=pl.scale_factor,
                url_refresh_mode=pl.url_refresh_mode,
                launch_string=pl_string
            )

            pl_scripts.append(pl_script)

        bl_scripts = create_bl_list()

        mon_script = dict(
            id=mon.id,
            slot=mon.host_slot,
            orientation=MON_ROTATE_CONST[mon.orientation],
            resolution=mon.resolution if not mon_res_is_default else None,
            playlists=pl_scripts,
            blackouts=bl_scripts,
            music_box=mon.music_box,
            spotify=mon.spotify,
            volume_locked=mon.volume_locked,
            current_pl_id=None,
            audio_output=mon.audio_output,
            hdmi_mode="CEA 20" if mon.resolution == '1920x1080i' else "CEA 31" if mon.resolution=='1920x1080p' else "CEA 19" if mon.resolution == '1280x720p' else None
        )

        mon_scripts.append(mon_script)
        if pl_string:
            command_arr.append(pl_string)

        mon_count += 1

    if only_copy_files:
        sync_pl_data["pls"] = {
            pl["start"]: pl for pl in sync_pl_data["pls"]
        }.values()

        return sync_pl_data

    try:
        reboot_param = Setting.objects.get(code='reboot').value
    except Setting.DoesNotExist:
        reboot_param = None

    #а этот словарь - состояние плейлиста
    host_script = dict(
        monitors=mon_scripts,
        blackout_apply=False if copy_files else True,
        reboot_param=reboot_param,
        master_ip=cur_ip,
        device_ip=host.ip,
        change_time=str(datetime.now()),
        postpone_change=str(
            datetime.now() + timedelta(seconds=60)
        ) if sync_group else None,
        sync_group=sync_group
    )

    json_host_script = json.dumps(host_script)
    script_file_path = os.path.join(
        STATIC_ROOT,
        'mc/bashes/.{}'.format(host.name)
    )

    with open(script_file_path, "w") as myfile:
        myfile.write(json_host_script)
    copy_file(host.ip, script_file_path, os.path.join(MC_LOCAL_FILES_ROOT, '.update'))

    err += execute_ssh(host.ip, 'chmod -R a+r {0}'.format(MC_LOCAL_BUFFER_DIR))
    #out_text = execute_ssh(host.ip, 'killall Xorg')
    if not DEBUG:
        # delete_file(bashrc_path)
        delete_file(script_file_path)
        for pl_file in pl_files_to_clean:
            delete_file(pl_file)

    result = err if err else 'ok'
    return result


def patch_peasants(fname):
    """
    Функция-патчер слейвов. Копирует файл патча на всех своих рабов
    и создает на них же файл .lock
    :param fname: имя патча
    :return:
    """
    hosts = Host.objects.all()
    master_uuid = get_uuid()
    lock_path = os.path.join(STATIC_ROOT, "mc/bashes/scripts/lock")
    patch_path = os.path.join(MEDIA_ROOT, MC_PATCH_FOLDER)
    now = datetime.now()
    RebootsData.objects.all().delete()

    for host in hosts:
        host_uuid = get_uuid(host.ip)
        RebootsData(start=now, host=host).save()

        if host_uuid == master_uuid:
            # себя второй раз не патчим
            continue

        try:
            copy_file(host.ip, os.path.join(patch_path, fname), patch_path)
            copy_file(host.ip, lock_path, os.path.join(patch_path, ".lock"))
            execute_ssh(host.ip, "date > /var/www/.reboot")

        except Exception as e:
            logger.error("Applying patch to slave {0}".format(host.ip))
            logger.error(e)
            raise


def all_hosts_obey(command_for_all, command_for_master=None):
    """Посылаем команду по SSH для всех хостов"""
    logger = logging.getLogger(__name__)
    hosts = Host.objects.all()
    master_uuid = get_uuid()
    log = u""

    for host in hosts:
        try:
            host_uuid = get_uuid(host.ip)
            if host_uuid == master_uuid:
                continue

            log += u"executing {0} at {1} \n".format(command_for_all, host.ip)
            log += execute_ssh(host.ip, command_for_all, "out")

        except Exception as e:
            logger.error("Command {0} at host {1} was not applied".format(
                command_for_all,
                host.name
            ))
            logger.error(e)

    log += u"executing {0} at localhost \n".format(command_for_all)
    log += execute_ssh("localhost", command_for_all, "out")

    if command_for_master:
        log += u"shutting web at localhost \n"
        log += execute_ssh("localhost", command_for_master, "out")

    logger.warning(log)


def all_hosts_lock():
    all_hosts_obey(
        "mv /home/starko/.bashrc /home/starko/.bashrc_tmp && pkill X",
        "rm /etc/nginx/sites-enabled/django_starko.conf && service nginx restart"
    )


def all_hosts_unlock():
    all_hosts_obey(
        "mv /home/starko/.bashrc_tmp /home/starko/.bashrc && pkill X",
        "cd /etc/nginx/sites-enabled/ && ln -s /etc/nginx/sites-available/django_starko.conf && service nginx restart"
    )


def get_master_host():
    """Возвращает мастера из списка хостов"""
    hosts = Host.objects.all()
    master_ips = ["127.0.0.1"]
    master_ips.append(execute_ssh("localhost", "hostname -I", "out").strip().split(" ")[0])

    for host in hosts:
        if host.ip in master_ips:
            return host

    return None


def all_hosts_reboot():
    """Отправляем команду на перезагрузку всех хостов"""
    command = "sync;date > /var/www/.reboot;reboot -f > /dev/null 2>&1 &"
    now = datetime.now()
    RebootsData.objects.all().delete()

    # Заранее создадим запись для мастера
    master_host = get_master_host()
    RebootsData(start=now, host=master_host).save()

    # Не нашли мастера, значит его нет в списке хостов
    if master_host is None:
        hosts = Host.objects.all()

    # В противном случае его надо исключить
    else:
        hosts = Host.objects.exclude(id=master_host.id)

    for host in hosts:
        try:
            # Для обычных хостов стучимся по SSH,
            # а потом создаем запись о перезагрузке
            execute_ssh(host.ip, command)
            RebootsData(start=now, host=host).save()

        except Exception as exc:
            # В противном случае сохраним данные,
            # что не получилось перезагрузить
            RebootsData(start=None, host=host).save()

    try:
        # После всех остальных перезагрузим мастера
        execute_ssh("localhost", command)

    except Exception as exc:
        # Если что-то пошло не так, то подправим запись
        master_reboot = RebootsData.objects.get(host=master_host)
        master_reboot.start = None
        master_reboot.save()


def create_bl_list():
    bl_scripts = []
    next_time_begin = None
    for bl in Blackout.objects.all().order_by('day_of_week'):
        # если у нас есть запись для всех дней
        if not bl.day_of_week:
            #только её одну и запишем, остальные смотреть не будем
            if bl.time_end < bl.time_begin:
                bl_script_1 = dict(
                    time_begin=bl.time_begin.strftime('%H:%M'),
                    time_end='00:00',
                    day_of_week=0
                )
                bl_scripts.append(bl_script_1)
                if bl.time_end != time(0, 0, 0):
                    bl_script_2 = dict(
                        time_begin='00:00',
                        time_end=bl.time_end.strftime('%H:%M'),
                        day_of_week=0
                    )
                    bl_scripts.append(bl_script_2)
            else:
                bl_script = dict(
                    time_begin=bl.time_begin.strftime('%H:%M'),
                    time_end=bl.time_end.strftime('%H:%M'),
                    day_of_week=0
                )
                bl_scripts.append(bl_script)
            return bl_scripts

        else:
            #если у нас есть записи, принадлежащие дню, поебёмся
            if bl.time_end < bl.time_begin:
                bl_script_1 = dict(
                    time_begin=next_time_begin if next_time_begin else '00:00',
                    time_end=bl.time_end.strftime('%H:%M'),
                    day_of_week=(bl.day_of_week) if (bl.day_of_week) <= 7 else 1
                    # это выключение закончится уже завтра %))))))))))
                )
                bl_scripts.append(bl_script_1)
                bl_script_2 = dict(
                    time_begin=bl.time_begin.strftime('%H:%M'),
                    time_end='23:59',
                    day_of_week=bl.day_of_week
                )
                bl_scripts.append(bl_script_2)

            else:
                bl_script = dict(
                    time_begin='00:00',
                    time_end=bl.time_end.strftime('%H:%M'),
                    day_of_week=bl.day_of_week
                )
                bl_scripts.append(bl_script)
                next_time_begin = bl.time_begin.strftime('%H:%M')

    return bl_scripts


def apply_new_bl(bls):
    new_objs = []
    for item in bls:
        item.pop('day_of_week_str')
        obj = Blackout(**item)
        try:
            obj.full_clean()
            new_objs.append(obj)
        except Exception as e:
            logger.error(e)
            raise e

    Blackout.objects.all().delete()
    for obj in new_objs:
        obj.save()

    apply_all_hosts_blackout()
