# -*- coding: utf-8 -*-
import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.timezone import get_default_timezone, utc

from mc.models import SyncScheduleOption, LastSyncState, Setting, SyncSchedule
from mc.utils import send_diag_request, is_master

DEV = getattr(settings, 'DEV', False)

class Command(BaseCommand):
    help = 'Send diag info to global'

    def handle(self, *args, **options):
        if not is_master():
            return

        if not DEV:
            try:
                work_by_schedule = SyncScheduleOption.objects.get(pk=1).enabled
            except SyncScheduleOption.DoesNotExist:
                work_by_schedule = False

            try:
                lss_time = LastSyncState.objects.latest('time').time
            except LastSyncState.DoesNotExist:
                lss_time = None

            if not work_by_schedule:
                try:
                    interval = int(Setting.objects.get(code='sync_period').value)
                except Setting.DoesNotExist:
                    interval = 60
                if interval < 5:
                    interval = 5
                if lss_time is not None:
                    next_sync_time = lss_time + datetime.timedelta(minutes=interval)
                    if next_sync_time > timezone.now():
                        return
            else:
                schedule = SyncSchedule.objects.all().order_by('time')
                time_now = timezone.now()
                last_possible_sync_time = None
                for rec in schedule:
                    rec_datetime = datetime.datetime.combine(datetime.date.today(), rec.time)
                    tz = get_default_timezone()
                    aware_dt =  rec_datetime.replace(tzinfo=tz).astimezone(utc)
                    if aware_dt > time_now:
                        break
                    else:
                        last_possible_sync_time = aware_dt

                if last_possible_sync_time is None or lss_time > last_possible_sync_time:
                    return
        res = send_diag_request()
        self.stdout.write(u"Diag send result: {0}".format(res))