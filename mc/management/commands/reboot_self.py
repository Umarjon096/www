# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from mc.utils.reboot import reboot_self

class Command(BaseCommand):
    help = 'Reboot by schedule'

    def handle(self, *args, **options):
        reboot_self()
