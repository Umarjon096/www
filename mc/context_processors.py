# -*- coding: utf-8 -*-
from django_starko.settings import MC_VERSION, TIME_ZONE, UUID, BT_ON



def show_version(request):
        return {
            'version': MC_VERSION,
            'uuid': UUID,
            'bt_on': BT_ON
        }

def show_tz(request):
    return {
        'time_zone': TIME_ZONE
    }