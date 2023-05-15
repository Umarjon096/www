# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from mc.utils import diagnose_all_hosts


class Command(BaseCommand):
    help = 'Diagnos everything around'

    def handle(self, *args, **options):
        res = diagnose_all_hosts()
        self.stdout.write(u"Diagnose: {0}".format(res))