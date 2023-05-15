# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    def default_settings(apps, schema_editor):
        # We can't import the Person model directly as it may be a newer
        # version than this migration expects. We use the historical version.
        Setting = apps.get_model("mc", "Setting")
        Setting(name=u'Название места установки',
                code=u'ent_name',
                value=u'').save()
        Setting(name=u'Адрес места установки',
                code=u'ent_address',
                value=u'').save()

    def reverse_code(apps, schema_editor):
        pass

    dependencies = [
        ('mc', '0004_lastsyncstate_syncschedule_syncscheduleoption_syncstatearchive'),
    ]

    operations = [
        migrations.RunPython(default_settings, reverse_code),
    ]
