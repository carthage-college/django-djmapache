# -*- coding: utf-8 -*-

"""URLs for all views."""

from django.urls import path
from django.views.generic import TemplateView
from djmapache.indahaus import api
from djmapache.indahaus import views


urlpatterns = [
    # rest
    #path('clients/all/', api.spa, name='spa_json'),
    path('clients/<str:domain>/', api.clients, name='clients_api'),
    # clients UI
    path('clients/', views.clients, name='clients'),
    #path('spa/', views.spa, name='spa_html'),
]
