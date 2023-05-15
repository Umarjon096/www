# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0048_monitor_spotify'),
    ]

    operations = [
        migrations.AddField(
            model_name='savedurl',
            name='video',
            field=models.BooleanField(default=False, verbose_name='\u041f\u0440\u0438\u0437\u043d\u0430\u043a \u0442\u043e\u0433\u043e, \u0447\u0442\u043e \u044d\u0442\u043e \u0441\u0441\u044b\u043b\u043a\u0430 \u043d\u0430 \u0432\u0438\u0434\u0435\u043e\u0441\u0442\u0440\u0438\u043c'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='savedurl',
            name='built_in',
            field=models.BooleanField(default=True, verbose_name='\u041f\u0440\u0438\u0437\u043d\u0430\u043a \u0432\u0441\u0442\u0440\u043e\u0435\u043d\u043d\u0430\u044f \u043b\u0438 \u0432 \u0441\u0438\u0441\u0442\u0435\u043c\u0443 \u0441\u0441\u044b\u043b\u043a\u0430 \u043d\u0430 \u043f\u043e\u0442\u043e\u043a'),
            preserve_default=True,
        ),
    ]
