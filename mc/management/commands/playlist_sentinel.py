# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
import json
import subprocess
import os
from datetime import date, datetime, timedelta
from shutil import copy, move, rmtree, copytree
import socket


class Command(BaseCommand):
    help = 'Apply new pls'

    def handle(self, *args, **options):
        DIR = '/var/starko/'
        now = datetime.now()
        now_day_of_week = now.isoweekday()
        hostname = socket.gethostname()
        file = os.path.join(DIR,'.{0}'.format(hostname))
        current_file = os.path.join(DIR,'.current')
        if os.path.isfile(file):
            move(file,current_file)
        f = open(current_file,'r')
        raw_file_str = f.read()
        obj = json.loads(raw_file_str)

        command_arr = []
        need_change = False
        empty = True
        new_buffer = False

        exit_blackout = True

        blackout_apply=obj.get('blackout_apply') #если это применение блэкаута, то не будем тереть медиа
        #цикл по мониторам
        for mon in obj['monitors']:

            #проверим, не блэкаут ли сейчас
            rng = len(mon['blackouts'])
            for i in range(rng):
                bl = mon['blackouts'][i]
                bl_begin_dt = datetime.strptime(bl['time_begin'],'%H:%M')
                bl_begin_tt = datetime.timetuple(bl_begin_dt)
                dt_begin_bl = datetime.combine(date.today(), datetime.min.time()) + timedelta(hours=bl_begin_tt.tm_hour,minutes=bl_begin_tt.tm_min)

                bl_end_dt = datetime.strptime(bl['time_end'],'%H:%M')
                bl_end_tt = datetime.timetuple(bl_end_dt)
                dt_end_bl = datetime.combine(date.today(), datetime.min.time()) + timedelta(hours=bl_end_tt.tm_hour,minutes=bl_end_tt.tm_min)

                #если блэкаут наступил
                if (dt_begin_bl <= now < dt_end_bl) and (bl['day_of_week']==0 or (bl['day_of_week']== now_day_of_week) ):
                    #но еще не включен
                    if not obj.get('is_blackout'):
                        #включим его
                        print 'BLACKOUT'
                        #command_arr.append('xrandr --output HDMI1 --off --output HDMI2 --off')
                        obj['is_blackout'] = True
                        need_change = True
                        empty = False
                    #если же включен, не будем ничего менять
                    exit_blackout = False
                    break

            if exit_blackout and obj.get('is_blackout'):
                need_change = True
            #если пора выходить из блэкаута
            if exit_blackout:
                #найдем текущий плейлист
                cur_pl = mon['current_pl_id']
                #если не нашли, значит надо полюбому заливать изменения
                if cur_pl is None and not blackout_apply: #и при этом не применение блэкаута
                    new_buffer = True

                #кол-во плейлистов на монитор
                rng = len(mon['playlists'])

                #если плейлистов нет, значит выставим текущий ПЛ == 0, что означает "нету"
                if rng == 0:
                    if cur_pl != '0':
                        need_change = True
                        mon['current_pl_id'] = '0'
                else:
                    empty = False

                pl_found = False
                for i in range(rng):
                    pl = mon['playlists'][i]

                    pl_dt = datetime.strptime(pl['time_begin'],'%H:%M')
                    pl_tt = datetime.timetuple(pl_dt)
                    dt_start_play = datetime.combine(date.today(), datetime.min.time()) + timedelta(hours=pl_tt.tm_hour,minutes=pl_tt.tm_min)
                    if dt_start_play <= now:
                        if cur_pl != pl['id']:
                            command_arr.append(pl['launch_string'])
                            mon['current_pl_id'] = pl['id']
                            pl_found = True
                            need_change = True
                            break
                        else:
                            command_arr.append(pl['launch_string'])
                            break
                    #а теперь защита от того, что у нас всего один плейлист и его время еше не настало)
                    if i == rng-1 and not pl_found:
                        command_arr.append(pl['launch_string'])
                        if cur_pl != pl['id']:
                            mon['current_pl_id'] = pl['id']
                            need_change = True

        if need_change:
            if not empty:
                command_str = '{0} & {1}' if len(command_arr) > 1 else '{0}'
                result_command = command_str.format(*command_arr)
            else:
                result_command = ''

            if new_buffer:
                rmtree('/var/starko/media/')
                os.mkdir('/var/starko/media')
                #move('/var/starko/buffer/*', '/var/starko/media')
                source = os.listdir("/var/starko/buffer/")
                destination = "/var/starko/media/"
                for filename in source:
                    move(os.path.join("/var/starko/buffer/", filename), destination)

            copy(os.path.join(DIR, '.bashrc_tmpl'), os.path.join(DIR,'.bashrc'))
            write_method = "a" if exit_blackout else "w"
            with open(os.path.join(DIR,'.bashrc'), write_method) as myfile:
                myfile.write(result_command)
                myfile.write('\n')
            copy(os.path.join(DIR,'.bashrc'),'/home/starko/.bashrc')
            subprocess.Popen('pkill X', shell=True)

            #если блэкаут был прекращен, запишем это
            if exit_blackout:
                subprocess.Popen("echo 'on 0' | cec-client -s RPI")
                obj['is_blackout'] = False
            else:
                subprocess.Popen("echo 'standby 0' | cec-client -s RPI")

            obj['change_time'] = str(datetime.today())
            new_json = json.dumps(obj)
            with open(current_file, "w") as myfile:
                    myfile.write(new_json)