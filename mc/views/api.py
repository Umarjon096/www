# -*- coding: utf-8 -*-
import json
import os

from django.http import HttpResponse, JsonResponse
from django.views.decorators import csrf
from django.views.decorators.csrf import csrf_exempt
from mc.utils import diagnose_all_hosts
from mc.utils.reboot import reboot_self as utils_reboot_self
from mc.utils.global_diag import send_diag_to_global
from django_starko.settings import STATIC_ROOT


@csrf_exempt
def diag_self(request):
    diagnose_all_hosts()
    return HttpResponse('ok')

@csrf_exempt
def reboot_self(request):
    utils_reboot_self()
    return HttpResponse('ok')

@csrf_exempt
def diag_me(request):
    send_diag_to_global()
    return HttpResponse('ok')

@csrf_exempt
def send_media_name(request):
    media_data = json.loads(request.body)
    print(media_data['fname'])
    script_file_path = os.path.join(STATIC_ROOT, '_cur_file')
    with open(script_file_path, "w") as myfile:
        myfile.write(media_data['fname'])
    return HttpResponse(dict(status='ok'))

