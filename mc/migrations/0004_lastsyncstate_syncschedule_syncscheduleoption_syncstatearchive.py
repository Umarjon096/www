# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0003_setting'),
    ]

    def sync_schedule_option(apps, schema_editor):
        sso = apps.get_model("mc", "SyncScheduleOption")
        sso(enabled=False).save()

    def reverse_code(apps, schema_editor):
        pass

    operations = [
        migrations.CreateModel(
            name='LastSyncState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u043f\u043e\u043f\u044b\u0442\u043a\u0438 \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0430\u0446\u0438\u0438')),
                ('schedule_time', models.DateTimeField(null=True, verbose_name='\u041f\u043b\u0430\u043d\u043e\u0432\u0430\u044f \u0434\u0430\u0442\u0430 \u043f\u043e\u043f\u044b\u0442\u043a\u0438 \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0430\u0446\u0438\u0438', blank=True)),
                ('status', models.CharField(max_length=200, verbose_name='\u0421\u0442\u0440\u043e\u043a\u043e\u0432\u044b\u0439 \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u0430')),
                ('note', models.TextField(null=True, verbose_name='\u0414\u0435\u0442\u0430\u043b\u044c\u043d\u043e\u0435 \u043e\u043f\u0438\u0441\u0430\u043d\u0438\u0435 \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u0430', blank=True)),
            ],
            options={
                'verbose_name': '\u041f\u043e\u0441\u043b\u0435\u0434\u043d\u0435\u0435 \u0441\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u0435 \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0430\u0446\u0438\u0438',
                'verbose_name_plural': '\u041f\u043e\u0441\u043b\u0435\u0434\u043d\u0438\u0435 \u0441\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u044f \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0430\u0446\u0438\u0438',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SyncSchedule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.TimeField(verbose_name='\u041f\u043b\u0430\u043d\u043e\u0432\u043e\u0435 \u0432\u0440\u0435\u043c\u044f \u0437\u0430\u043f\u0440\u043e\u0441\u0430 \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u0439 \u0441 \u0433\u043b\u043e\u0431\u0430\u043b\u0430')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SyncScheduleOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('enabled', models.BooleanField(default=False, verbose_name='\u0412\u043a\u043b\u044e\u0447\u0435\u043d\u043e \u043b\u0438 \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u0435 \u043f\u043e \u0440\u0430\u0441\u043f\u0438\u0441\u0430\u043d\u0438\u044e (\u0432 \u043f\u0440\u043e\u0442\u0438\u0432\u043d\u043e\u043c \u0441\u043b\u0443\u0447\u0430\u0435 \u0440\u0430\u0431\u043e\u0442\u0430\u0435\u0442 \u043f\u0435\u0440\u0438\u043e\u0434\u0438\u0447\u0435\u0441\u043a\u043e\u0435')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SyncStateArchive',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u043f\u043e\u043f\u044b\u0442\u043a\u0438 \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0430\u0446\u0438\u0438')),
                ('schedule_time', models.DateTimeField(null=True, verbose_name='\u041f\u043b\u0430\u043d\u043e\u0432\u0430\u044f \u0434\u0430\u0442\u0430 \u043f\u043e\u043f\u044b\u0442\u043a\u0438 \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0430\u0446\u0438\u0438', blank=True)),
                ('status', models.CharField(max_length=200, verbose_name='\u0421\u0442\u0440\u043e\u043a\u043e\u0432\u044b\u0439 \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u0430')),
                ('note', models.TextField(null=True, verbose_name='\u0414\u0435\u0442\u0430\u043b\u044c\u043d\u043e\u0435 \u043e\u043f\u0438\u0441\u0430\u043d\u0438\u0435 \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u0430', blank=True)),
            ],
            options={
                'verbose_name': '\u0410\u0440\u0445\u0438\u0432\u043d\u043e\u0435 \u0441\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u0435 \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0430\u0446\u0438\u0438',
                'verbose_name_plural': '\u0410\u0440\u0445\u0438\u0432\u043d\u044b\u0435 \u0441\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u044f \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0430\u0446\u0438\u0438',
            },
            bases=(models.Model,),
        ),
        migrations.RunPython(sync_schedule_option, reverse_code),
    ]
