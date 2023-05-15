# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0035_auto_20170529_2111'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='is_nuc',
            field=models.BooleanField(default=False, verbose_name='NUC'),
            preserve_default=True,
        ),
    ]
