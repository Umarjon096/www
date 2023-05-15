# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0058_file_bitrate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playlist',
            name='volume',
            field=models.IntegerField(null=True, verbose_name='\u0413\u0440\u043e\u043c\u043a\u043e\u0441\u0442\u044c \u043e\u0442\u0434\u0435\u043b\u044c\u043d\u043e\u0433\u043e \u043f\u043b\u0435\u0439\u043b\u0438\u0441\u0442\u0430', blank=True),
            preserve_default=True,
        ),
    ]
