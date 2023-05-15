# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0016_auto_20160116_1216'),
    ]

    operations = [
        migrations.AddField(
            model_name='blackout',
            name='day_of_week',
            field=models.IntegerField(null=True, verbose_name='\u0414\u0435\u043d\u044c \u043d\u0435\u0434\u0435\u043b\u0438', blank=True),
            preserve_default=True,
        ),
    ]
