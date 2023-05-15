# -*- coding: utf-8 -*-
from django.apps import AppConfig

class MCAppConfig(AppConfig):
    name = u'mc'
    verbose_name = u'Панель управления мониторами'

    def ready(self):
        import mc.signals