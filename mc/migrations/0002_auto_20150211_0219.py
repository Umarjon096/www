# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='data',
            field=models.FileField(upload_to=b'', verbose_name='\u0418\u0441\u0445\u043e\u0434\u043d\u044b\u0439 \u0444\u0430\u0439\u043b'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='file',
            name='thumbnail',
            field=models.ImageField(upload_to=b'thumbnails', verbose_name='\u0421\u043a\u0440\u0438\u043d\u0448\u043e\u0442 \u0441 \u0444\u0430\u0439\u043b\u0430'),
            preserve_default=True,
        ),
    ]
