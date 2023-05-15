# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0033_vwallpixel_hostname'),
    ]

    operations = [
        migrations.AddField(
            model_name='monitor',
            name='volume_locked',
            field=models.BooleanField(default=False, verbose_name='\u0413\u0440\u043e\u043c\u043a\u043e\u0441\u0442\u044c \u0444\u0438\u043a\u0441\u0438\u0440\u043e\u0432\u0430\u043d\u0430'),
            preserve_default=True,
        ),
    ]
