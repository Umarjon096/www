# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0018_auto_20160509_1531'),
    ]

    operations = [
        migrations.AlterField(
            model_name='setting',
            name='code',
            field=models.CharField(unique=True, max_length=200, verbose_name='\u041a\u043e\u0434 \u043f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u0430 (\u043f\u043e\u043d\u044f\u0442\u043d\u044b\u0439 \u043a\u043e\u043c\u043f\u044c\u044e\u0442\u0435\u0440\u0430\u043c)'),
            preserve_default=True,
        ),
    ]
