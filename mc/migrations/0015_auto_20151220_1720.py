# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0014_rebootlog'),
    ]

    def setup_reboot(apps, schema_editor):
        # We can't import the Person model directly as it may be a newer
        # version than this migration expects. We use the historical version.
        Setting = apps.get_model("mc", "Setting")
        Setting.objects.filter(code=u'reboot').update(value='1 03:00')

        RebootLog = apps.get_model("mc", "RebootLog")

        try:
            latest = RebootLog.objects.latest('scheduled_time')
        except RebootLog.DoesNotExist:
            latest = None

        if not latest:
            default_time = datetime.date(2010, 1, 1)
            RebootLog.objects.create(scheduled_time=default_time)

    def reverse_code(apps, schema_editor):
        pass


    operations = [
        migrations.RunPython(setup_reboot, reverse_code),
    ]
