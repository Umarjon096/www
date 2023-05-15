# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0047_auto_20201203_1622'),
    ]

    operations = [
        migrations.AddField(
            model_name='monitor',
            name='spotify',
            field=models.BooleanField(default=False, verbose_name='\u041c\u043e\u043d\u0438\u0442\u043e\u0440 \u0432 \u0440\u0435\u0436\u0438\u043c\u0435 Spotify Connect'),
            preserve_default=True,
        ),
    ]
