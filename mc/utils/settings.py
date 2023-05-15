# -*- coding: utf-8 -*-
import os
from datetime import datetime

from django_starko.settings import MEDIA_ROOT, MC_PATCH_FOLDER


def is_updating():
    """Проверяем идет ли обновление"""
    lock_path = os.path.join(MEDIA_ROOT, MC_PATCH_FOLDER, ".lock")
    locked = os.path.isfile(lock_path)
    if locked:
        locked_time = datetime.fromtimestamp(os.path.getmtime(lock_path))
        time_spent = datetime.now() - locked_time
        if time_spent.total_seconds() <= 60 * 60 * 24:
            return True
    return False
