# -*- coding: utf-8 -*-

from django.conf.urls import *

from . import views

urlpatterns = (
    url(r'^upload/$', views.upload, name='upload'), # todo: fix!!! "upload" --> "upload_pagebuilder_file" e.t.c.
    url(r'^save/$', views.save, name='save'),
    url(r'^load/$', views.load, name='load'),
    url(r'^preview/$', views.preview, name='preview'),
    url(r'^export/$', views.export, name='export'),
)
