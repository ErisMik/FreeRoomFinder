"""
Server URL Configuration
"""
from django.conf.urls import url
from django.contrib import admin
from FreeRoomFinderServer import views

urlpatterns = [
    url(r'refresh', views.refresh),
    url(r'db', views.db),
    url(r"api", views.api),
    url(r"", views.main),
]
