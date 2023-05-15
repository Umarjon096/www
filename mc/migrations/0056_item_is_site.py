# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0055_savedurl_audio'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='is_site',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
