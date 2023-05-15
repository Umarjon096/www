# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0032_auto_20170429_1629'),
    ]

    operations = [
        migrations.AddField(
            model_name='vwallpixel',
            name='hostname',
            field=models.CharField(max_length=200, unique=True, null=True, verbose_name='Hostname', blank=True),
            preserve_default=True,
        ),
    ]
