# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db.models import FieldDoesNotExist

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
import json

from mc.models import Host, Monitor, Setting, SyncSchedule, SyncScheduleOption, Blackout, PendingChanges, vWallPixel
from mc.utils import apply_all_hosts_blackout


class DeCSRFedView(View):
    template_name = "secret.html"
    model = None

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(DeCSRFedView, self).dispatch(*args, **kwargs)

    def post_save(self, obj, props):
        pass

    def clean_props(self, props):
        return props

    def get(self, request, obj_id=None):
        _filter = dict()
        if obj_id:
            _filter["id"] = obj_id
        beings = self.model.objects.filter(**_filter)
        beings_json = [being.as_json() for being in beings]

        return HttpResponse(json.dumps(beings_json))

    def post(self, request):
        obj_props = self.clean_props(json.loads(request.body))
        obj = self.model()
        for key, value in obj_props.items():
            setattr(obj, key, value)

        try:
            obj.save()
            self.post_save(obj, obj_props)

        except Exception as e:
            return HttpResponse(e.message, status=500)

        # TODO Добавить name при ответе
        return HttpResponse(json.dumps({"id": obj.id}))

    def put(self, request, obj_id=None):
        obj_props = self.clean_props(json.loads(request.body))
        obj, created = self.model.objects.get_or_create(
            id=obj_id,
            defaults=dict(**obj_props)
        )
        if not created:
            for attr, value in obj_props.items():
                try:
                    setattr(obj, attr, value)
                except ValueError:
                    pass
        obj.save()

        try:
            self.post_save(obj, obj_props)

        except Exception as e:
            return HttpResponse(e.message, status=500)

        return HttpResponse(json.dumps({"id": obj.id}))

    def delete(self, request, obj_id=None):
        _filter = dict()
        if obj_id:
            _filter["id"] = obj_id
        objects = self.model.objects.filter(**_filter).delete()

        return HttpResponse(json.dumps({"status": "ok"}))


class HostAdmin(DeCSRFedView):
    model = Host

    def clean_props(self, props):
        if "name" in props:
            props.pop("name")
        return props


class MonitorAdmin(DeCSRFedView):
    model = Monitor

    def clean_props(self, props):
        # бугага, слоты подъехали!!!
        if props.get("nuc_mon"):
            return props

        # костыль для слотов. в пихе пока нет слотов, но не зарекайся!
        alrdy_mons = Monitor.objects.filter(
            host_id=props["host_id"]
        ).order_by("host_slot")
        free_slot = 0

        for mon in alrdy_mons:
            if mon.host_slot == free_slot:
                free_slot = mon.host_slot + 1

        props["host_slot"] = free_slot
        return props

    def post_save(self, obj, props):
        vWallPixel.objects.filter(monitor=obj).delete()
        for pix in props.get("pixels"):
            pix_obj = vWallPixel(**pix)
            pix_obj.monitor = obj

            host_for_diag, _ = Host.objects.get_or_create(
                ip=pix_obj.ip_address,
                defaults={"name":pix_obj.hostname}
            )

            mons = Monitor.objects.filter(
                host=host_for_diag,
                video_wall=False
            ).exists()

            if mons:
                raise ValueError(u"Выбраный хост уже установлен в системе")

            pix_obj.save()


class SettingAdmin(DeCSRFedView):
    model = Setting


class SyncScheduleAdmin(DeCSRFedView):
    model = SyncSchedule


class SyncTypeAdmin(DeCSRFedView):
    model = SyncScheduleOption


class BlackoutAdmin(DeCSRFedView):
    model = Blackout

    def post(self, request):
        obj_props = json.loads(request.body)
        if type(obj_props) == type([]):
            new_objs = []
            for item in obj_props:
                item.pop("day_of_week_str")
                obj = self.model(**item)

                try:
                    obj.full_clean(exclude=["id"])
                    new_objs.append(obj)

                except Exception as e:
                    error_strings = [
                        u", ".join(value) for key, value in e.message_dict.items()
                    ]
                    return HttpResponse(u"; ".join(error_strings), status=500)

            self.model.objects.all().delete()
            for obj in new_objs:
                obj.save()

            beings = self.model.objects.all()
            beings_json = [being.as_json() for being in beings]
            apply_all_hosts_blackout()
            return HttpResponse(json.dumps(beings_json))

        obj_props.pop("day_of_week_str")
        obj = self.model(**obj_props)

        try:
            obj.save()

        except Exception as e:
            return HttpResponse(e.message, status=500)

        PendingChanges.objects.update_or_create(
            pk=1,
            defaults=dict(blackouts=True, config=True)
        )
        apply_all_hosts_blackout()
        return HttpResponse(json.dumps({"id": obj.id}))


class UserAdmin(DeCSRFedView):
    model = User

    def get(self, request, obj_id=None):
        _filter = dict()

        if obj_id:
            _filter['id'] = obj_id

        beings = self.model.objects.filter(**_filter)
        beings_json = [being.as_json() for being in beings]

        return HttpResponse(json.dumps(beings_json))

    def post(self, request):
        obj_props = json.loads(request.body)

        try:
            new_usr = User.objects.create_user(
                obj_props['username'],
                obj_props['email'],
                obj_props['password'],
                first_name=obj_props['name']
            )

        except Exception as e:
            return HttpResponse(e.message, status=500)

        PendingChanges.objects.update_or_create(
            pk=1,
            defaults=dict(users=True)
        )

        return HttpResponse(json.dumps({"id": new_usr.id}))

    def put(self, request, obj_id=None):
        obj_props = json.loads(request.body)

        try:
            u = User.objects.get(id=obj_id)
            u.set_password(obj_props['password'])
            u.save()

        except Exception as e:
            return HttpResponse(e.message, status=500)

        PendingChanges.objects.update_or_create(
            pk=1,
            defaults=dict(users=True)
        )

        return HttpResponse(json.dumps({"id": u.id}))

    def delete(self, request, obj_id=None):
        _filter = dict()

        if obj_id:
            _filter['id'] = obj_id
            usr = self.model.objects.get(**_filter)

            if usr.is_staff:
                return HttpResponse(
                    u'Нельзя удалить администратора',
                    status=500
                )

        else:
            return HttpResponse(u'Нельзя удалить администратора', status=500)

        return super(UserAdmin, self).delete(request, obj_id)
