# -*- coding: utf-8 -*-
from django.utils import timezone
import datetime
from math import fabs
from mc.models import Setting, RebootLog
from mc.utils import all_hosts_reboot


def reboot_self():
    restart_if_not_already = False
    reboot_param = Setting.objects.get(code='reboot')
    day_str, time_str = reboot_param.value.split(' ')
    if not time_str or int(day_str) == 0:
        #если время перезагрузки не задано в параметре, ничего не делаем
        return
    time_obj = datetime.datetime.strptime(time_str, '%H:%M')
    new_time = time_obj.time()
    tz_now = timezone.localtime(timezone.now())
    day_now = tz_now.isoweekday()
    time_now = tz_now.time()

    if (int(day_str) == -1 or int(day_str) <= day_now) and new_time <= time_now:
        restart_if_not_already = True
        days_delta = fabs(int(day_str) - day_now) if int(day_str) != -1 else 0
        real_day = tz_now.date() - datetime.timedelta(days=days_delta)
        real_datetime = timezone.make_aware(datetime.datetime.combine(real_day, new_time), tz_now.tzinfo)

    if restart_if_not_already:
        try:
            latest = RebootLog.objects.latest('scheduled_time')
        except RebootLog.DoesNotExist:
            latest = None

        if not latest:
            #первый раз не будем перезагружать
            RebootLog.objects.create(scheduled_time=real_datetime)
            return
        else:
            #если не первый раз, проверим, перезагружались ли мы уже для этого времени
            if latest.scheduled_time >= real_datetime:
                #если у нас в логе запись со временем ребута старшим, чем сейчас, видимо что-то поменялось. Потрем их на всяк
                RebootLog.objects.filter(scheduled_time__gt=real_datetime).delete()
                #если мы уже перезапускались для указанного времени, ниче не делаем
                return
            else:
                #если нет, создаём запись в лог и перезагружаемся
                RebootLog.objects.create(scheduled_time=real_datetime)
                all_hosts_reboot()