# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0019_auto_20160509_1544'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='monitor',
            unique_together=set([('host', 'host_slot')]),
        ),
    ]
