# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0002_auto_20150211_0219'),
    ]

    def default_settings(apps, schema_editor):
        # We can't import the Person model directly as it may be a newer
        # version than this migration expects. We use the historical version.
        Setting = apps.get_model("mc", "Setting")
        Setting(name=u'Адрес глобального мастера',
                code=u'global_url',
                value=u'https://opteo.pro').save()
        Setting(name=u'Период запросов обновления (мин)',
                code=u'sync_period',
                value=u'60').save()

    def reverse_code(apps, schema_editor):
        pass

    operations = [
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u0430')),
                ('code', models.CharField(max_length=200, verbose_name='\u041a\u043e\u0434 \u043f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u0430 (\u043f\u043e\u043d\u044f\u0442\u043d\u044b\u0439 \u043a\u043e\u043c\u043f\u044c\u044e\u0442\u0435\u0440\u0430\u043c)')),
                ('value', models.CharField(max_length=2000, verbose_name='\u0417\u043d\u0430\u0447\u0435\u043d\u0438\u0435 \u043f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u0430')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RunPython(default_settings, reverse_code),
    ]
