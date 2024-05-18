from django.db import models
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework import viewsets
from rest_framework.permissions import BasePermission

from .models import Faculty, Group, Lesson, Student, Subject, Teacher
from .serializers import (FacultySerializer, GroupSerializer, LessonSerializer,
                          StudentSerializer, SubjectSerializer,
                          TeacherSerializer)


def custom_main(request):
    context = {
        'greeting': _("Welcome to our Localization Project!"),
        'large_number': 12345.67,
        'current_date': timezone.now()
    }
    return render(request, 'index.html', context)


# REST, ModelViewSet
class Permission(BasePermission):
    safe_methods = ('GET', 'HEAD', 'OPTIONS', 'PATCH')
    unsafe_methods = ('POST', 'PUT', 'DELETE')

    def has_permission(self, request, _):
        if request.method in self.safe_methods:
            return bool(request.user and request.user.is_authenticated)
        elif request.method in self.unsafe_methods:
            return bool(request.user and request.user.is_superuser)
        return False


def query_from_request(request, serializer=None):
    if serializer:
        query = {}
        for attr in serializer.Meta.fields:
            attr_value = request.GET.get(attr, '')
            if attr_value:
                query[attr] = attr_value
        return query
    return request.GET


def create_viewset(cls_model: models.Model, serializer, order_field: str):
    class_name = f"{cls_model.__name__}ViewSet"
    doc = f"API endpoint that allows users to be viewed or edited for {
        cls_model.__name__}"
    CustomViewSet = type(class_name, (viewsets.ModelViewSet,), {
        "__doc__": doc,
        "serializer_class": serializer,
        "queryset": cls_model.objects.all().order_by(order_field),
        "permission_classes": [Permission],
        "get_queryset": lambda self, *args, **kwargs: cls_model.objects.filter(**query_from_request(self.request, serializer)).order_by(order_field)}
    )

    return CustomViewSet


LessonViewSet = create_viewset(Lesson, LessonSerializer, 'subject')
SubjectViewSet = create_viewset(Subject, SubjectSerializer, 'title')
StudentViewSet = create_viewset(Student, StudentSerializer, 'full_name')
TeacherViewSet = create_viewset(Teacher, TeacherSerializer, 'full_name')
GroupViewSet = create_viewset(Group, GroupSerializer, 'title')
FacultyViewSet = create_viewset(Faculty, FacultySerializer, 'title')
