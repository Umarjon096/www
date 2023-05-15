# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from mc.models import PendingChanges, Host, Monitor, Setting, SyncSchedule, SyncScheduleOption

logging.basicConfig(**settings.LOGGING)


def dont_raise(fn):
    def wrapped(*args, **kwargs):
        try:
            fn(*args, **kwargs)
        except Exception as e:
            logging.exception("signal error")
    return wrapped


@receiver(post_save, sender=Host, dispatch_uid='host_save')
@dont_raise
def host_save(sender, instance, created, raw, using, update_fields, **kwargs):
    PendingChanges.objects.update_or_create(pk=1, defaults=dict(config=True))


@receiver(post_delete, sender=Host, dispatch_uid='host_delete')
@dont_raise
def host_delete(sender, instance, created, raw, using, update_fields, **kwargs):
    PendingChanges.objects.update_or_create(pk=1, defaults=dict(config=True))


@receiver(post_save, sender=Monitor, dispatch_uid='monitor_save')
@dont_raise
def monitor_save(sender, instance, created, raw, using, update_fields, **kwargs):
    PendingChanges.objects.update_or_create(pk=1, defaults=dict(config=True))


@receiver(post_delete, sender=Monitor, dispatch_uid='monitor_delete')
@dont_raise
def monitor_delete(sender, instance, created, raw, using, update_fields, **kwargs):
    PendingChanges.objects.update_or_create(pk=1, defaults=dict(config=True))


@receiver(post_save, sender=Setting, dispatch_uid='setting_save')
@dont_raise
def setting_save(sender, instance, created, raw, using, update_fields, **kwargs):
    PendingChanges.objects.update_or_create(pk=1, defaults=dict(config=True))


@receiver(post_delete, sender=Setting, dispatch_uid='setting_delete')
@dont_raise
def setting_delete(sender, instance, created, raw, using, update_fields, **kwargs):
    PendingChanges.objects.update_or_create(pk=1, defaults=dict(config=True))


@receiver(post_save, sender=SyncSchedule, dispatch_uid='syncschedule_save')
@dont_raise
def syncschedule_save(sender, instance, created, raw, using, update_fields, **kwargs):
    PendingChanges.objects.update_or_create(pk=1, defaults=dict(config=True))


@receiver(post_delete, sender=SyncSchedule, dispatch_uid='syncschedule_delete')
@dont_raise
def syncschedule_delete(sender, instance, created, raw, using, update_fields, **kwargs):
    PendingChanges.objects.update_or_create(pk=1, defaults=dict(config=True))


@receiver(post_save, sender=SyncScheduleOption, dispatch_uid='syncscheduleopt_save')
@dont_raise
def syncscheduleopt_save(sender, instance, created, raw, using, update_fields, **kwargs):
    PendingChanges.objects.update_or_create(pk=1, defaults=dict(config=True))


@receiver(post_delete, sender=SyncScheduleOption, dispatch_uid='syncscheduleopt_delete')
@dont_raise
def syncscheduleopt_delete(sender, instance, created, raw, using, update_fields, **kwargs):
    PendingChanges.objects.update_or_create(pk=1, defaults=dict(config=True))