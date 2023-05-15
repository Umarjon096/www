# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0036_host_is_nuc'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='host',
            name='gateway',
        ),
        migrations.RemoveField(
            model_name='host',
            name='netmask',
        ),
    ]
