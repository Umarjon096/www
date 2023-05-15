# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from mc.models import HostDiagArchive, SyncStateArchive
from mc.utils import delete_unused_files, delete_nginx_tmp, delete_not_db_files


class Command(BaseCommand):
    def handle(self, *args, **options):
        age_of_killing = timezone.now()-timedelta(days=30)
        HostDiagArchive.objects.filter(time__lte=age_of_killing).delete()
        SyncStateArchive.objects.filter(time__lte=age_of_killing).delete()
        delete_unused_files()
        delete_not_db_files()
        delete_nginx_tmp()
