# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0041_auto_20190523_2238'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='adv_at_once',
            field=models.BooleanField(default=False, verbose_name='\u041f\u0440\u043e\u0438\u0433\u0440\u044b\u0432\u0430\u0442\u044c \u0432\u0441\u0435 \u0444\u0430\u0439\u043b\u044b \u0440\u0430\u0437\u043e\u043c'),
            preserve_default=True,
        ),
    ]
