# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0029_pendingchanges'),
    ]

    operations = [
        migrations.AddField(
            model_name='pendingchanges',
            name='sync',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
