# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0062_playlist_url_refresh_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='is_script',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
