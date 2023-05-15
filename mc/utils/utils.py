# -*- coding: utf-8 -*-
import subprocess
from django.templatetags.static import static
from django_starko.settings import MC_VERSION
from mc.models import Setting

from .commands import get_uuid, execute_ssh


PI_MODELS = {
    "900021": "Opteo A+",
    "900032": "Opteo B+",
    "a01040": "Opteo 2B",
    "a01041": "Opteo 2B",
    "a02042": "Opteo 2B",
    "a21041": "Opteo 2B",
    "a22042": "Opteo 2B",
    "9020e0": "Opteo 3A+",
    "a02082": "Opteo 3B",
    "a22082": "Opteo 3B",
    "a32082": "Opteo 3B",
    "a52082": "Opteo 3B",
    "a22083": "Opteo 3B",
    "2a22082": "Opteo 3B",
    "a020d3": "Opteo 3B+",
    "a03111": "Opteo 4B",
    "b03111": "Opteo 4B",
    "b03112": "Opteo 4B",
    "b03114": "Opteo 4B",
    "c03111": "Opteo 4B",
    "c03112": "Opteo 4B",
    "c03114": "Opteo 4B",
    "d03114": "Opteo 4B",
    "900061": "Opteo CM",
    "a020a0": "Opteo CM3",
    "a220a0": "Opteo CM3",
    "a02100": "Opteo CM3+",
    "900092": "Opteo Zero",
    "900093": "Opteo Zero",
    "920092": "Opteo Zero",
    "920093": "Opteo Zero",
    "9000C1": "Opteo Zero W"
}


def human_readable(kbytes, units=None):
    """Преобразуем число килобайт в читаемый формат"""
    if units is None:
        units = ["Kb", "Mb", "Gb", "Tb"]
    if kbytes < 1024 or len(units) == 1:
        return str(round(kbytes, 2)) + units[0]
    else:
        return human_readable(kbytes / 1024.0, units[1:])


def get_logo():
    """Получаем путь к логотипу."""
    logo = None
    try:
        logo = Setting.objects.get(code="logo").value
    except Setting.DoesNotExist:
        logo = ""
    return logo


def get_memory_data():
    """Получаем данные о свободном пространстве."""
    command = 'df -hm /var/starko/ | grep ^/ | awk \'{print $2" "$3}\''
    str_idx = 0

    size = None
    used = None

    try:
        output = subprocess.check_output(command, shell=True).decode("utf-8")
        data = output.split("\n")[str_idx].split()
        size, used = data

    except:
        pass

    return size, used


def get_data_for_context():
    """Получаем данные для добавления в context."""
    context = {}

    context["uuid"] = get_uuid()

    size, used = get_memory_data()
    device = get_device_model()
    total_mem = get_total_memory()
    memory = round(total_mem/1024,1) if total_mem else '-'
    context["version_n_device"] = '{0} {1} {2}GB'.format(MC_VERSION, device, memory)
    context["max_media_size"] = get_max_resolution(device)

    if size is not None:
        # Отображаем только половину свободного пространства,
        # чтобы всегда оставалось место для загрузки данных с сервера
        half_size = int(size) / 2
        used = int(used)
        half_percent = int(float(used) / half_size * 100)
        half_left = half_size - used
        if half_left < 0:
            half_left = 0 
        context["disk_space_perc"] = half_percent
        context["disk_space"] = u"Использовано {0}/{1}".format(
            human_readable(used*1024),
            human_readable(half_size*1024)
        )
        context["disk_space_left"] = half_left*1024
        context["disk_space_left_pretty"] = u"Свободно {0}".format(
            human_readable(half_left*1024)
        )

    else:
        context["disk_space_perc"] = 0
        context["disk_space"] = ""
        context["disk_space_left"] = 0
        context["disk_space_left_pretty"] = u"Свободно -"

    return context


def add_memory_data_to_context(func):
    """Добавляем данные в 2ХХ ответ."""
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        if 200 <= response.status_code <= 299:
            if not response.context_data:
                response.context_data = {}
            response.context_data.update(get_data_for_context())
        return response
    return wrapper


def get_device_model():
    """Получаем модель девайса"""
    try:
        raw_version = subprocess.check_output(
            "grep Revision /proc/cpuinfo | awk {'print $3'}",
            shell=True
        ).decode("utf-8").strip()

        return PI_MODELS.get(raw_version, "-")

    except subprocess.CalledProcessError:
        return "-"

def get_total_memory():
    raw_version = execute_ssh('localhost', "vcgencmd get_config int | grep total_mem|awk -F= {'print $2'}", "out").strip()

    return int(raw_version)


def get_max_resolution(device_model):
    if device_model in ("Opteo 4B",
        "Opteo CM",
        "Opteo CM3",
        "Opteo CM3",
        "Opteo CM3+",):
        return 3840
    return 2048