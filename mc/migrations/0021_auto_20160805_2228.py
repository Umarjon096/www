# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0020_auto_20160624_2046'),
    ]

    def hybritize_playlists(apps, schema_editor):
        # We can't import the Playlist model directly as it may be a newer
        # version than this migration expects. We use the historical version.
        Playlist = apps.get_model("mc", "Playlist")
        Playlist.objects.all().update(content_type='hybrid')

    def reverse_code(apps, schema_editor):
        pass


    operations = [
        migrations.RunPython(hybritize_playlists, reverse_code),
    ]
