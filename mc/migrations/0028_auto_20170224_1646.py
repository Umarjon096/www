# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0027_auto_20170128_1247'),
    ]

    def to_https(apps, schema_editor):
        # We can't import the Person model directly as it may be a newer
        # version than this migration expects. We use the historical version.
        Setting = apps.get_model("mc", "Setting")
        Setting.objects.update_or_create(code=u'global_url', defaults=dict(name=u'Адрес глобального мастера', value=u'https://opteo.pro'))

    def reverse_code(apps, schema_editor):
        pass

    operations = [
        migrations.RunPython(to_https, reverse_code),
    ]
