# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0049_auto_20201216_1137'),
    ]

    operations = [
        migrations.AddField(
            model_name='monitor',
            name='audio_output',
            field=models.IntegerField(default=0, verbose_name='\u0412\u044b\u0432\u043e\u0434 \u0437\u0432\u0443\u043a\u0430 \u043d\u0430 jack(0) \u0438\u043b\u0438 hdmi(1)', choices=[(0, b'3.5mm jack'), (1, b'hdmi')]),
            preserve_default=True,
        ),
    ]
