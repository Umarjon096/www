# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0057_file_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='bitrate',
            field=models.IntegerField(default=0, verbose_name='\u0411\u0438\u0442\u0440\u0435\u0439\u0442'),
            preserve_default=True,
        ),
    ]
