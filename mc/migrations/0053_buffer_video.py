# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0052_buffer_setting'),
    ]

    def default_settings(apps, schema_editor):
        # We can't import the Person model directly as it may be a newer
        # version than this migration expects. We use the historical version.
        Setting = apps.get_model("mc", "Setting")
        Setting(name=u'Размер буффера видео, c',
                code=u'video_buffer',
                value=u'5').save()

    def reverse_code(apps, schema_editor):
        pass

    operations = [
        migrations.RunPython(default_settings, reverse_code),
    ]
