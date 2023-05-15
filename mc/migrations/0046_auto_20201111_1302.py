# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0045_rebootsdata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rebootsdata',
            name='start',
            field=models.DateTimeField(null=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u0437\u0430\u043f\u0443\u0441\u043a\u0430 \u043f\u0435\u0440\u0435\u0437\u0430\u0433\u0440\u0443\u0437\u043a\u0438'),
            preserve_default=True,
        ),
    ]
