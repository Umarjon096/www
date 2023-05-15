# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0044_playlist_last_updated'),
    ]

    operations = [
        migrations.CreateModel(
            name='RebootsData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.DateTimeField(verbose_name='\u0412\u0440\u0435\u043c\u044f \u0437\u0430\u043f\u0443\u0441\u043a\u0430 \u043f\u0435\u0440\u0435\u0437\u0430\u0433\u0440\u0443\u0437\u043a\u0438')),
                ('check', models.DateTimeField(null=True, verbose_name='\u0412\u0440\u0435\u043c\u044f, \u043a\u043e\u0433\u0434\u0430 \u0444\u0430\u043a\u0442 \u043f\u0435\u0440\u0435\u0437\u0430\u0433\u0440\u0443\u0437\u043a\u0438 \u0431\u044b\u043b \u043f\u0440\u043e\u0432\u0435\u0440\u0435\u043d', blank=True)),
                ('host', models.ForeignKey(to='mc.Host')),
            ],
            options={
                'verbose_name': '\u041f\u0435\u0440\u0435\u0437\u0430\u0433\u0440\u0443\u0437\u043a\u0430 \u043f\u043e \u043a\u043e\u043c\u0430\u043d\u0434\u0435',
                'verbose_name_plural': '\u041f\u0435\u0440\u0435\u0437\u0430\u0433\u0440\u0443\u0437\u043a\u0438 \u043f\u043e \u043a\u043e\u043c\u0430\u043d\u0434\u0435',
            },
            bases=(models.Model,),
        ),
    ]
