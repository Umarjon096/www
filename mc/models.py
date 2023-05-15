# -*- coding: utf-8 -*-
import hashlib
import json
import datetime

from django.contrib.auth.models import User
from django.db import models
from django_starko.settings import BITRATE_LIMIT

# Create your models here.
class SettingManager(models.Manager):
    def get_name_and_address(self):
        ent_data = self.filter(code__in=('ent_name', 'ent_address'))
        ent_name, ent_address = None, None
        for rec in ent_data:
            if rec.code == 'ent_name':
                ent_name = rec.value
            elif rec.code == 'ent_address':
                ent_address = rec.value
        return ent_name, ent_address

class Setting(models.Model):
    name = models.CharField(max_length=200, verbose_name=u'Название параметра')
    code = models.CharField(max_length=200, verbose_name=u'Код параметра (понятный компьютерам)', unique=True)
    value = models.CharField(max_length=2000, verbose_name=u'Значение параметра')

    objects = SettingManager()

    def as_json(self):
        return dict(
            id=self.id,
            name=self.name,
            code=self.code,
            value=self.value)

    def __unicode__(self):
        return u'{0}'.format(self.name)

    class Meta:
        verbose_name = u'Настройка'
        verbose_name_plural = u'Настройки'

class SyncScheduleOption(models.Model):
    enabled = models.BooleanField(verbose_name=u'Включено ли обновление по расписанию (в противном случае работает периодическое', default=False)

    def as_json(self):
        return dict(
            id=self.id,
            enabled=self.enabled
        )

    class Meta:
        verbose_name = u'Тип синхронизации'
        verbose_name_plural = u'Тип синхронизации'

class SyncSchedule(models.Model):
    # TODO Добавить name?
    time = models.TimeField(verbose_name=u'Плановое время запроса обновлений с глобала')

    def as_json(self):
        return dict(
            id=self.id,
            time=self.time.strftime('%H:%M')
        )

    class Meta:
        verbose_name = u'Расписание синхронизации'
        verbose_name_plural = u'Расписание синхронизации'

class SyncStatuses(dict):
    SYNCED = 'Синхронизировано'
    NOTHING_TO_SYNC = 'Нет обновлений'
    WAITING_FOR_AUTH = 'Ожидание авторизации'
    ERROR = 'Ошибка'


SYNC_STATUSES_CHOICES = ({
    (SyncStatuses.SYNCED, 'Синхронизированно'),
    (SyncStatuses.NOTHING_TO_SYNC, 'Нет обновлений'),
    (SyncStatuses.WAITING_FOR_AUTH, 'Ожидает авторизации'),
    (SyncStatuses.ERROR, 'Ошибка синхронизации'),}
)

class SyncState(models.Model):
    time = models.DateTimeField(verbose_name=u'Дата попытки синхронизации', auto_now_add=True)
    schedule_time = models.DateTimeField(verbose_name=u'Плановая дата попытки синхронизации', blank=True, null=True)
    status = models.CharField(max_length=200, verbose_name=u'Строковый результат', choices=SYNC_STATUSES_CHOICES)
    note = models.TextField(verbose_name=u'Детальное описание результата', blank=True, null=True)

    def __unicode__(self):
        return u'{0}: {1}'.format(self.time, self.status)

    class Meta:
        abstract = True

class LastSyncState(SyncState):

    class Meta:
        verbose_name = u'Последнее состояние синхронизации'
        verbose_name_plural = u'Последние состояния синхронизации'

class SyncStateArchive(SyncState):

    class Meta:
        verbose_name = u'Архивное состояние синхронизации'
        verbose_name_plural = u'Архивные состояния синхронизации'

class Host(models.Model):
    #name = models.CharField(max_length=200, verbose_name=u'Имя устройства', blank=True, null=True, unique=True)
    ip = models.CharField(max_length=200, verbose_name=u'IP', blank=True, null=True, unique=True)
    is_nuc = models.BooleanField(default=False, verbose_name=u'NUC')

    @property
    def name(self):
        return 'opteo{0}'.format(self.ip.split('.')[3])

    def __unicode__(self):
        return u'{0}'.format(self.name)

    def as_json(self):
        vw_p = vWallPixel.objects.filter(ip_address=self.ip)
        vw_mon_id = None
        vw_taken = False
        if vw_p:
            vw_taken = True
            vw_mon_id = vw_p[0].monitor_id
        vw_mon = Monitor.objects.filter(host=self, video_wall=True).exists()
        sync_mon = Monitor.objects.filter(host=self).exclude(sync_group=0, sync_group__isnull=True)
        sync_group = None
        if sync_mon:
            sync_group = sync_mon[0].sync_group
        return dict(
            id=self.id,
            name=self.name,
            ip=self.ip,
            vw_taken=vw_taken and not vw_mon,
            is_nuc=self.is_nuc,
            vw_mon_id = vw_mon_id,
            sync_group=sync_group
        )

    class Meta:
        verbose_name = u'Устройство'
        verbose_name_plural = u'Устройства'

SOUND_OUTPUT_CHOICES = (
    ('mini-jack', 'mini-jack'),
    ('hdmi', 'HDMI'),
)

resolutions = (
    '800x600',
    '854x480',
    '960x540',
    '1024x600',
    '1024x768',
    '1152x864',
    '1200x600',
    '1280x720',
    '1280x768',
    '1280x1024',
    '1440x900',
    '1400x1050',
    '1440x1080',
    '1536x960',
    '1536x1024',
    '1600x900',
    '1600x1024',
    '1680x1050',
    '1920x1080'
)
res_choices = [(res,res,) for res in resolutions]

MON_ORIENTATION_CHOICES = (
    ('left', 'повёрнут влево'),
    ('standard', 'обычная'),
    ('right', 'повёрнут вправо'),
    ('inverted', 'перевёрнут'),
)


class Monitor(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name=u'Название монитора',
        blank=True,
        null=True
    )
    host = models.ForeignKey(
        Host
    )
    orientation = models.CharField(
        max_length=200,
        default='standard',
        verbose_name=u'Ориентация (left/standard/right/inverted)',
        choices=MON_ORIENTATION_CHOICES
    )
    host_slot = models.IntegerField(
        default=0,
        verbose_name=u'Первый(0) или второй(1) монитор',
        choices=[(0, 'первый'), (1, 'второй')]
    )
    sequence = models.IntegerField(
        default=0,
        verbose_name=u'Очередность'
    )
    resolution = models.CharField(
        max_length=50,
        verbose_name=u'Разрешение монитора',
        null=True,
        blank=True
    )
    music_box = models.BooleanField(
        default=False,
        verbose_name=u'Аудио-плеер'
    )
    spotify = models.BooleanField(
        default=False,
        verbose_name=u"Монитор в режиме Spotify Connect"
    )
    volume_locked = models.BooleanField(
        default=False,
        verbose_name=u'Громкость фиксирована'
    )
    video_wall = models.BooleanField(
        default=False,
        verbose_name=u'Видео-стена'
    )
    video_wall_x = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=u'Размер стены по горизонтали'
    )
    video_wall_y = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=u'Размер стены по горизонтали'
    )
    video_wall_borders = models.PositiveIntegerField(
        default=0,
        verbose_name=u'Размер рамки (в пикселях)'
    )
    sync_group = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=u'Группа синхронизации'
    )
    audio_output = models.IntegerField(
        default=0,
        verbose_name=u"Вывод звука выключен(0), на jack(1) или hdmi(2)",
        choices=[(0, "off"), (1, "3.5mm jack"), (2, "hdmi")]
    )

    def __unicode__(self):
        return u'{0}'.format(self.name)

    def as_json(self):
        pixels = []
        for pix in vWallPixel.objects.filter(monitor=self):
            pixels.append(dict(
                x_pos=pix.x_pos,
                y_pos=pix.y_pos,
                ip_address=pix.ip_address,
                hostname=pix.hostname,
                inverted=pix.inverted
            ))

        return dict(
            id=self.id,
            name=self.name,
            host=self.host_id,
            host_id=self.host_id,
            host_slot=self.host_slot,
            orientation=self.orientation,
            sequence=self.sequence,
            music_box=self.music_box,
            volume_locked=self.volume_locked,
            video_wall=self.video_wall,
            video_wall_x=self.video_wall_x if self.video_wall_x else 1,
            video_wall_y=self.video_wall_y if self.video_wall_y else 1,
            video_wall_borders=self.video_wall_borders,
            pixels=pixels,
            nuc_mon=self.host.is_nuc,
            resolution=self.resolution,
            sync_group=self.sync_group,
            spotify=self.spotify,
            audio_output=self.audio_output
        )

    class Meta:
        unique_together = (("host","host_slot"),)
        verbose_name = u'Монитор'
        verbose_name_plural = u'Мониторы'


class vWallPixel(models.Model):
    monitor = models.ForeignKey(Monitor)
    x_pos = models.PositiveSmallIntegerField(verbose_name=u'Координата X')
    y_pos = models.PositiveSmallIntegerField(verbose_name=u'Координата Y')
    ip_address = models.GenericIPAddressField(verbose_name=u'IP')
    inverted = models.BooleanField(default=False, verbose_name=u'Перевёрнут')

    @property
    def hostname(self):
        return 'pixel{0}'.format(self.ip_address.split('.')[3])

    class Meta:
        verbose_name = u'Ячейка видеостены'
        verbose_name_plural = u'Ячейки видеостены'


class Playlist(models.Model):
    monitor = models.ForeignKey(Monitor)
    content_type = models.CharField(max_length=200, verbose_name=u'Тип содержимого')
    sequence = models.IntegerField(default=0, verbose_name=u'Очередность')
    interval = models.IntegerField(verbose_name=u'Интервал смены картинок, мс')
    time_begin = models.TimeField(verbose_name=u'Время начала действия, чч:мм')
    shuffle = models.BooleanField(verbose_name=u'Вперемешку', default=False)
    is_adv = models.BooleanField(verbose_name=u'Рекламный', default=False)
    fade_time = models.IntegerField(verbose_name=u'Длительность перехода картинок, мс')
    adv_at_once = models.BooleanField(verbose_name=u'Проигрывать все файлы разом', default=False)
    last_updated = models.DateTimeField(auto_now=True)
    volume = models.IntegerField(verbose_name=u'Громкость отдельного плейлиста', null=True, blank=True)
    scale_factor = models.PositiveIntegerField(verbose_name=u'Масштаб браузера', default=100)
    url_refresh_mode = models.PositiveIntegerField(verbose_name=u'Масштаб браузера', null=True, blank=True)

    def __unicode__(self):
        return str(self.sequence)

    def as_json(self):
        return dict(
            id=self.id,
            monitor=self.monitor_id,
            content_type=self.content_type,
            interval=self.interval,
            time_begin=self.time_begin.strftime('%H:%M'),
            sequence=self.sequence,
            shuffle=self.shuffle,
            is_adv=self.is_adv,
            fade_time=self.fade_time,
            adv_at_once=self.adv_at_once,
            last_updated=self.last_updated.strftime("%a, %d %b %Y %X %Z %z"),
            volume=self.volume,
            scale_factor=self.scale_factor,
            url_refresh_mode=self.url_refresh_mode
        )


# class File(models.Model):
#     name = models.CharField(
#         max_length=200,
#         verbose_name=u'Название файла',
#         blank=True,
#         null=True
#     )
#     data = models.FileField(
#         verbose_name=u"Исходный файл"
#     )
#     thumbnail = models.ImageField(
#         verbose_name=u"Скриншот с файла",
#         upload_to='thumbnails',
#         blank=True,
#         null=True
#     )
#     duration = models.FloatField(
#         verbose_name=u'Длительность в сек',
#         default=0.0
#     )
#     bitrate = models.IntegerField(
#         verbose_name=u'Битрейт',
#         default=0
#     )
#     is_vertical = models.BooleanField(
#         verbose_name=u"Вертикально ориентированная картинка",
#         default=False
#     )

#     def __unicode__(self):
#         return u'{0}'.format(self.name)


class File(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название файла',
        blank=True,
        null=True
    )
    data = models.FileField(
        verbose_name='Исходный файл'
    )
    thumbnail = models.ImageField(
        verbose_name='Скриншот с файла',
        upload_to='thumbnails',
        blank=True,
        null=True
    )
    duration = models.FloatField(
        verbose_name='Длительность в сек',
        default=0.0
    )
    bitrate = models.IntegerField(
        verbose_name='Битрейт',
        default=0
    )
    is_vertical = models.BooleanField(
        verbose_name='Вертикально ориентированная картинка',
        default=False
    )

    def __str__(self):
        return self.name



class Item(models.Model):
    type = models.CharField(max_length=200, verbose_name=u'Тип медиа')
    playlist = models.ForeignKey(Playlist)
    sequence = models.IntegerField(default=0, verbose_name=u'Очередность')
    file = models.ForeignKey(File, blank=True, null=True, on_delete=models.CASCADE)
    url = models.CharField(max_length=2000, verbose_name=u'URL', null=True, blank=True)
    is_site = models.BooleanField(default=False)
    is_script = models.BooleanField(default=False)

    def __unicode__(self):
        return u'{0}'.format(self.id)

    def as_json(self):
        if self.url:
            try:
                url_name = SavedUrl.objects.get(url = self.url).name
            except (SavedUrl.DoesNotExist, SavedUrl.MultipleObjectsReturned) as e:
                url_name = self.url
        return dict(
            id=self.id,
            playlist=self.playlist_id,
            type=self.type,
            name=self.file.name if self.file else url_name if self.url else None,
            file_url=self.file.data.url if self.file else None,
            local_path=self.file.data.path if self.file else None,
            sequence=self.sequence,
            thumb_url=self.file.thumbnail.url if self.file and self.file.thumbnail else None,
            url=self.url,
            is_site=self.is_site,
            is_script=self.is_script,
            bitrate=self.file.bitrate if self.file else 0,
            bitrate_violation=self.bitrate_violation,
            wrong_orientation=self.wrong_orientation
        )

    def as_sync_json(self):
        return dict(
            id=self.id,
            playlist=self.playlist_id,
            type=self.type,
            name=self.file.name,
            sequence=self.sequence,
            thumb_url=self.file.thumbnail.url,
            url=self.url,
            is_site=self.is_site,
            is_script=self.is_script,
            )
    
    @property
    def bitrate_violation(self):
        return self.file.bitrate > BITRATE_LIMIT if self.file else False

    @property
    def wrong_orientation(self):
        return bool(self.file and ((self.file.is_vertical and self.playlist.monitor.orientation not in ('left', 'right')) or \
                (not self.file.is_vertical and self.playlist.monitor.orientation in ('left', 'right'))))


class RadioManager(models.Manager):

    def as_sync_json(self):
        result_list = []
        for obj in self.get_queryset().filter(built_in=True).order_by('url'):
            result_list.append(obj.as_sync_json())
        return result_list

    def get_sha(self):
        result_list = []
        for obj in self.get_queryset().filter(built_in=True).order_by('url'):
            result_list.append(obj.as_sync_json())
        sha_data = hashlib.sha224(json.dumps(result_list)).hexdigest()
        return sha_data

class SavedUrl(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name=u"Название"
    )

    url = models.CharField(
        max_length=2000,
        verbose_name=u"URL",
        null=True,
        blank=True
    )

    built_in = models.BooleanField(
        verbose_name=u"Признак встроенная ли в систему ссылка на поток",
        default=True
    )

    video = models.BooleanField(
        verbose_name=u"Признак того, что это ссылка на видеострим",
        default=False
    )

    audio = models.BooleanField(
        verbose_name=u"Признак того, что это ссылка на аудиострим",
        default=False
    )

    objects = models.Manager()
    sync_manager = RadioManager()

    def __unicode__(self):
        return u'{0}'.format(self.name)

    def as_json(self):
        return dict(
            id=self.id,
            name=self.name,
            url=self.url,
            video=self.video,
            audio=self.audio
        )

    def as_sync_json(self):
        return dict(
            name=self.name,
            url=self.url,
            video=self.video,
            audio=self.audio
        )


class HostDiag(models.Model):
    host = models.ForeignKey(Host, on_delete=models.CASCADE)
    #time = models.DateTimeField(verbose_name=u'Время сбора диагностики').auto_now_add
    time = models.DateTimeField(verbose_name=u'Время сбора диагностики', auto_now_add=True)
    ping = models.BooleanField(verbose_name=u'Есть ли пинг до хоста', default=False)
    webserver = models.BooleanField(verbose_name=u'Поднят ли веб сервер', default=True)
    health = models.TextField(verbose_name=u'json с диагностической информацией', blank=True, null=True)

    def __unicode__(self):
        return u'{0}: {1}'.format(self.host.name, self.time)

    class Meta:
        abstract = True


class HostDiagState(HostDiag):
    def save(self, *args, **kwargs):
        self.pending_changes = True
        super(HostDiagState, self).save(*args, **kwargs)

    class Meta:
        verbose_name = u'Последнее состояние диагностики'
        verbose_name_plural = u'Последние состояния диагностики'
        unique_together = (("host",),)

    def as_sync_json(self):
        return dict(
            host_id=self.host.id,
            time=self.time.now(),
            ping=self.ping,
            webserver=self.webserver,
            health=self.health
        )


class HostDiagArchive(HostDiag):

    class Meta:
        verbose_name = u'Последнее состояние диагностики'
        verbose_name_plural = u'Последние состояния диагностики'


class Blackout(models.Model):
    time_begin = models.TimeField(verbose_name=u'Время начала действия, чч:мм')
    time_end = models.TimeField(verbose_name=u'Время окончания действия, чч:мм')
    day_of_week = models.IntegerField(verbose_name=u'День недели', null=True, blank=True)

    day_letters = {
        0: 'Все',
        1: 'Пн',
        2: 'Вт',
        3: 'Ср',
        4: 'Чт',
        5: 'Пт',
        6: 'Сб',
        7: 'Вс'
        }

    class Meta:
        verbose_name = u'Период неактивности мониторов'
        verbose_name_plural = u'Периоды неактивности мониторов'

    def __unicode__(self):
        return '{0}: {1} - {2}'.format(self.day_of_week, self.time_begin, self.time_end)

    def as_json(self):
        return dict(
            id=self.id,
            time_begin=self.time_begin.strftime('%H:%M'),
            time_end=self.time_end.strftime('%H:%M'),
            day_of_week=self.day_of_week,
            day_of_week_str=self.day_letters.get(self.day_of_week, self.day_letters[0])
        )


class RebootLog(models.Model):
    scheduled_time = models.DateTimeField(
        verbose_name=u"Назначенная дата перезагрузки"
    )

    processed_time = models.DateTimeField(
        verbose_name=u"Назначенная дата перезагрузки",
        auto_now=True
    )

    class Meta:
        verbose_name = u"Лог перезагрузки"
        verbose_name_plural = u"Логи перезагрузки"


class RebootsData(models.Model):
    """Для проверки успешности перезагрузок по команде"""
    start = models.DateTimeField(
        verbose_name=u"Время запуска перезагрузки",
        null=True
    )

    check = models.DateTimeField(
        verbose_name=u"Время, когда факт перезагрузки был проверен",
        blank=True,
        null=True
    )

    host = models.ForeignKey(
        Host,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = u"Перезагрузка по команде"
        verbose_name_plural = u"Перезагрузки по команде"

    def as_json(self):
        """Для возврата в JSON"""
        if self.host is None:
            json_host = {
                "ip": "localhost",
                "name": "Master"
            }

        else:
            json_host = self.host.as_json()

        return dict(
            host=json_host,
            start=self.start,
            check=self.check
        )


class PendingChanges(models.Model):
    blackouts = models.BooleanField(default=False)
    users = models.BooleanField(default=False)
    config = models.BooleanField(default=False)
    sync = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.pk = 1
        super(PendingChanges, self).save(*args, **kwargs)

    class Meta:
        verbose_name = u'Индикатор обновившихся данных'
        verbose_name_plural = u'Индикаторы обновившихся данных'

def user_as_json(self):
    return dict(
        id=self.id,
        username=self.username,
        email=self.email,
        name=self.first_name
    )

User.add_to_class('as_json', user_as_json)