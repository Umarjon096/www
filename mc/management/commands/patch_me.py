# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from mc.utils import send_patch_request, is_master


class Command(BaseCommand):
    help = 'Get patch'

    def handle(self, *args, **options):
        if not is_master():
            return
        res = send_patch_request()
        self.stdout.write(u"Diag send result: {0}".format(res))