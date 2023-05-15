# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0024_playlist_shuffle'),
    ]

    operations = [
        migrations.CreateModel(
            name='SavedUrl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('url', models.CharField(max_length=2000, null=True, verbose_name='URL', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
