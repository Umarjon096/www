# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0021_auto_20160805_2228'),
    ]

    operations = [
        migrations.AddField(
            model_name='monitor',
            name='music_box',
            field=models.BooleanField(default=False, verbose_name='\u0410\u0443\u0434\u0438\u043e-\u043f\u043b\u0435\u0435\u0440'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='monitor',
            name='orientation',
            field=models.CharField(default=b'standard', max_length=200, verbose_name='\u041e\u0440\u0438\u0435\u043d\u0442\u0430\u0446\u0438\u044f (left/standard/right/inverted)', choices=[(b'left', b'\xd0\xbf\xd0\xbe\xd0\xb2\xd1\x91\xd1\x80\xd0\xbd\xd1\x83\xd1\x82 \xd0\xb2\xd0\xbb\xd0\xb5\xd0\xb2\xd0\xbe'), (b'standard', b'\xd0\xbe\xd0\xb1\xd1\x8b\xd1\x87\xd0\xbd\xd0\xb0\xd1\x8f'), (b'right', b'\xd0\xbf\xd0\xbe\xd0\xb2\xd1\x91\xd1\x80\xd0\xbd\xd1\x83\xd1\x82 \xd0\xb2\xd0\xbf\xd1\x80\xd0\xb0\xd0\xb2\xd0\xbe'), (b'inverted', b'\xd0\xbf\xd0\xb5\xd1\x80\xd0\xb5\xd0\xb2\xd1\x91\xd1\x80\xd0\xbd\xd1\x83\xd1\x82')]),
            preserve_default=True,
        ),
    ]
