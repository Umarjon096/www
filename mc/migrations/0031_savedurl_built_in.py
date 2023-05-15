# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0030_pendingchanges_sync'),
    ]

    operations = [
        migrations.AddField(
            model_name='savedurl',
            name='built_in',
            field=models.BooleanField(default=True, verbose_name='\u041f\u0440\u0438\u0437\u043d\u0430\u043a \u0432\u0441\u0442\u0440\u043e\u0435\u043d\u043d\u0430\u044f \u043b\u0438 \u0432 \u0441\u0438\u0441\u0442\u0435\u043c\u0443 \u0440\u0430\u0434\u0438\u043e\u0441\u0442\u0430\u043d\u0446\u0438\u044f'),
            preserve_default=True,
        ),
    ]
