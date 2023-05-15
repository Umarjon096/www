# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0013_auto_20151218_0013'),
    ]

    operations = [
        migrations.CreateModel(
            name='RebootLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('scheduled_time', models.DateTimeField(verbose_name='\u041d\u0430\u0437\u043d\u0430\u0447\u0435\u043d\u043d\u0430\u044f \u0434\u0430\u0442\u0430 \u043f\u0435\u0440\u0435\u0437\u0430\u0433\u0440\u0443\u0437\u043a\u0438')),
                ('processed_time', models.DateTimeField(auto_now=True, verbose_name='\u041d\u0430\u0437\u043d\u0430\u0447\u0435\u043d\u043d\u0430\u044f \u0434\u0430\u0442\u0430 \u043f\u0435\u0440\u0435\u0437\u0430\u0433\u0440\u0443\u0437\u043a\u0438')),
            ],
            options={
                'verbose_name': '\u041b\u043e\u0433 \u043f\u0435\u0440\u0435\u0437\u0430\u0433\u0440\u0443\u0437\u043a\u0438',
                'verbose_name_plural': '\u041b\u043e\u0433\u0438 \u043f\u0435\u0440\u0435\u0437\u0430\u0433\u0440\u0443\u0437\u043a\u0438',
            },
            bases=(models.Model,),
        ),
    ]
