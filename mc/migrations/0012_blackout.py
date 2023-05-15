# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0011_auto_20151012_2116'),
    ]

    operations = [
        migrations.CreateModel(
            name='Blackout',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_begin', models.TimeField(verbose_name='\u0412\u0440\u0435\u043c\u044f \u043d\u0430\u0447\u0430\u043b\u0430 \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u044f, \u0447\u0447:\u043c\u043c')),
                ('time_end', models.TimeField(verbose_name='\u0412\u0440\u0435\u043c\u044f \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u044f, \u0447\u0447:\u043c\u043c')),
            ],
            options={
                'verbose_name': '\u041f\u0435\u0440\u0438\u043e\u0434 \u043d\u0435\u0430\u043a\u0442\u0438\u0432\u043d\u043e\u0441\u0442\u0438 \u043c\u043e\u043d\u0438\u0442\u043e\u0440\u043e\u0432',
                'verbose_name_plural': '\u041f\u0435\u0440\u0438\u043e\u0434\u044b \u043d\u0435\u0430\u043a\u0442\u0438\u0432\u043d\u043e\u0441\u0442\u0438 \u043c\u043e\u043d\u0438\u0442\u043e\u0440\u043e\u0432',
            },
            bases=(models.Model,),
        ),
    ]
