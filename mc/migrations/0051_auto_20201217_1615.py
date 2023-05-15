# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0050_monitor_audio_output'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monitor',
            name='audio_output',
            field=models.IntegerField(default=0, verbose_name='\u0412\u044b\u0432\u043e\u0434 \u0437\u0432\u0443\u043a\u0430 \u0432\u044b\u043a\u043b\u044e\u0447\u0435\u043d(0), \u043d\u0430 jack(1) \u0438\u043b\u0438 hdmi(2)', choices=[(0, b'off'), (1, b'3.5mm jack'), (2, b'hdmi')]),
            preserve_default=True,
        ),
    ]
