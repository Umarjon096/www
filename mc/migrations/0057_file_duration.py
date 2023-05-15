# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0056_item_is_site'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='duration',
            field=models.FloatField(default=0.0, verbose_name='\u0414\u043b\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u044c \u0432 \u0441\u0435\u043a'),
            preserve_default=True,
        ),
    ]
