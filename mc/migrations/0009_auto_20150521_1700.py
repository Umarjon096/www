# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0008_auto_20150516_1159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monitor',
            name='resolution',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='\u0420\u0430\u0437\u0440\u0435\u0448\u0435\u043d\u0438\u0435 \u043c\u043e\u043d\u0438\u0442\u043e\u0440\u0430', choices=[(b'800x600', b'800x600'), (b'854x480', b'854x480'), (b'960x540', b'960x540'), (b'1024x600', b'1024x600'), (b'1024x768', b'1024x768'), (b'1152x864', b'1152x864'), (b'1200x600', b'1200x600'), (b'1280x720', b'1280x720'), (b'1280x768', b'1280x768'), (b'1280x1024', b'1280x1024'), (b'1440x900', b'1440x900'), (b'1400x1050', b'1400x1050'), (b'1440x1080', b'1440x1080'), (b'1536x960', b'1536x960'), (b'1536x1024', b'1536x1024'), (b'1600x900', b'1600x900'), (b'1600x1024', b'1600x1024'), (b'1680x1050', b'1680x1050'), (b'1920x1080', b'1920x1080')]),
            preserve_default=True,
        ),
    ]
