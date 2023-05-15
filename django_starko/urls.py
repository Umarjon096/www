# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from django.conf.urls.static import static

from django.contrib import admin
from django_starko import settings
from django.views.static import serve

admin.autodiscover()
urlpatterns = [
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    url(r'^', include('mc.urls'))
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'django_starko.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    #url(r'^admin/login/$', 'django.contrib.auth.views.login', {'template_name': 'mc/login.html'}, name='login'),
    #url(r'^admin/', include(admin.site.urls)),
    #url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    #url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    #url(r'^', include('mc.urls'))
#)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
