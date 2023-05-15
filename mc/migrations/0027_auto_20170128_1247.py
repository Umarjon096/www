# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0025_savedurl'),
    ]

    def default_settings(apps, schema_editor):
        # We can't import the Person model directly as it may be a newer
        # version than this migration expects. We use the historical version.
        Setting = apps.get_model("mc", "Setting")
        Setting(name=u'Аккаунт на Opteo.pro (email)',
                code=u'reg_email',
                value=u'').save()

    def reverse_code(apps, schema_editor):
        pass

    operations = [
        migrations.RunPython(default_settings, reverse_code),
    ]
