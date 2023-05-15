# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0043_auto_20201014_1302'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2020, 10, 27, 12, 45, 38, 982017), auto_now=True),
            preserve_default=False,
        ),
    ]
