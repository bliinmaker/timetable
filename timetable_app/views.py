from typing import Any

from django.contrib.auth import decorators as auth_decorators
from django.core.paginator import Paginator
from django.db import models
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.generic import ListView
from rest_framework import permissions, viewsets

from . import config
from .models import Faculty, Group, Lesson, Student, Teacher


def custom_main(request):
    context = {
        'greeting': _("Welcome to our Localization Project!"),
        'large_number': 12345.67,
        'current_date': timezone.now()
    }
    return render(request, 'index.html', context)
