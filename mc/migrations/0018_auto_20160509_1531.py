# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0017_blackout_day_of_week'),
    ]

    def syncstatus_setting(apps, schema_editor):
        # We can't import the Person model directly as it may be a newer
        # version than this migration expects. We use the historical version.
        Setting = apps.get_model("mc", "Setting")
        Setting(name=u'Статус синхронизации медиа с глобалом',
                code=u'global_sync',
                value=u'synced').save()

    def reverse_code(apps, schema_editor):
        Setting = apps.get_model("mc", "Setting")
        Setting.objects.filter(code=u'global_sync').delete()


    operations = [
        migrations.RunPython(syncstatus_setting, reverse_code),
    ]
