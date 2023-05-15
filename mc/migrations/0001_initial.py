# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, null=True, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0444\u0430\u0439\u043b\u0430', blank=True)),
                ('data', models.FileField(upload_to=b'usr_uploads/', verbose_name='\u0418\u0441\u0445\u043e\u0434\u043d\u044b\u0439 \u0444\u0430\u0439\u043b')),
                ('thumbnail', models.ImageField(upload_to=b'usr_uploads/thumbnails', verbose_name='\u0421\u043a\u0440\u0438\u043d\u0448\u043e\u0442 \u0441 \u0444\u0430\u0439\u043b\u0430')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, null=True, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0445\u043e\u0441\u0442\u0430', blank=True)),
                ('ip', models.CharField(max_length=200, null=True, verbose_name='IP', blank=True)),
                ('netmask', models.CharField(max_length=200, null=True, verbose_name='Netmask', blank=True)),
                ('gateway', models.CharField(max_length=200, null=True, verbose_name='Gateway', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=200, verbose_name='\u0422\u0438\u043f \u043c\u0435\u0434\u0438\u0430')),
                ('sequence', models.IntegerField(default=0, verbose_name='\u041e\u0447\u0435\u0440\u0435\u0434\u043d\u043e\u0441\u0442\u044c')),
                ('file', models.ForeignKey(to='mc.File')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Monitor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, null=True, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043c\u043e\u043d\u0438\u0442\u043e\u0440\u0430', blank=True)),
                ('orientation', models.CharField(max_length=200, verbose_name='\u041e\u0440\u0438\u0435\u043d\u0442\u0430\u0446\u0438\u044f (left/standard/right)', choices=[(b'left', b'\xd0\xbf\xd0\xbe\xd0\xb2\xd0\xb5\xd1\x80\xd0\xbd\xd1\x83\xd1\x82 \xd0\xb2\xd0\xbb\xd0\xb5\xd0\xb2\xd0\xbe'), (b'standard', b'\xd0\xbe\xd0\xb1\xd1\x8b\xd1\x87\xd0\xbd\xd0\xb0\xd1\x8f'), (b'right', b'\xd0\xbf\xd0\xbe\xd0\xb2\xd0\xb5\xd1\x80\xd0\xbd\xd1\x83\xd1\x82 \xd0\xb2\xd0\xbf\xd1\x80\xd0\xb0\xd0\xb2\xd0\xbe')])),
                ('host_slot', models.IntegerField(default=0, verbose_name='\u041f\u0435\u0440\u0432\u044b\u0439(0) \u0438\u043b\u0438 \u0432\u0442\u043e\u0440\u043e\u0439(1) \u043c\u043e\u043d\u0438\u0442\u043e\u0440', choices=[(0, b'\xd0\xbf\xd0\xb5\xd1\x80\xd0\xb2\xd1\x8b\xd0\xb9'), (1, b'\xd0\xb2\xd1\x82\xd0\xbe\xd1\x80\xd0\xbe\xd0\xb9')])),
                ('sequence', models.IntegerField(default=0, verbose_name='\u041e\u0447\u0435\u0440\u0435\u0434\u043d\u043e\u0441\u0442\u044c')),
                ('host', models.ForeignKey(to='mc.Host')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_type', models.CharField(max_length=200, verbose_name='\u0422\u0438\u043f \u0441\u043e\u0434\u0435\u0440\u0436\u0438\u043c\u043e\u0433\u043e')),
                ('sequence', models.IntegerField(default=0, verbose_name='\u041e\u0447\u0435\u0440\u0435\u0434\u043d\u043e\u0441\u0442\u044c')),
                ('interval', models.IntegerField(verbose_name='\u0418\u043d\u0442\u0435\u0440\u0432\u0430\u043b \u0441\u043c\u0435\u043d\u044b \u043a\u0430\u0440\u0442\u0438\u043d\u043e\u043a, \u043c\u0441')),
                ('time_begin', models.TimeField(verbose_name='\u0412\u0440\u0435\u043c\u044f \u043d\u0430\u0447\u0430\u043b\u0430 \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u044f, \u0447\u0447:\u043c\u043c')),
                ('monitor', models.ForeignKey(to='mc.Monitor')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='item',
            name='playlist',
            field=models.ForeignKey(to='mc.Playlist'),
            preserve_default=True,
        ),
    ]
