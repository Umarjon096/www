# -*- coding: utf-8 -*-
import json
import subprocess
import os
from datetime import date, datetime, timedelta
from shutil import copy, move, rmtree, copytree
from copy import copy as objcopy
import socket
import fileinput
import sys
import time

from math import fabs

reload(sys)
sys.setdefaultencoding('utf8')


VW_PORT = "4444"

IPC_AUDIO = "/tmp/mpv-audio"
IPC_VIDEO = "/tmp/mpv-video"

MAX_VOLUME = 100


def rebootCheck(obj):
    restart_if_not_already = False
    reboot_param = obj.get('reboot_param')
    if not reboot_param:
        return
    day_str, time_str = reboot_param.split(' ')
    if not time_str:
        # если время перезагрузки не задано в параметре, ничего не делаем
        return
    time_obj = datetime.strptime(time_str, '%H:%M')
    new_time = time_obj.time()
    tz_now = datetime.now()
    day_now = tz_now.isoweekday()
    time_now = tz_now.time()

    if int(day_str) <= day_now and new_time <= time_now:
        restart_if_not_already = True
        days_delta = fabs(int(day_str) - day_now)
        real_day = tz_now.date() - timedelta(days=days_delta)
        real_datetime = datetime.combine(real_day, new_time)

    if restart_if_not_already:
        lr = obj.get('last_reboot')
        latest = datetime.strptime(lr, "%d.%m.%Y %H:%M") if lr else None

        if not latest:
            # первый раз не будем перезагружать
            obj['last_reboot'] = real_datetime.strftime("%d.%m.%Y %H:%M")
            return
        else:
            # если не первый раз, проверим, перезагружались ли мы уже для этого времени
            if latest >= real_datetime:
                # если мы уже перезапускались для указанного времени, ниче не делаем
                return
            else:
                # если нет, создаём запись в лог и перезагружаемся
                obj['last_reboot'] = real_datetime.strftime("%d.%m.%Y %H:%M")
                return True

def refreshCheck(obj, new_refresh_interval):
    print('chekin refresh')
    if new_refresh_interval != -1:
        obj['refresh_interval'] = new_refresh_interval

    if obj.get('refresh_interval') is None:
        return

    if obj['refresh_interval'] == 0:
        print('check url avail')
        f = open('/var/starko/media/playlist', "r")
        raw_file_str = f.read()
        obj = json.loads(raw_file_str)
        files = obj.get('files')
        if files:
            if files[0]["type"] == 'url':
                url_to_check = files[0]["name"]
                print('sending req')
                import requests
                r = requests.head(url_to_check, verify=False)
                url_avail = (r.status_code == 200)

                url_unavail_times = obj.get('url_unavail_times', 0)
                print(url_avail, url_unavail_times)
                if url_unavail_times > 1 and url_avail:
                    obj['url_unavail_times'] = 0
                    return True
                if not url_avail:
                    obj['url_unavail_times'] = url_unavail_times + 1

    lr = obj.get('last_refresh')
    tz_now = datetime.now()
    latest = datetime.strptime(lr, "%d.%m.%Y %H:%M") if lr else None
    print(tz_now, latest)
    if not latest:
        # первый раз не будем перезагружать
        obj['last_refresh'] = tz_now.strftime("%d.%m.%Y %H:%M")
        return

    if (latest + timedelta(minutes=obj['refresh_interval'])) < tz_now:
        obj['last_refresh'] = tz_now.strftime("%d.%m.%Y %H:%M")
        return True



def checkOrReplaceBoot(replaceExp):
    replaced = False
    found = False
    file = '/boot/config.txt'
    searchExp='display_rotate'
    for line in fileinput.input(file, inplace=1):
        if searchExp in line and not line.startswith('#'):
            found = True
            if replaceExp not in line:
                line = replaceExp + '\n'
                replaced = True
        sys.stdout.write(line)
    if not replaced and not found:
        replaced = True
        with open("/boot/config.txt", "a") as myfile:
            myfile.write(replaceExp)
            myfile.write('\n')

    return replaced


def reloadOrKill(state_object):
    print('reloadOrKill')
    scale_replaced = replaceScaleFactor(scale_factor)

    try:
        chromi_active = subprocess.check_output("pgrep chromium", shell=True).decode('utf-8').replace('\n', '')
    except subprocess.CalledProcessError as e:
        chromi_active = False
    #print('state', state_object)
    #print('ch extern c_saved', external, state_object.get('external'))
    if chromi_active and not scale_replaced and not external and external == state_object.get('external') and not resolution_changed:
        subprocess.Popen('refresh', shell=True)
    else:
        subprocess.Popen('pkill -KILL -u starko', shell=True)



def checkIP():
    ip_path = '/var/starko/media/_ip'
    ip = None
    if os.path.isfile(ip_path):
        f = open(ip_path, 'r')
        raw_file_str = f.read()
        f.close()
        ip = raw_file_str.replace('\n','')

    cur_ip = [(
        s.connect(('8.8.8.8', 53)),
        s.getsockname()[0],
        s.close()
    ) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]

    if not ip or cur_ip not in ip:
        with open('/var/starko/media/_ip', 'w') as ipfile:
            ipfile.write(cur_ip)
        return True


def blackscreenMaybe(rotation, old_obj):
    print('checkin blackscreen')
    pkill_needed = False #checkIP()
    if os.path.isfile('/var/starko/media/playlist') \
        or os.path.isfile('/var/www/static/chromi/playlist') \
        or os.path.isfile('/var/starko/media/m_playlist') \
        or os.path.isfile('/var/starko/media/mon_playlist'):
        if pkill_needed:
            print('IP CHANGED, RELOADING')
            reloadOrKill(old_obj)
        return

    pl = {"files": [{"type": "img", "name": "blackscreen_opteo.png", "duration": 600}], "start_time": datetime.now().isoformat(),
     "shuffle": False, "interval": 10, "type": "hybrid", "rotate": rotation, "blackscreen": True}

    if os.path.exists('/var/www/static/chromi') and not os.path.islink('/var/www/static/chromi'):
        rmtree('/var/www/static/chromi/')
        
    rmtree('/var/starko/media/')
    os.mkdir('/var/starko/media')
    os.chmod("/var/starko/media", 0o777)
    if not os.path.islink('/var/www/static/chromi'):
        os.symlink('/var/starko/media', '/var/www/static/chromi')

    copy(os.path.join(DIR, "vid3.html"), '/var/www/static/chromi/')

    with open('/var/starko/media/playlist', "w") as myfile:
        myfile.write(json.dumps(pl))

    copy(os.path.join(DIR, "blackscreen_opteo.png"), '/var/starko/media/')
    #copy(os.path.join(DIR, 'hybrid.lua'), os.path.join('/var/starko/media/node.lua'))
    #copy(os.path.join(DIR, 'FreeSans.ttf'), os.path.join('/var/starko/media/FreeSans.ttf'))

    #pkill_needed = checkIP()

    #result_command = "cd /var/starko/cec-menu/src && python cec_killer.py && sudo /var/starko/cec-menu.sh &\n"
    result_command = "xinit /home/starko/kiosk -- -nocursor vt$(fgconsole) > /dev/null 2>&1"
    # result_command += " && python cec_killer.py && sudo /var/starko/cec-menu.sh\n"
    # result_command += 'mpv /var/starko/media/blackscreen_opteo.png --sub-file=/var/starko/media/.ip --loop -- > /dev/null 2>&1 && sudo /var/starko/cec-menu.sh'

    copy(os.path.join(DIR, '.bashrc_tmpl'), os.path.join(DIR,'.bash_profile'))
    with open(os.path.join(DIR,'.bash_profile'), "a") as myfile:
        myfile.write(result_command)
        myfile.write('\n')
    copy(os.path.join(DIR,'.bash_profile'),'/home/starko/.bash_profile')
    #subprocess.Popen('rm -f /tmp/mpv*', shell=True)
    reloadOrKill(old_obj)


def check_volume(volume_locked=False):
    if not os.path.exists(IPC_AUDIO):
        return None

    try:
        cv_raw = subprocess.check_output(
            "echo '{\"command\": [\"get_property\", \"volume\"]}' | socat - " + IPC_AUDIO,
            shell=True
        )

        v_data = json.loads(cv_raw)

        cv = int(v_data["data"]) if v_data["error"] == "success" else 0
        true_vol = get_saved_volume() if not volume_locked else MAX_VOLUME

        if cv != true_vol:
            subprocess.Popen(
                "echo '{\"command\": [\"set_property\", \"volume\", {}]}' | socat - {}".format(
                    true_vol,
                    IPC_AUDIO
                ),
                shell=True
            )

    except:
        pass


def check_ntp(master_ntp):
    ntp_raw = subprocess.check_output(
        "sed -n '/#s_e/,/#s_m/{/#s_e/b;/#s_m/b;p}' /etc/chrony/chrony.conf",
        shell=True
    ).replace('server ', '').replace(' iburst', '').replace('\n', ',')

    if ntp_raw != master_ntp:
        try:
            subprocess.check_output('mount -o remount,rw /', shell=True)
        except subprocess.CalledProcessError:
            pass
        subprocess.check_output(
            "sed -n -i '/#s_e/{p;:a;N;/#s_m/!ba;s/.*\\n/server " + master_ntp + " iburst\\n/};p' /etc/chrony/chrony.conf",
            shell=True
        )

        try:
            subprocess.check_output('mount -o remount,ro /', shell=True)
        except subprocess.CalledProcessError:
            pass
        subprocess.Popen('service chrony restart', shell=True)


DIR = os.path.dirname(os.path.realpath(__file__))


def get_saved_volume():
    cur_vol = get_pl_volume()
    if not cur_vol:
        v_file_path = os.path.join(DIR, '.vol')
        if os.path.isfile(v_file_path):
            v_file = open(v_file_path, 'r')
            raw_cur_vol = v_file.read().strip()

            try:
                cur_vol = float(raw_cur_vol)
            except Exception as e:
                cur_vol = 1
                print(e.message)

        else:
            cur_vol = 1
    return cur_vol

def get_pl_volume():
    v_file_path = os.path.join(DIR, '.pl_vol')
    if os.path.isfile(v_file_path):
        v_file = open(v_file_path, 'r')
        raw_cur_vol = v_file.read().strip()

        try:
            cur_vol = float(raw_cur_vol)
        except Exception as e:
            cur_vol = None
            print(e.message)

    else:
        cur_vol = None
    return cur_vol

def save_pl_volume(volume):
    subprocess.check_output(
            "echo {0} > /var/starko/.pl_vol".format(volume),
            shell=True
        )


def set_fade_fps(image_frames, fade_frames, fade_out_start):
    """При помощи sed вставляем нужные значения в конфиг"""
    subprocess.check_output(
        "sed -i '/mf-fps=/c\\mf-fps={}' /var/starko/mpv-images.conf".format(
            MPV_FPS
        ),
        shell=True
    )

    subprocess.check_output(
        "sed -i '/vf=lavfi=/c\\vf=lavfi=[loop={0}:1:0,fade=t=in:s=0:n={1},fade=t=out:s={2}:n={1}]' /var/starko/mpv-images.conf".format(
            image_frames,
            fade_frames,
            fade_out_start
        ),
        shell=True
    )

def replaceScaleFactor(new_scale):
    cur_scale = subprocess.check_output("cat /home/starko/kiosk |grep scale-factor | awk -F '[= ]' {'print $2'}", shell=True).replace('\n', '')
    if float(cur_scale) == float(new_scale):
        print('SCALES EQUAL')
        return False
    print('REPLACING SCALE TO: ', new_scale)
    sed_str = "sed -i 's/--force-device-scale-factor=[0-9]*.[0-9]*\+/--force-device-scale-factor={}/'".format(new_scale)
    #print(sed_str+" /home/starko/kiosk")
    subprocess.check_output(sed_str+" /home/starko/kiosk", shell=True)
    return True

def check_audio_output():
    print('chekin sound')
    hdmi_sound = False
    audio_str = subprocess.check_output("cat /boot/config.txt |grep audio=on", shell=True).replace('\n', '')
    if '#' in audio_str:
        hdmi_sound = True
    print('hdmi sound enabled', hdmi_sound)
    print('pl sound', audio_output)
    if audio_output == 'hdmi' and not hdmi_sound:
        subprocess.check_output('mount -o remount,rw /', shell=True)
        subprocess.check_output("sed -i '/dtparam=audio=on/s/^/#/g' /boot/config.txt", shell=True)
        subprocess.check_output('mount -o remount,ro /', shell=True)
        subprocess.Popen('reboot', shell=True)
        time.sleep(1)
    if audio_output != 'hdmi' and hdmi_sound:
        subprocess.check_output('mount -o remount,rw /', shell=True)
        subprocess.check_output("sed -i '/dtparam=audio=on/s/^#//g' /boot/config.txt", shell=True)
        subprocess.check_output('mount -o remount,ro /', shell=True)
        subprocess.Popen('reboot', shell=True)
        time.sleep(1)
    print('sound checked')

def change_resolution(new_res):
    print('CHECK RES')
    cur_res = subprocess.check_output("cat /home/starko/kiosk |grep xrandr | awk -F '-s ' {'print $2'}", shell=True).replace('\n', '')
    if cur_res == '':
        cur_res = None
    print('cur_res', type(cur_res), cur_res)
    print('new_res', type(cur_res), new_res)
    if cur_res == new_res:
        print('RESOLUTIONS EQUAL')
        return False
    print('REPLACING RESOLUTION TO: ', new_res)
    if cur_res is not None and new_res is not None:
        sed_str = "sed -i 's/xrandr -d :0 -s [0-9]*x[0-9]*\w\?/xrandr -d :0 -s {}/'".format(new_res)
    else:
        if new_res is None and cur_res is not None:
            sed_str = "sed -i '3d'"
        if cur_res is None and new_res is not None:
            sed_str = "sed -i '3i xrandr -d :0 -s {}'".format(new_res)

    #print(sed_str+" /home/starko/kiosk")
    subprocess.check_output(sed_str+" /home/starko/kiosk", shell=True)
    return True

def launch_script(script):
    print('LAUNCH SERIAL')
    import serial
    ser = serial.Serial('/dev/ttyUSB0')  # open serial port
    print(ser.name)         # check which port was really used
    success = ser.write('{}\r'.format(script))     # write a string
    print('BYTES WRITTEN: ', success)
    ser.close()  



new_file_arrived = False
now = datetime.now()
now_day_of_week = now.isoweekday()

file = os.path.join(DIR, ".update")
current_file = os.path.join(DIR, ".current")

try:
    old_f = open(current_file, "r")
    old_raw_file_str = old_f.read()
    old_obj = json.loads(old_raw_file_str)
except Exception as e:
    old_obj = {}

if os.path.isfile(file):
    move(file,current_file)
    new_file_arrived = True

try:
    f = open(current_file, "r")
    raw_file_str = f.read()
    obj = json.loads(raw_file_str)

except Exception as e:
    rmtree("/var/starko/media/")
    os.mkdir("/var/starko/media")
    os.chmod("/var/starko/media", 0o777)
    obj = {}

if new_file_arrived and obj:
    master_ip = obj.get("master_ip")
    if master_ip:
        check_ntp(master_ip)

command_arr = []
pl_info = {}
aud_files = []
adv_files = []
adv_interval = 0
adv_at_once = False
shuffle_audio = False
shuffle_video = False
radio = False
music_box = False
spotify = False
need_change = False
empty = True
new_buffer = False
volume_locked = None
hdmi_mode = None
audio_output = None
external = False
interval = 30
scale_factor = 1.0
refresh_interval = -1
resolution_changed = False

OUTPUTS = {
    0: "",
    1: "local",
    2: "hdmi"
}

MPV_FPS = 30

exit_blackout = True

mon_rotate = None
postpone_change = False #obj.get("postpone_change")

if postpone_change:
    postpone_datetime = datetime.strptime(postpone_change, "%Y-%m-%d %H:%M:%S.%f")
    if postpone_datetime > datetime.today():
        sys.exit("Change postponed")

# если это применение блэкаута, то не будем тереть медиа
blackout_apply=obj.get("blackout_apply")

vwall = obj.get("video_wall", False)
vw_files = []

sync_group = obj.get("sync_group", False)

simple_mon = False
simple_pl = None

fade_time = 0
audio_buffer = 5
video_buffer = 5

#цикл по мониторам
for mon in obj.get("monitors", []):
    mon_res = mon.get("resolution")
    resolution_changed = change_resolution(mon_res)

    audio_output = OUTPUTS.get(mon.get("audio_output"))
    check_audio_output()

    mon_rotate = mon["orientation"]

    #проверим, не блэкаут ли сейчас
    rng = len(mon["blackouts"])
    for i in range(rng):
        bl = mon["blackouts"][i]
        bl_begin_dt = datetime.strptime(bl["time_begin"], "%H:%M")
        bl_begin_tt = datetime.timetuple(bl_begin_dt)
        dt_begin_bl = datetime.combine(
            date.today(),
            datetime.min.time()
        ) + timedelta(hours=bl_begin_tt.tm_hour, minutes=bl_begin_tt.tm_min)

        bl_end_dt = datetime.strptime(bl["time_end"], "%H:%M")
        bl_end_tt = datetime.timetuple(bl_end_dt)
        end_timedelta = timedelta(
            hours=bl_end_tt.tm_hour,
            minutes=bl_end_tt.tm_min
        )

        if end_timedelta:
            dt_end_bl = datetime.combine(
                date.today(),
                datetime.min.time()
            ) + end_timedelta
        else:
            dt_end_bl = datetime.combine(
                date.today(),
                datetime.min.time()
            ) + timedelta(hours=24)

        # если блэкаут наступил
        if (dt_begin_bl <= now < dt_end_bl) and (
            bl["day_of_week"] == 0 or (bl["day_of_week"]== now_day_of_week)
        ):
            # но еще не включен
            if not obj.get("is_blackout"):
                # включим его
                print("BLACKOUT")

                obj["is_blackout"] = True
                need_change = True
                empty = False

            #если же включен, не будем ничего менять
            exit_blackout = False
            break

    if exit_blackout and obj.get("is_blackout"):
        need_change = True

    print('EXIT BLACKOUT: ', exit_blackout)
    # если пора выходить из блэкаута
    if exit_blackout:
        # найдем текущий плейлист
        cur_pl = mon["current_pl_id"]

        # если не нашли, значит надо полюбому заливать изменения
         # и при этом не применение блэкаута
        if cur_pl is None and (not blackout_apply or sync_group):
            new_buffer = True

        sorted_pls = sorted(
            mon["playlists"],
            key=lambda k: k["time_begin"],
            reverse=True
        )
        sorted_pls = sorted(
            sorted_pls,
            key=lambda k: k.get("is_adv", False),
            reverse=True
        )

        # кол-во плейлистов на монитор
        rng = len(sorted_pls)

        # если плейлистов нет, значит выставим текущий ПЛ == 0, что означает "нету"
        if rng == 0:
            if cur_pl != "0":
                need_change = True
                mon["current_pl_id"] = "0"
        else:
            empty = False

        pl_found = False
        for i in range(rng):
            pl = sorted_pls[i]

            if pl["type"] != "audio":
                for f in pl["files"]:
                    if f["type"] == "url" and not f.get("is_script"):
                        external = True
                        break
                    elif f.get("is_script"):
                        pl["script"] = f["name"]

            if pl.get("is_adv"):
                for f in pl["files"]:
                    adv_files.append(f["name"])

                adv_interval= pl["interval"]
                adv_at_once=pl.get("adv_at_once")
                continue

            pl_dt = datetime.strptime(pl["time_begin"],"%H:%M")
            pl_tt = datetime.timetuple(pl_dt)
            dt_start_play = datetime.combine(
                date.today(),
                datetime.min.time()
            ) + timedelta(hours=pl_tt.tm_hour, minutes=pl_tt.tm_min)

            if dt_start_play <= now:
                command_arr.append(pl["launch_string"])
                pl_info["type"] = pl["type"]
                shuffle_video = pl["shuffle"]
                interval = pl["interval"]
                pl_info["files"] = pl["files"]
                pl_info["interval"] = interval
                pl_info["rotation"] = mon_rotate
                pl_info["start_time"] = dt_start_play.isoformat()

                if cur_pl != pl["id"]:
                    mon["current_pl_id"] = pl["id"]
                    save_pl_volume(pl.get("volume"))
                    fade_time = pl.get("fade_time", fade_time)
                    audio_buffer = pl.get("audio_buffer", audio_buffer)
                    video_buffer = pl.get("video_buffer", video_buffer)
                    scale_factor = round(pl.get("scale_factor", 100)/100.0, 2)
                    refresh_interval = pl.get("url_refresh_mode")
                    pl_found = True
                    if pl.get("script"):
                        # если у нас есть скрипт, то выполним его и не будем перезапускать медиа
                        launch_script(pl.get("script"))
                        need_change = False
                    else:
                        need_change = True
                    break
                else:
                    break

            #а теперь защита от того, что у нас всего один плейлист и его время еше не настало)
            if i == rng - 1 and not pl_found:
                command_arr.append(pl["launch_string"])
                if cur_pl != pl["id"]:
                    mon["current_pl_id"] = pl["id"]
                    save_pl_volume(pl.get("volume"))
                    fade_time = pl.get("fade_time", fade_time)
                    audio_buffer = pl.get("audio_buffer", audio_buffer)
                    video_buffer = pl.get("video_buffer", video_buffer)
                    scale_factor = round(pl.get("scale_factor", 100)/100, 2)
                    refresh_interval = pl.get("url_refresh_mode")
                    need_change = True

                #вынесено за условие, чтобы последующий код определения шаффла и признака "радио" имел с чем работать
                pl_info["type"] = pl["type"]
                shuffle_video = pl["shuffle"]
                interval = pl["interval"]
                pl_info["interval"] = interval
                pl_info["files"] = pl["files"]
                pl_info["rotation"] = mon_rotate
                pl_info["start_time"] = dt_start_play.isoformat()

        if vwall:
            for f in pl_info["files"]:
                vw_files.append([f["name"], f["len"]])

        if pl_info.get("type") == "audio":
            shuffle_audio = pl_info.get("shuffle")
            for f in pl_info["files"]:
                if f["type"] == "url":
                    radio = True
                    aud_files.append(f["name"])
                else:
                    aud_files.append(os.path.join(
                        "/var/starko/media/",
                        f["name"]
                    ))

    if not vwall and not mon["music_box"]:
        simple_mon = True
        simple_pl = objcopy(pl_info)

    music_box = mon["music_box"] if not music_box else music_box
    spotify = mon.get("spotify", False) if not spotify else spotify

    volume_locked = mon.get("volume_locked") if (
        not volume_locked or volume_locked is None
    ) else volume_locked
    hdmi_mode = mon.get("hdmi_mode")

    # if music_box:
    #     if audio_output == "local":
    #         audio_output = "hdmi"

    # else:
    #     output = OUTPUTS.get(mon.get("audio_output"))

    #     if audio_output != "hdmi" or output != "local":
    #         audio_output = output

if need_change:
    if not empty:
        result_command = ""

        if simple_mon and hdmi_mode:
            result_command += ''.format(hdmi_mode)

        if vwall:
            vw_x = obj.get("vw_pixel_x", 1)
            vw_y = obj.get("vw_pixel_y", 1)

            wall_size_x = obj.get("video_wall_x")
            wall_size_y = obj.get("video_wall_y")

            border = obj.get("border", 0)

            if wall_size_x % 2 == 0:
                half = wall_size_x / 2
                if vw_x <= half:
                    vw_x = half - vw_x + 0.25
                else:
                    vw_x = half - vw_x + 0.75

            else:
                vw_x = wall_size_x // 2 + 1 - vw_x

            if wall_size_y % 2 == 0:
                half = wall_size_y / 2
                if vw_y <= half:
                    vw_y = half - vw_y + 0.25
                else:
                    vw_y = half - vw_y + 0.75

            else:
                vw_y = wall_size_y // 2 + 1 - vw_y

            aspect = None

            try:
                res_x, res_y = subprocess.check_output(
                    "fbset -s | grep -o '\".*\"' | sed 's/\"//g'",
                    shell=True
                ).split("x")

                res_x = float(int(res_x))
                res_y = float(int(res_y))

                wall_size_x = (res_x * wall_size_x + (wall_size_x - 1) * border) / res_x
                wall_size_y = (res_y * wall_size_y + (wall_size_y - 1) * border) / res_y

                vw_x = vw_x * (res_x + border) / res_x
                vw_y = vw_y * (res_y + border) / res_y

                aspect = str(res_x / res_y)

            except:
                pass

            image_fade = ""
            if len(vw_files) == 1:
                image_fade = "--image-display-duration=inf"
            else:
                if float(fade_time) == 0:
                    image_fade = "--image-display-duration={} ".format(interval)
                else:
                    image_fade = "--include=/var/starko/mpv-images.conf"

            result_command += "python3 /var/starko/mpv-videowall/slave.py {} {} " \
                "/var/starko/media/playlist --keepaspect " \
                "--include=/var/starko/mpv-video.conf{} " \
                "{} " \
                "--video-rotate={} " \
                "--video-scale-x={} " \
                "--video-scale-y={} " \
                "--video-pan-x={} " \
                "--video-pan-y={} > /dev/null 2>&1 && sudo /var/starko/cec-menu.sh\n".format(
                    obj.get("device_ip"),
                    VW_PORT,
                    " --video-aspect-override=" + aspect if aspect is not None else "",
                    image_fade,
                    mon_rotate,
                    wall_size_x,
                    wall_size_y,
                    vw_x,
                    vw_y
                )

        if music_box:
            result_command += "/home/starko/bt_auto_connect\nsleep 5\n"

            result_command += "amixer sset 'Headphone' 100%\n" \
                "mpv --include=/var/starko/mpv-audio.conf " \
                    "--playlist=/var/starko/media/m_playlist " \
                    "--volume={0} {1} --cache-pause-wait={2} > /dev/null 2>&1 &\n".format(
                    get_saved_volume() if exit_blackout else 0,
                    "--shuffle" if shuffle_audio else "",
                    audio_buffer
                )

        if adv_interval:
            result_command += "while sleep 1; do /var/starko/adv_wd.sh {0} {1}; done &\n".format(
                adv_interval,
                1 if adv_at_once else 0
            )

        if simple_mon:
            image_frames = float(interval) * MPV_FPS
            fade_frames = float(fade_time) * MPV_FPS / 2

            if fade_frames <= 0:
                fade_frames = 1

            # fade_out_start = image_frames - fade_frames

            # set_fade_fps(image_frames, fade_frames, fade_out_start)

            
            # result_command += "mpv --include=/var/starko/mpv-video.conf "
            # result_command += "--playlist=/var/starko/media/mon_playlist "
            # result_command += "--no-keepaspect "

            pl_len = 0
            if pl_info:
                if simple_mon and simple_pl:
                    pl_json = json.dumps(simple_pl)
                    if simple_pl['files']:
                        for file in simple_pl["files"]:
                            if file["type"] != "aud":
                                pl_len += 1

            # if pl_len == 1:
            #     result_command += "--image-display-duration=inf "
            # else:
            #     if float(fade_time) == 0:
            #         result_command += "--image-display-duration={} ".format(interval)
            #     else:
            #         result_command += "--include=/var/starko/mpv-images.conf "

            # result_command += "--video-rotate={} ".format(mon_rotate)
            # result_command += "--cache-pause-wait={} ".format(video_buffer)

            # if shuffle_video:
            #     result_command += "--shuffle "

            # if audio_output:
            #     if audio_output == "hdmi":
            #         device = "alsa/sysdefault:CARD=b1 "

            #     if audio_output == "local":
            #         device = "alsa/default:CARD=Headphones "  # TODO починить блюпуп

            #     result_command += "--audio-device=" + device

            # else:
            #     result_command += "--no-audio "
            result_command += "xinit /home/starko/kiosk -- -nocursor vt$(fgconsole) > /dev/null 2>&1"
            # result_command += " && sudo /var/starko/cec-menu.sh\n"
            

    if new_buffer:
        print('APPLY NEW BUFFER')
        if os.path.exists('/var/www/static/chromi') and not os.path.islink('/var/www/static/chromi'):
            rmtree('/var/www/static/chromi/')
        rmtree('/var/starko/media/')
        os.mkdir('/var/starko/media')
        os.chmod("/var/starko/media", 0o777)
        if not os.path.islink('/var/www/static/chromi'):
            os.symlink('/var/starko/media', '/var/www/static/chromi')

        copy(os.path.join(DIR, "vid3.html"), '/var/www/static/chromi/')
        #move('/var/starko/buffer/*', '/var/starko/media')
        source = os.listdir("/var/starko/buffer/")
        destination = "/var/starko/media/"
        for filename in source:
            move(os.path.join("/var/starko/buffer/", filename), destination)

        subprocess.Popen('chown -R starko /var/starko/media', shell=True)
    if pl_info:
        if vwall:
            vw_set = {
                "audio": True,
                "grid": {
                    "width": 1 if sync_group else obj.get('video_wall_x', 1),
                    "height": 1 if sync_group else obj.get('video_wall_y', 1),
                },
                "rotation": 180 if obj.get('inverted') else mon_rotate,
                "border": obj.get('border', 0)
            }
            copy(os.path.join(DIR, 'silkscreen.ttf'), os.path.join('/var/starko/media/silkscreen.ttf'))
            with open('/var/starko/media/settings.json', "w") as myfile:
                myfile.write(json.dumps(vw_set))
            with open('/var/starko/media/playlist', "w") as myfile:
                if len(vw_files) == 1:
                    vw_files.append(vw_files[0])
                for fi in vw_files:
                    myfile.write(u'{0},{1}'.format(fi[0], fi[1]))
                    myfile.write('\n')


        if simple_mon and simple_pl:
            pl_json = json.dumps(simple_pl)
            if simple_pl['files']:
                with open('/var/www/static/chromi/playlist', "w") as myfile:
                    myfile.write(pl_json)

                # with open("/var/starko/media/mon_playlist", "w") as myfile:
                #     for file in simple_pl["files"]:
                #         if file["type"] != "aud":
                #             file_path = os.path.join("/var/starko/media", file["name"])
                #             myfile.write(file_path)
                #             myfile.write("\n")

            else:
                #если нет файлов в плейлисте, симитируем отсутствие плейлиста для установки Лого старки
                print("DELETING FILE")
                if os.path.isfile('/var/starko/media/playlist'):
                    os.remove('/var/starko/media/playlist')

                if os.path.isfile('/var/starko/media/mon_playlist'):
                    os.remove('/var/starko/media/mon_playlist')

        if music_box and aud_files:
            with open('/var/starko/media/m_playlist', "w") as myfile:
                for aud in aud_files:
                    myfile.write(aud)
                    myfile.write('\n')

        if music_box and adv_files:
            with open('/var/starko/media/adv_playlist', "w") as myfile:
                for aud in adv_files:
                    myfile.write(aud)
                    myfile.write('\n')

    # если блэкаут был прекращен, запишем это
    if exit_blackout:
        if obj.get('is_blackout', False):
            if simple_mon:
                try:
                    subprocess.Popen("vcgencmd display_power 1 & echo 'on 0' | cec-client -d 1 -s", shell=True)
                except:
                    print('error opening HDMI')
            if music_box:
                try:
                    vol_to_set = MAX_VOLUME if volume_locked else get_saved_volume()

                    if os.path.exists(IPC_AUDIO):
                        subprocess.Popen(
                            "echo '{\"command\": [\"set_property\", \"volume\", {}]}' | socat - {}".format(
                                vol_to_set,
                                IPC_AUDIO
                            ),
                            shell=True
                        )

                except:
                    print('error unmuting sound')

            obj['is_blackout'] = False
    else:
        if simple_mon:
            try:
                subprocess.Popen("echo 'standby 0' | cec-client -d 1 -s & vcgencmd display_power 0", shell=True)

                time.sleep(1)

                subprocess.Popen('sync', shell=True)
                #subprocess.Popen('rm -f /tmp/mpv*', shell=True)
                reloadOrKill(old_obj)

            except:
                print('error closing HDMI')
        if music_box:
            try:
                if os .path.exists(IPC_AUDIO):
                    subprocess.Popen(
                        "echo '{\"command\": [\"set_property\", \"volume\", 0]}' | socat - " + IPC_AUDIO,
                        shell=True
                    )

            except:
                print('error muting sound')
    obj['change_time'] = str(datetime.today())

    if exit_blackout and not empty:
        copy(os.path.join(DIR, '.bashrc_tmpl'), os.path.join(DIR,'.bash_profile'))
        write_method = "a" if exit_blackout else "w"
        with open(os.path.join(DIR,'.bash_profile'), write_method) as myfile:
            myfile.write(result_command)
            myfile.write('\n')
        copy(os.path.join(DIR,'.bash_profile'),'/home/starko/.bash_profile')
        subprocess.Popen('sync', shell=True)
        #subprocess.Popen('rm -f /tmp/mpv*', shell=True)
        if simple_mon:
            reloadOrKill(old_obj)
        else:
            print('else PKILL')
            subprocess.Popen('pkill -KILL -u starko', shell=True)


if not obj.get('is_blackout'):
    if music_box:
        check_volume(volume_locked)
    blackscreenMaybe(mon_rotate or 0, old_obj)

rbt = rebootCheck(obj)

rfs = refreshCheck(obj, refresh_interval)

obj['external'] = external

new_json = json.dumps(obj)
with open(current_file, "w") as myfile:
    myfile.write(new_json)

if rbt:
    subprocess.Popen('sync', shell=True)
    subprocess.Popen('reboot', shell=True)

if rfs:
    subprocess.Popen('refresh', shell=True)
