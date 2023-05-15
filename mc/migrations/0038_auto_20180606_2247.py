# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0037_auto_20180514_2227'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='host',
            name='name',
        ),
        migrations.RemoveField(
            model_name='vwallpixel',
            name='hostname',
        ),
    ]
