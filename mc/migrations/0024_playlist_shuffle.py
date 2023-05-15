# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0023_auto_20160807_1122'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='shuffle',
            field=models.BooleanField(default=False, verbose_name='\u0412\u043f\u0435\u0440\u0435\u043c\u0435\u0448\u043a\u0443'),
            preserve_default=True,
        ),
    ]
