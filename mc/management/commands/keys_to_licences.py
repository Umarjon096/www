# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import hashlib
import subprocess
from mc.utils import write_key
import os


class Command(BaseCommand):
    help = 'Rewrite key'

    def handle(self, *args, **options):
        uuid = subprocess.check_output("cat /proc/cpuinfo | grep ^Serial | awk {'print $3'}", shell=True).decode("utf-8").replace('\n', '')
        new_key = hashlib.sha224('hexadragon{0}'.format(uuid)).hexdigest()
        write_key(new_key)
        os.chmod('/var/www/django_starko/.key', 0o777)
