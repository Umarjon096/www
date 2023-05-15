# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0059_auto_20220126_1713'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='is_vertical',
            field=models.BooleanField(default=False, verbose_name='\u0412\u0435\u0440\u0442\u0438\u043a\u0430\u043b\u044c\u043d\u043e \u043e\u0440\u0438\u0435\u043d\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u0430\u044f \u043a\u0430\u0440\u0442\u0438\u043d\u043a\u0430'),
            preserve_default=True,
        ),
    ]
