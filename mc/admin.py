from django.contrib import admin

from mc.models import Host, Monitor, Setting, SyncStateArchive, SyncScheduleOption, SyncSchedule, Blackout

admin.site.register([Host,Monitor])

from django.contrib.auth.models import User, Group

class SettingAdmin(admin.ModelAdmin):
    readonly_fields=('name','code',)
    def has_delete_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request):
        return False

admin.site.register(Setting, SettingAdmin)

class SyncArchive(admin.ModelAdmin):
    list_display = ('time', 'schedule_time', 'status', 'note')
    readonly_fields=('time', 'schedule_time', 'status', 'note')
    ordering = ['-time',]

    def has_add_permission(self, request):
        return False

admin.site.register(SyncStateArchive, SyncArchive)

class SyncScheduleOptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'enabled')
    readonly_fields=('id',)
    list_editable = ['enabled',]

    def has_add_permission(self, request):
        return False

admin.site.register(SyncScheduleOption, SyncScheduleOptionAdmin)


class SyncTimeTable(admin.ModelAdmin):
    list_display = ('id', 'time')
    readonly_fields = ('id',)
    list_editable = ['time']

admin.site.register(SyncSchedule, SyncTimeTable)


class BlackoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'time_begin', 'time_end')
    readonly_fields = ('id',)
    list_editable = ['time_begin', 'time_end']

admin.site.register(Blackout, BlackoutAdmin)


#admin.site.unregister(User)
admin.site.unregister(Group)
