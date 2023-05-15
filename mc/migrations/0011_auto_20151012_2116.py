# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0010_auto_20150616_1946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monitor',
            name='resolution',
            field=models.CharField(max_length=50, null=True, verbose_name='\u0420\u0430\u0437\u0440\u0435\u0448\u0435\u043d\u0438\u0435 \u043c\u043e\u043d\u0438\u0442\u043e\u0440\u0430', blank=True),
            preserve_default=True,
        ),
    ]
