# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mc', '0038_auto_20180606_2247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lastsyncstate',
            name='status',
            field=models.CharField(max_length=200, verbose_name='\u0421\u0442\u0440\u043e\u043a\u043e\u0432\u044b\u0439 \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442', choices=[(b'\xd0\x9e\xd0\xb6\xd0\xb8\xd0\xb4\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5 \xd0\xb0\xd0\xb2\xd1\x82\xd0\xbe\xd1\x80\xd0\xb8\xd0\xb7\xd0\xb0\xd1\x86\xd0\xb8\xd0\xb8', b'\xd0\x9e\xd0\xb6\xd0\xb8\xd0\xb4\xd0\xb0\xd0\xb5\xd1\x82 \xd0\xb0\xd0\xb2\xd1\x82\xd0\xbe\xd1\x80\xd0\xb8\xd0\xb7\xd0\xb0\xd1\x86\xd0\xb8\xd0\xb8'), (b'\xd0\x9d\xd0\xb5\xd1\x82 \xd0\xbe\xd0\xb1\xd0\xbd\xd0\xbe\xd0\xb2\xd0\xbb\xd0\xb5\xd0\xbd\xd0\xb8\xd0\xb9', b'\xd0\x9d\xd0\xb5\xd1\x82 \xd0\xbe\xd0\xb1\xd0\xbd\xd0\xbe\xd0\xb2\xd0\xbb\xd0\xb5\xd0\xbd\xd0\xb8\xd0\xb9'), (b'\xd0\xa1\xd0\xb8\xd0\xbd\xd1\x85\xd1\x80\xd0\xbe\xd0\xbd\xd0\xb8\xd0\xb7\xd0\xb8\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xbe', b'\xd0\xa1\xd0\xb8\xd0\xbd\xd1\x85\xd1\x80\xd0\xbe\xd0\xbd\xd0\xb8\xd0\xb7\xd0\xb8\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xbd\xd0\xbe'), (b'\xd0\x9e\xd1\x88\xd0\xb8\xd0\xb1\xd0\xba\xd0\xb0', b'\xd0\x9e\xd1\x88\xd0\xb8\xd0\xb1\xd0\xba\xd0\xb0 \xd1\x81\xd0\xb8\xd0\xbd\xd1\x85\xd1\x80\xd0\xbe\xd0\xbd\xd0\xb8\xd0\xb7\xd0\xb0\xd1\x86\xd0\xb8\xd0\xb8')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='syncstatearchive',
            name='status',
            field=models.CharField(max_length=200, verbose_name='\u0421\u0442\u0440\u043e\u043a\u043e\u0432\u044b\u0439 \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442', choices=[(b'\xd0\x9e\xd0\xb6\xd0\xb8\xd0\xb4\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5 \xd0\xb0\xd0\xb2\xd1\x82\xd0\xbe\xd1\x80\xd0\xb8\xd0\xb7\xd0\xb0\xd1\x86\xd0\xb8\xd0\xb8', b'\xd0\x9e\xd0\xb6\xd0\xb8\xd0\xb4\xd0\xb0\xd0\xb5\xd1\x82 \xd0\xb0\xd0\xb2\xd1\x82\xd0\xbe\xd1\x80\xd0\xb8\xd0\xb7\xd0\xb0\xd1\x86\xd0\xb8\xd0\xb8'), (b'\xd0\x9d\xd0\xb5\xd1\x82 \xd0\xbe\xd0\xb1\xd0\xbd\xd0\xbe\xd0\xb2\xd0\xbb\xd0\xb5\xd0\xbd\xd0\xb8\xd0\xb9', b'\xd0\x9d\xd0\xb5\xd1\x82 \xd0\xbe\xd0\xb1\xd0\xbd\xd0\xbe\xd0\xb2\xd0\xbb\xd0\xb5\xd0\xbd\xd0\xb8\xd0\xb9'), (b'\xd0\xa1\xd0\xb8\xd0\xbd\xd1\x85\xd1\x80\xd0\xbe\xd0\xbd\xd0\xb8\xd0\xb7\xd0\xb8\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xbe', b'\xd0\xa1\xd0\xb8\xd0\xbd\xd1\x85\xd1\x80\xd0\xbe\xd0\xbd\xd0\xb8\xd0\xb7\xd0\xb8\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xbd\xd0\xbe'), (b'\xd0\x9e\xd1\x88\xd0\xb8\xd0\xb1\xd0\xba\xd0\xb0', b'\xd0\x9e\xd1\x88\xd0\xb8\xd0\xb1\xd0\xba\xd0\xb0 \xd1\x81\xd0\xb8\xd0\xbd\xd1\x85\xd1\x80\xd0\xbe\xd0\xbd\xd0\xb8\xd0\xb7\xd0\xb0\xd1\x86\xd0\xb8\xd0\xb8')]),
            preserve_default=True,
        ),
    ]
