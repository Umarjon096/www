# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0034_monitor_volume_locked'),
    ]

    operations = [
        migrations.AddField(
            model_name='monitor',
            name='video_wall_borders',
            field=models.PositiveIntegerField(default=0, verbose_name='\u0420\u0430\u0437\u043c\u0435\u0440 \u0440\u0430\u043c\u043a\u0438 (\u0432 \u043f\u0438\u043a\u0441\u0435\u043b\u044f\u0445)'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='vwallpixel',
            name='inverted',
            field=models.BooleanField(default=False, verbose_name='\u041f\u0435\u0440\u0435\u0432\u0451\u0440\u043d\u0443\u0442'),
            preserve_default=True,
        ),
    ]
