# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0028_auto_20170224_1646'),
    ]

    operations = [
        migrations.CreateModel(
            name='PendingChanges',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('blackouts', models.BooleanField(default=False)),
                ('users', models.BooleanField(default=False)),
                ('config', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': '\u0418\u043d\u0434\u0438\u043a\u0430\u0442\u043e\u0440 \u043e\u0431\u043d\u043e\u0432\u0438\u0432\u0448\u0438\u0445\u0441\u044f \u0434\u0430\u043d\u043d\u044b\u0445',
                'verbose_name_plural': '\u0418\u043d\u0434\u0438\u043a\u0430\u0442\u043e\u0440\u044b \u043e\u0431\u043d\u043e\u0432\u0438\u0432\u0448\u0438\u0445\u0441\u044f \u0434\u0430\u043d\u043d\u044b\u0445',
            },
            bases=(models.Model,),
        ),
    ]
