# -*- coding: utf-8 -*-
from datetime import  datetime
import json
import logging
import os
import time
import shutil

from django.core.files.base import ContentFile
from io import BytesIO

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.views.generic import View

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.template.response import TemplateResponse
from django.shortcuts import render
from django.utils import timezone
from transliterate import translit

# Create your views here.
from django_starko.settings import MEDIA_ROOT, BITRATE_LIMIT

from mc.models import Monitor, Playlist, Item, Host, File, Setting, Blackout, SavedUrl, \
    PendingChanges
from mc.utils import execute_ssh, make_scrnsht_and_len, get_thumbnail, get_bitrate, get_logo, apply_host, \
    delete_item_files, is_mon_ok, apply_all_hosts_blackout, get_volume, set_volume, is_master, \
    get_timezone_etc_timezone, current_song, process_ready_file, add_memory_data_to_context, current_image

logger = logging.getLogger(__name__)

def master_test(void):
    return is_master()

@user_passes_test(
    master_test,
    login_url="http://0.0.0.0",
    redirect_field_name=""
)
@login_required
@csrf_exempt
@add_memory_data_to_context
def index(request):
    if not is_master():
        return HttpResponseNotFound("<h1>Сервер не найден</h1>")

    monitors = Monitor.objects.all().order_by("sequence")

    monitors_json = []
    for mon in monitors:
        mon_with_health = mon.as_json()
        health, reason, license = is_mon_ok(mon)
        mon_with_health["health"] = health
        mon_with_health["health_reason"] = reason
        mon_with_health["licence"] = license
        try:
            health_obj = json.loads(mon.host.hostdiagstate_set.first().health)
            mon_with_health["bt"] = health_obj.get("bluetooth", False)
        except Exception as e:
            mon_with_health["bt"] = False
        monitors_json.append(mon_with_health)

    pls = Playlist.objects.all()
    pls_json = [pl.as_json() for pl in pls]

    items = Item.objects.all()
    surls = dict(SavedUrl.objects.values_list("url", "name"))
    items_json = []
    for item in items:
        try:
            item_json = item.as_json()
        except ObjectDoesNotExist:
            item.delete()

        if item.url:
            item_json["name"] = surls.get(item.url, item.url)

        item_json["duration"] = item.file.duration if item.file and item.file.duration else item.playlist.interval / 1000 if item.playlist.interval else 30
        items_json.append(item_json)

    context = {
        "all_monitors": json.dumps(monitors_json),
        "all_playlists": json.dumps(pls_json),
        "all_items": json.dumps(items_json),
        "cur_date": datetime.now()
    }
    ent_data = Setting.objects.get_name_and_address()
    context["ent_name"] = ent_data[0]
    context["ent_address"] = ent_data[1]
    context["logo_url"] = get_logo()

    return TemplateResponse(request, "mc/index.html", context)


@user_passes_test(
    master_test,
    login_url="http://0.0.0.0",
    redirect_field_name=""
)
@login_required
@csrf_exempt
@add_memory_data_to_context
def manual(request):
    return TemplateResponse(request, "mc/manual.html")


@csrf_exempt
def get_time(request):
    if not request.session.get("time_zone", False):
        request.session["time_zone"] = get_timezone_etc_timezone()
    return JsonResponse(dict(
        time=timezone.now().isoformat(),
        tz=request.session["time_zone"]
    ))


@csrf_exempt
def get_host_volume(request):
    mon_id = json.loads(request.body)
    host_mon = Monitor.objects.select_related("Host").get(pk=mon_id)
    cur_vol = get_volume(host_mon.host.ip)
    return HttpResponse(int(cur_vol) if cur_vol else 0)


@csrf_exempt
def set_host_volume(request):
    json_val = json.loads(request.body)
    mon_id = json_val["mon_id"]
    volume = json_val["volume"]
    host_mon = Monitor.objects.select_related("Host").get(pk=mon_id)
    cur_vol = set_volume(host_mon.host.ip, volume)
    return HttpResponse(float(cur_vol) if cur_vol else 0)


@csrf_exempt
def get_current_song(request):
    mon_id = int(request.body)
    host_mon = Monitor.objects.select_related("Host").get(pk=mon_id)
    cur_song = current_song(host_mon.host.ip)
    return HttpResponse(cur_song)


@csrf_exempt
def get_current_image(request):
    mon_id = int(request.body)
    host_mon = Monitor.objects.select_related("Host").get(pk=mon_id)
    host_ip = host_mon.host.ip
    image_name = current_image(host_ip)

    if host_ip in ("localhost", "127.0.0.1"):
        host_ip = execute_ssh(
            "localhost",
            "hostname -I",
            "out"
        ).replace("\n", "").split(" ")[0]

    if image_name is not None:
        return HttpResponse("http://{}/static/screen/{}".format(
            host_ip,
            image_name
        ))

    return HttpResponse(status=400)


@csrf_exempt
def ntp_check(request):
    """Синхронизируемся с ntp и возвращаем текущие дату и время"""
    err = execute_ssh(
        "localhost",
        "chronyc -a 'burst 4/4'",
        type_of_return="out"
    )
    time.sleep(8)
    err = execute_ssh(
        "localhost",
        "chronyc -a makestep",
        type_of_return="out"
    )
    time.sleep(1)
    err = execute_ssh(
        "localhost",
        "date",
        type_of_return="out"
    )
    return HttpResponse(err)



# Оставляем его для обратной совместимости
@csrf_exempt
def upload(request):
    if request.method == "POST":
        rdy_files = []
        for file in request.FILES.getlist("file"):

            newfile_name = translit(file.name, "ru", reversed=True)
            newfile = File.objects.create()
            newfile.data.save(newfile_name, file)
            newfile.name = os.path.basename(newfile_name)
            file_data = {}
            file_data["name"] = newfile.name
            file_data["url"] = newfile.data.url
            file_data["path"] = newfile.data.path
            file_data["type"] = file.content_type.split("/")[0]
            file_data["thumb_url"] = None
            if file_data["type"] in ("video", "image"):
                if file_data["type"] == "video":
                    scrn_path, dur = make_scrnsht_and_len(file_data["path"])
                    thumb_file, is_vertical = get_thumbnail(scrn_path)
                    newfile.duration = dur
                    newfile.bitrate = get_bitrate(file_data["path"])
                elif file_data["type"] == "image":
                    thumb_file, is_vertical = get_thumbnail(file_data["path"])
                newfile.thumbnail = os.path.join("thumbnails", thumb_file)
                newfile.is_vertical = is_vertical
                file_data["thumb_url"] = newfile.thumbnail.url

            newfile.save()
            file_data["file_id"] = newfile.id
            file_data["bitrate"] = newfile.bitrate
            file_data["bitrate_violation"] = newfile.bitrate > BITRATE_LIMIT
            rdy_files.append(file_data)

        return JsonResponse(rdy_files)

    return render(request, "mc/upload.html")








@csrf_exempt
def upload_chunks(request):
    """Загрузка файлов чанками эксклюзивно для dropzone."""
    if request.method == "POST":
        current_chunk = int(request.POST["dzchunkindex"])
        file_uuid = ".".join((
            request.POST["dzuuid"],
            request.POST["dzchunkindex"]
        ))
        full_path = os.path.join(MEDIA_ROOT, file_uuid)

        # Если получили начальный чанк, то будем создавать файл
        if current_chunk == 0:
            file_mode = "wb+"

        # Если чанк не первый, то допишем в существующий файл
        else:
            if os.path.isfile(full_path):
                file_mode = "ab"

            # Если не нашли файл, то вернем код ошибки
            else:
                return HttpResponse(status=400)

        with open(full_path, file_mode) as tmp_file:
            for chunk in request.FILES["file"].chunks():
                tmp_file.write(chunk)

        next_chunk = current_chunk + 1

        # Если остались необработанные чанки, то переименуем файл в
        # ожидании следующего чанка и вернем 2ХХ код
        if next_chunk != int(request.POST["dztotalchunkcount"]):
            new_name = full_path.rsplit(
                str(current_chunk),
                1
            )[0] + str(next_chunk)
            os.rename(full_path, new_name)
            status_code = 202 if current_chunk > 0 else 201
            return HttpResponse(status=status_code)

        # Если приняли все чанки, то обработаем файл
        # и вернем json с инфой
        else:
            file = request.FILES["file"]
            done_file = [process_ready_file(file, file_uuid)]
            return JsonResponse(done_file, safe=False)

    return




# TODO Удалить
@csrf_exempt
def big_file_meta(request):
    if request.method == "POST":
        rdy_files = []
        file_props = json.loads(request.body)
        fpath = file_props["fpath"]
        name = file_props["name"]
        newfile_name = translit(name, "ru", reversed=True)
        type = file_props["type"]

        # Separate base from extension
        base, extension = os.path.splitext(newfile_name)

        # Initial new name
        new_name = os.path.join(MEDIA_ROOT, base + extension)

        if not os.path.exists(new_name):  # folder exists, file does not
            shutil.move(fpath, new_name)
        else:  # folder exists, file exists as well
            i = 1
            while True:
                new_name = os.path.join(os.path.join(MEDIA_ROOT, base + "_" + str(i) + extension))
                if not os.path.exists(new_name):
                    shutil.move(fpath, new_name)
                    print("Copied", fpath, "as", new_name)
                    break
                i += 1

        newfile = File.objects.create()
        newfile.data = os.path.basename(new_name)
        newfile.name = os.path.basename(new_name)

        file_data = {}
        thumb_file = None
        file_data["name"] = newfile.name
        file_data["url"] = newfile.data.url
        file_data["path"] = newfile.data.path
        file_data["type"] = type.split("/")[0]
        if file_data["type"] == "video":
            scrn_path, dur = make_scrnsht_and_len(file_data["path"])
            thumb_file, is_vertical = get_thumbnail(scrn_path)
            newfile.duration = dur
            newfile.bitrate = get_bitrate(file_data["path"])
        elif file_data["type"] == "image":
            thumb_file, is_vertical = get_thumbnail(file_data["path"])
        if thumb_file:
            newfile.thumbnail = os.path.join("thumbnails", thumb_file)
            newfile.is_vertical = is_vertical
            file_data["thumb_url"] = newfile.thumbnail.url
        
        newfile.save()
        file_data["bitrate"] = newfile.bitrate
        file_data["bitrate_violation"] = newfile.bitrate > BITRATE_LIMIT
        file_data["file_id"] = newfile.id
        rdy_files.append(file_data)

        return HttpResponse(json.dumps(rdy_files))


def treat_item(item_props):
    if not item_props.get(u"only_save_url"):
        item = Item(
            type=item_props[u"type"],
            playlist_id=item_props[u"playlist"],
            sequence=item_props[u"sequence"],
            file_id=item_props.get(u"file_id"),
            url=item_props.get(u"url"),
            is_site=item_props.get(u"is_site"),
            is_script=item_props.get(u"is_script")
        )

        item.save()
        PendingChanges.objects.update_or_create(pk=1, defaults=dict(sync=True))

    if item_props.get(u"url_name") and not item_props.get(u"dont_save_url"):
        SavedUrl.objects.create(
            name=item_props[u"url_name"],
            url=item_props.get(u"url"),
            built_in=False
        )

    if item_props.get(u"only_save_url"):
        return None

    return item


@csrf_exempt
def item(request, item_id=None):
    if request.method == "POST":
        item_props = json.loads(request.body)

        if isinstance(item_props, list):
            rdy_items = []
            with transaction.atomic():
                for item in item_props:
                    if not item.get("id", None):
                        new_item = treat_item(item)
                        rdy_items.append(new_item.as_json())
            return HttpResponse(json.dumps(rdy_items))

        else:
            new_item = treat_item(item_props)
            return HttpResponse(json.dumps(new_item.as_json()))

    elif request.method == "DELETE":
        item = Item.objects.get(pk=item_id)
        file_id = item.file.id if item.file else None
        item.delete()

        if file_id:
            delete_item_files(file_id)
        PendingChanges.objects.update_or_create(pk=1, defaults=dict(sync=True))

        return HttpResponse("ok")


class SavedUrlView(View):
    """Api для сохранённых урлов"""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(SavedUrlView, self).dispatch(*args, **kwargs)

    def get(self, request):
        surls = SavedUrl.objects.all().order_by("id")
        surls_json = [su.as_json() for su in surls]
        return JsonResponse(surls_json, safe=False)

    def post(self, request):
        item_props = json.loads(request.body)
        if "delete_list" in item_props:
            SavedUrl.objects.filter(pk__in=item_props[u"delete_list"]).delete()
            return HttpResponse("ok")

        else:
            surl = SavedUrl.objects.create(
                url=item_props.get(u"url"),
                name=item_props.get(u"name"),
                video=item_props.get(u"video", False),
                audio=item_props.get(u"audio", False)
            )
            return JsonResponse({"id": surl.id})

    def put(self, request, surl_id):
        item_props = json.loads(request.body)
        surl = SavedUrl.objects.filter(pk=surl_id).update(
            url=item_props.get(u"url"),
            name=item_props.get(u"name"),
            video=item_props.get(u"video"),
            audio=item_props.get(u"audio")
        )
        return JsonResponse({"id": surl})

    def delete(self, request, surl_id):
        SavedUrl.objects.get(pk=surl_id).delete()
        return HttpResponse("ok")


@csrf_exempt
def playlist(request, playlist_id=None):
    # TODO Отрефакторить
    if request.method == "POST":
        pl_props = json.loads(request.body)

        pl = Playlist(
            content_type=pl_props[u"content_type"],
            monitor_id=pl_props[u"monitor"],
            sequence=pl_props[u"sequence"],
            shuffle=pl_props[u"shuffle"],
            is_adv=pl_props[u"is_adv"],
            adv_at_once=pl_props[u"adv_at_once"],
            fade_time=pl_props[u"fade_time"],
            interval=pl_props[u"interval"],
            volume=pl_props[u"volume"] if pl_props[u"volume"] != "" else None,
            scale_factor=pl_props[u"scale_factor"],
            url_refresh_mode=pl_props[u"url_refresh_mode"],
            time_begin=datetime.strptime(
                pl_props[u"time_begin"],
                "%H:%M"
            )
        )

        pl.save()
        PendingChanges.objects.update_or_create(
            pk=1,
            defaults=dict(sync=True)
        )

        return HttpResponse(json.dumps({"id": pl.id}))

    elif request.method == "DELETE":
        pl = Playlist.objects.get(pk=playlist_id)
        items = Item.objects.all().filter(playlist=pl)

        for item in items:
            file_id = item.file.id if item.file else None
            item.delete()

            if file_id:
                delete_item_files(file_id)

        pl.delete()
        PendingChanges.objects.update_or_create(pk=1, defaults=dict(sync=True))

        return HttpResponse("ok")

    elif request.method == "PUT":
        pl = Playlist.objects.get(pk=playlist_id)
        pl_props = json.loads(request.body)
        pl.content_type = pl_props[u"content_type"]
        pl.monitor_id = pl_props[u"monitor"]
        pl.sequence = pl_props[u"sequence"]
        pl.interval = pl_props[u"interval"]
        pl.shuffle = pl_props[u"shuffle"]
        pl.is_adv = pl_props[u"is_adv"]
        pl.volume = pl_props[u"volume"] if pl_props[u"volume"] != "" else None
        pl.adv_at_once = pl_props[u"adv_at_once"]
        pl.fade_time = pl_props[u"fade_time"]
        pl.scale_factor=pl_props[u"scale_factor"]
        pl.url_refresh_mode=pl_props[u"url_refresh_mode"]
        pl.time_begin = datetime.strptime(pl_props[u"time_begin"], "%H:%M")
        pl.save()
        PendingChanges.objects.update_or_create(pk=1, defaults=dict(sync=True))

        return HttpResponse("ok")


@csrf_exempt
def sort_items(request):
    string_items = json.loads(request.body)
    for string_item in string_items:
        item = Item.objects.get(pk=string_item[u"id"])
        item.sequence = string_item[u"sequence"]
        item.save()
    return HttpResponse("ok")


@csrf_exempt
def pl_command(request):
    string_item = json.loads(request.body)
    # для начала получим монитор
    mon = Monitor.objects.get(pk=string_item[u"id"])
    #а с помощью монитора получим хост
    host = Host.objects.get(pk=mon.host.id)  #переделать на __
    try:
        result = apply_host(host)
    except Exception as e:
        logger.error(u"Host {0} was not applied".format(host.name))
        logger.error(e)
        raise e
    return HttpResponse(result)


def reboot_interfaces(request):
    import paramiko

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("10.10.10.25", username="root", password="ph0nenumber")
    stdin, stdout, stderr = ssh.exec_command("/etc/init.d/networking restart")
    ssh.close()
    return HttpResponse("ok")


@csrf_exempt
def big_file_complete(request):
    fpath = request.META["HTTP_X_FILE"]
    return HttpResponse(json.dumps({"fpath": fpath}))


def blackouts(request):
    if request.method == "GET":
        bls = Blackout.objects.all()
        bls_json = [bl.as_json() for bl in bls]

        return HttpResponse(json.dumps(bls_json))

    if request.method == "POST":
        try:
            new_bls = json.loads(request.body)
            new_objs = []
            for k, v in new_bls.items():
                obj = Blackout(day_of_week=k, time_begin=v["time_begin"], time_end=v["time_end"])
                obj.full_clean()
                new_objs.append(obj)

            Blackout.objects.all().delete()
            for obj in new_objs:
                obj.save()
            pc, _ = PendingChanges.objects.get_or_create(pk=1)
            pc.blackouts=True
            pc.config=True
            pc.save()
            apply_all_hosts_blackout()

        except Exception as e:
            # return HttpResponse(e.message, status=500)
            return HttpResponse(str(e), status=500)


        bls = Blackout.objects.all()
        bls_json = [bl.as_json() for bl in bls]

        return HttpResponse(json.dumps(bls_json))
