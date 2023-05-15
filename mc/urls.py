# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.views.generic import TemplateView

from mc import views

admin.site.site_header = u'Панель администратора Opteo'

urlpatterns = [
    url(r'^upload/$', views.upload, name='upload'),
    url(r'^upload_chunks/$', views.upload_chunks, name='upload_chunks'),
    url(r'^big_file_meta/$', views.big_file_meta, name='big_file_meta'),
    url(r'^big_file_complete/$', views.big_file_complete, name='big_file_complete'),
    url(r'^item/$', views.item, name='item'),
    url(r'^item/(?P<item_id>[0-9]+)$', views.item, name='item'),
    url(r'^playlist/$', views.playlist, name='playlist'),
    url(r'^playlist/(?P<playlist_id>[0-9]+)$', views.playlist, name='playlist'),
    url(r'^sort_items/$', views.sort_items, name='sort_items'),
    url(r'^reboot/$', views.reboot_interfaces, name='reboot_interfaces'),
    url(r'^pl_command/$', views.pl_command, name='pl_command'),
    url(r'^blackouts/$', views.blackouts, name='blackouts'),

    # Мануал
    url(r'^manual/$', views.manual, name='manual'),

    # Урлы настроек
    url(r'^admin/$', views.admin_page, name='admin_page'),
    url(r'^admin/common/$', views.common, name='common'),
    url(r'^admin/network/$', views.Network.as_view(), name='network'),
    url(r'^admin/datetime/$', views.DatetimeConfig.as_view(), name='datetime'),
    url(r'^admin/sync/$', views.sync, name='sync'),
    url(r'^admin/license/$', views.license, name='license'),
    url(r'^admin/bluetooth/$', views.BluetoothConfig.as_view(), name='bluetooth'),
    url(r'^admin/diag/$', views.diag, name='diag'),
    url(r'^admin/host/$', views.HostAdmin.as_view(), name='host_settings'),
    url(r'^admin/host/(?P<obj_id>[0-9]+)$', views.HostAdmin.as_view(), name='host_settings'),
    url(r'^admin/monitor/$', views.MonitorAdmin.as_view(), name='mon_settings'),
    url(r'^admin/monitor/(?P<obj_id>[0-9]+)$', views.MonitorAdmin.as_view(), name='mon_settings'),
    url(r'^admin/setting/$', views.SettingAdmin.as_view(), name='set_settings'),
    url(r'^admin/setting/(?P<obj_id>[0-9]+)$', views.SettingAdmin.as_view(), name='set_settings'),
    url(r'^admin/syncschedule/$', views.SyncScheduleAdmin.as_view(), name='sync_schedule'),
    url(r'^admin/syncschedule/(?P<obj_id>[0-9]+)$', views.SyncScheduleAdmin.as_view(), name='sync_schedule'),
    url(r'^admin/synctype/$', views.SyncTypeAdmin.as_view(), name='sync_type'),
    url(r'^admin/synctype/(?P<obj_id>[0-9]+)$', views.SyncTypeAdmin.as_view(), name='sync_type'),
    url(r'^admin/boschedule/$', views.BlackoutAdmin.as_view(), name='blackout'),
    url(r'^admin/boschedule/(?P<obj_id>[0-9]+)$', views.BlackoutAdmin.as_view(), name='blackout'),
    url(r'^admin/user/$', views.UserAdmin.as_view(), name='user'),
    url(r'^admin/user/(?P<obj_id>[0-9]+)$', views.UserAdmin.as_view(), name='user'),
    url(r'^admin/about/$', views.about, name='about'),

    url(r'^spotify/$', views.Spotify.as_view(), name='spotify'),
    url(r'^spotify/(?P<host_id>[0-9]+)$', views.Spotify.as_view(), name='spotify'),

    url(r'^ntp_srv_ctl/$', views.ntp_srv_ctl, name='ntp_srv_ctl'),  # TODO Удалить
    url(r'^patch_upload/$', views.patch_upload, name='patch_upload'),
    url(r'^logo_upload/$', views.logo_upload, name='logo_upload'),
    url(r'^ntp_check/$', views.ntp_check, name='ntp_check'),
    url(r'^get_time/$', views.get_time, name='get_time'),
    url(r'^get_host_volume/$', views.get_host_volume, name='get_host_volume'),
    url(r'^set_host_volume/$', views.set_host_volume, name='set_host_volume'),
    url(r'^get_current_image/$', views.get_current_image, name="get_current_image"),
    url(r'^get_current_song/$', views.get_current_song, name='get_current_song'),
    url(r'^mon_res_list/$', views.mon_res_list, name='mon_res_list'),
    url(r'^wifi_quality/$', views.wifi_quality, name='wifi_quality'),
    url(r'^wifi_scan/$', views.wifi_scan, name='wifi_scan'),
    url(r'^saved_url/$', views.SavedUrlView.as_view(), name='saved_url'),
    url(r'^saved_url/(?P<surl_id>[0-9]+)$', views.SavedUrlView.as_view(), name='saved_url'),
    url(r'^login/$', login, {'template_name': 'mc/login.html'}, name='login'),
    url(r'^login_admin/$', login, {'template_name': 'mc/login_admin.html'}, name='login_admin'),  # TODO Удалить
    url(r'^logout/$', logout, {'next_page': '/login/'}, name='logout'),
    ###########################
    url(r'^export_conf/$', views.export_conf, name='export_conf'),
    url(r'^import_conf/$', views.import_conf, name='import_conf'),

    url(r'^export_radio/$', views.export_radio, name='export_radio'),
    url(r'^import_radio/$', views.import_radio, name='import_radio'),

    url(r'^key_license/$', views.KeyLicense.as_view(), name='key_license'),
    url(r'^multiple_key/$', views.KeyLicenseMultiple.as_view(), name='multiple_key'),
    url(r'^spawn_diag/$', views.spawn_diag, name='spawn_diag'),
    url(r'^reboot_all/$', views.Reboot.as_view(), name='reboot_all'),

    url(r'^diag_self/$', views.diag_self, name='diag_self'),
    url(r'^reboot_self/$', views.reboot_self, name='reboot_self'),
    url(r'^diag_me/$', views.diag_me, name='diag_me'),
    url(r'^send_media_name/$', views.send_media_name, name='send_media_name'),

    url(r'^$', views.index, name='index')
]


