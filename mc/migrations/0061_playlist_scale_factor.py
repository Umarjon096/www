# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0060_file_is_vertical'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='scale_factor',
            field=models.PositiveIntegerField(default=100, verbose_name='\u041c\u0430\u0441\u0448\u0442\u0430\u0431 \u0431\u0440\u0430\u0443\u0437\u0435\u0440\u0430'),
            preserve_default=True,
        ),
    ]
