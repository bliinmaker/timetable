"""timatable_app URL Configuration."""
from django.urls import include, path
from rest_framework import routers

from . import views


urlpatterns = [
    path('', views.custom_main, name='homepage'),
]
