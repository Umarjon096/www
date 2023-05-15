# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0031_savedurl_built_in'),
    ]

    operations = [
        migrations.CreateModel(
            name='vWallPixel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('x_pos', models.PositiveSmallIntegerField(verbose_name='\u041a\u043e\u043e\u0440\u0434\u0438\u043d\u0430\u0442\u0430 X')),
                ('y_pos', models.PositiveSmallIntegerField(verbose_name='\u041a\u043e\u043e\u0440\u0434\u0438\u043d\u0430\u0442\u0430 Y')),
                ('ip_address', models.IPAddressField(verbose_name='IP')),
                ('monitor', models.ForeignKey(to='mc.Monitor')),
            ],
            options={
                'verbose_name': '\u042f\u0447\u0435\u0439\u043a\u0430 \u0432\u0438\u0434\u0435\u043e\u0441\u0442\u0435\u043d\u044b',
                'verbose_name_plural': '\u042f\u0447\u0435\u0439\u043a\u0438 \u0432\u0438\u0434\u0435\u043e\u0441\u0442\u0435\u043d\u044b',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='monitor',
            name='video_wall',
            field=models.BooleanField(default=False, verbose_name='\u0412\u0438\u0434\u0435\u043e-\u0441\u0442\u0435\u043d\u0430'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='monitor',
            name='video_wall_x',
            field=models.PositiveSmallIntegerField(null=True, verbose_name='\u0420\u0430\u0437\u043c\u0435\u0440 \u0441\u0442\u0435\u043d\u044b \u043f\u043e \u0433\u043e\u0440\u0438\u0437\u043e\u043d\u0442\u0430\u043b\u0438', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='monitor',
            name='video_wall_y',
            field=models.PositiveSmallIntegerField(null=True, verbose_name='\u0420\u0430\u0437\u043c\u0435\u0440 \u0441\u0442\u0435\u043d\u044b \u043f\u043e \u0433\u043e\u0440\u0438\u0437\u043e\u043d\u0442\u0430\u043b\u0438', blank=True),
            preserve_default=True,
        ),
    ]
