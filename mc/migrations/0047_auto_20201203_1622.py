# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0046_auto_20201111_1302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rebootsdata',
            name='host',
            field=models.ForeignKey(blank=True, to='mc.Host', null=True),
            preserve_default=True,
        ),
    ]
