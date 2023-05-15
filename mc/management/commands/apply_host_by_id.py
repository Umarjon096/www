# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from mc.models import Host
from mc.utils import apply_host


class Command(BaseCommand):
    help = 'Apply host or hosts'
    args = '<host_id> <copy_files>'

    def handle(self, *args, **options):
        host = None
        copy_files = True
        if args:
            try:
                host = Host.objects.get(pk=int(args[0]))
                if len(args)> 1:
                    if args[1] == 'False':
                        copy_files = False
            except Exception as e:
                raise CommandError('Error: {0}'.format(e.message))
        apply_host(host, copy_files=copy_files)