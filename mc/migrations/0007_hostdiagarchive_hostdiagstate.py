# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0006_auto_20150405_1350'),
    ]

    operations = [
        migrations.CreateModel(
            name='HostDiagArchive',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(auto_now=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u0441\u0431\u043e\u0440\u0430 \u0434\u0438\u0430\u0433\u043d\u043e\u0441\u0442\u0438\u043a\u0438', auto_now_add=True)),
                ('ping', models.BooleanField(default=False, verbose_name='\u0415\u0441\u0442\u044c \u043b\u0438 \u043f\u0438\u043d\u0433 \u0434\u043e \u0445\u043e\u0441\u0442\u0430')),
                ('webserver', models.BooleanField(default=True, verbose_name='\u041f\u043e\u0434\u043d\u044f\u0442 \u043b\u0438 \u0432\u0435\u0431 \u0441\u0435\u0440\u0432\u0435\u0440')),
                ('health', models.TextField(null=True, verbose_name='json \u0441 \u0434\u0438\u0430\u0433\u043d\u043e\u0441\u0442\u0438\u0447\u0435\u0441\u043a\u043e\u0439 \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u0435\u0439', blank=True)),
                ('host', models.ForeignKey(to='mc.Host')),
            ],
            options={
                'verbose_name': '\u041f\u043e\u0441\u043b\u0435\u0434\u043d\u0435\u0435 \u0441\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u0435 \u0434\u0438\u0430\u0433\u043d\u043e\u0441\u0442\u0438\u043a\u0438',
                'verbose_name_plural': '\u041f\u043e\u0441\u043b\u0435\u0434\u043d\u0438\u0435 \u0441\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u044f \u0434\u0438\u0430\u0433\u043d\u043e\u0441\u0442\u0438\u043a\u0438',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HostDiagState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(auto_now=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u0441\u0431\u043e\u0440\u0430 \u0434\u0438\u0430\u0433\u043d\u043e\u0441\u0442\u0438\u043a\u0438', auto_now_add=True)),
                ('ping', models.BooleanField(default=False, verbose_name='\u0415\u0441\u0442\u044c \u043b\u0438 \u043f\u0438\u043d\u0433 \u0434\u043e \u0445\u043e\u0441\u0442\u0430')),
                ('webserver', models.BooleanField(default=True, verbose_name='\u041f\u043e\u0434\u043d\u044f\u0442 \u043b\u0438 \u0432\u0435\u0431 \u0441\u0435\u0440\u0432\u0435\u0440')),
                ('health', models.TextField(null=True, verbose_name='json \u0441 \u0434\u0438\u0430\u0433\u043d\u043e\u0441\u0442\u0438\u0447\u0435\u0441\u043a\u043e\u0439 \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u0435\u0439', blank=True)),
                ('host', models.ForeignKey(to='mc.Host')),
            ],
            options={
                'verbose_name': '\u041f\u043e\u0441\u043b\u0435\u0434\u043d\u0435\u0435 \u0441\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u0435 \u0434\u0438\u0430\u0433\u043d\u043e\u0441\u0442\u0438\u043a\u0438',
                'verbose_name_plural': '\u041f\u043e\u0441\u043b\u0435\u0434\u043d\u0438\u0435 \u0441\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u044f \u0434\u0438\u0430\u0433\u043d\u043e\u0441\u0442\u0438\u043a\u0438',
            },
            bases=(models.Model,),
        ),
    ]
