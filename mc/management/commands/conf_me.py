# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from mc.utils import is_master, send_config_request


class Command(BaseCommand):
    help = 'Send conf info to global'

    def handle(self, *args, **options):
        if not is_master():
            return
        res = send_config_request()
        self.stdout.write(u"Conf send result: {0}".format(res))