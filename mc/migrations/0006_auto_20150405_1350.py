# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0005_auto_20150405_1331'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='host',
            options={'verbose_name': '\u0425\u043e\u0441\u0442', 'verbose_name_plural': '\u0425\u043e\u0441\u0442\u044b'},
        ),
        migrations.AlterModelOptions(
            name='monitor',
            options={'verbose_name': '\u041c\u043e\u043d\u0438\u0442\u043e\u0440', 'verbose_name_plural': '\u041c\u043e\u043d\u0438\u0442\u043e\u0440\u044b'},
        ),
        migrations.AlterModelOptions(
            name='setting',
            options={'verbose_name': '\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430', 'verbose_name_plural': '\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438'},
        ),
        migrations.AlterModelOptions(
            name='syncschedule',
            options={'verbose_name': '\u0420\u0430\u0441\u043f\u0438\u0441\u0430\u043d\u0438\u0435 \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0430\u0446\u0438\u0438', 'verbose_name_plural': '\u0420\u0430\u0441\u043f\u0438\u0441\u0430\u043d\u0438\u0435 \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0430\u0446\u0438\u0438'},
        ),
        migrations.AlterModelOptions(
            name='syncscheduleoption',
            options={'verbose_name': '\u0422\u0438\u043f \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0430\u0446\u0438\u0438', 'verbose_name_plural': '\u0422\u0438\u043f \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0430\u0446\u0438\u0438'},
        ),
        migrations.AddField(
            model_name='monitor',
            name='resolution',
            field=models.CharField(default='1920x1080', max_length=50, verbose_name='\u0420\u0430\u0437\u0440\u0435\u0448\u0435\u043d\u0438\u0435 \u043c\u043e\u043d\u0438\u0442\u043e\u0440\u0430', choices=[(b'800x600', b'800x600'), (b'854x480', b'854x480'), (b'960x540', b'960x540'), (b'1024x600', b'1024x600'), (b'1024x768', b'1024x768'), (b'1152x864', b'1152x864'), (b'1200x600', b'1200x600'), (b'1280x720', b'1280x720'), (b'1280x768', b'1280x768'), (b'1280x1024', b'1280x1024'), (b'1440x900', b'1440x900'), (b'1400x1050', b'1400x1050'), (b'1440x1080', b'1440x1080'), (b'1536x960', b'1536x960'), (b'1536x1024', b'1536x1024'), (b'1600x900', b'1600x900'), (b'1600x1024', b'1600x1024'), (b'1680x1050', b'1680x1050'), (b'1920x1080', b'1920x1080')]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='lastsyncstate',
            name='status',
            field=models.CharField(max_length=200, verbose_name='\u0421\u0442\u0440\u043e\u043a\u043e\u0432\u044b\u0439 \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u0430', choices=[(b'synced', b'\xd0\xa1\xd0\xb8\xd0\xbd\xd1\x85\xd1\x80\xd0\xbe\xd0\xbd\xd0\xb8\xd0\xb7\xd0\xb8\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xbd\xd0\xbe'), (b'waiting_for_auth', b'\xd0\x9e\xd0\xb6\xd0\xb8\xd0\xb4\xd0\xb0\xd0\xb5\xd1\x82 \xd0\xb0\xd0\xb2\xd1\x82\xd0\xbe\xd1\x80\xd0\xb8\xd0\xb7\xd0\xb0\xd1\x86\xd0\xb8\xd0\xb8'), (b'error', b'\xd0\x9e\xd1\x88\xd0\xb8\xd0\xb1\xd0\xba\xd0\xb0 \xd1\x81\xd0\xb8\xd0\xbd\xd1\x85\xd1\x80\xd0\xbe\xd0\xbd\xd0\xb8\xd0\xb7\xd0\xb0\xd1\x86\xd0\xb8\xd0\xb8'), (b'nothing_to_sync', b'\xd0\x9d\xd0\xb5\xd1\x82 \xd0\xbe\xd0\xb1\xd0\xbd\xd0\xbe\xd0\xb2\xd0\xbb\xd0\xb5\xd0\xbd\xd0\xb8\xd0\xb9')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='syncstatearchive',
            name='status',
            field=models.CharField(max_length=200, verbose_name='\u0421\u0442\u0440\u043e\u043a\u043e\u0432\u044b\u0439 \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u0430', choices=[(b'synced', b'\xd0\xa1\xd0\xb8\xd0\xbd\xd1\x85\xd1\x80\xd0\xbe\xd0\xbd\xd0\xb8\xd0\xb7\xd0\xb8\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xbd\xd0\xbe'), (b'waiting_for_auth', b'\xd0\x9e\xd0\xb6\xd0\xb8\xd0\xb4\xd0\xb0\xd0\xb5\xd1\x82 \xd0\xb0\xd0\xb2\xd1\x82\xd0\xbe\xd1\x80\xd0\xb8\xd0\xb7\xd0\xb0\xd1\x86\xd0\xb8\xd0\xb8'), (b'error', b'\xd0\x9e\xd1\x88\xd0\xb8\xd0\xb1\xd0\xba\xd0\xb0 \xd1\x81\xd0\xb8\xd0\xbd\xd1\x85\xd1\x80\xd0\xbe\xd0\xbd\xd0\xb8\xd0\xb7\xd0\xb0\xd1\x86\xd0\xb8\xd0\xb8'), (b'nothing_to_sync', b'\xd0\x9d\xd0\xb5\xd1\x82 \xd0\xbe\xd0\xb1\xd0\xbd\xd0\xbe\xd0\xb2\xd0\xbb\xd0\xb5\xd0\xbd\xd0\xb8\xd0\xb9')]),
            preserve_default=True,
        ),
    ]
