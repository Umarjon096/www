# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0022_auto_20160806_1534'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='url',
            field=models.CharField(max_length=2000, null=True, verbose_name='URL', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='file',
            name='thumbnail',
            field=models.ImageField(upload_to=b'thumbnails', null=True, verbose_name='\u0421\u043a\u0440\u0438\u043d\u0448\u043e\u0442 \u0441 \u0444\u0430\u0439\u043b\u0430', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='file',
            field=models.ForeignKey(blank=True, to='mc.File', null=True),
            preserve_default=True,
        ),
    ]
