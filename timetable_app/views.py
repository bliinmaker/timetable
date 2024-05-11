from typing import Any

from django.contrib.auth import decorators as auth_decorators
from django.core.paginator import Paginator
from django.db import models
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.generic import ListView
from rest_framework import authentication, permissions
from rest_framework import status as status_codes
from rest_framework import viewsets
from rest_framework.parsers import JSONParser
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from . import config
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


def query_from_request(cls_serializer, request) -> dict:
    """Gets query from request according to fields of the serializer class. 
    Returns empty dict if didn't find any."""
    query = {}
    for field in cls_serializer.Meta.fields:
        value = request.GET.get(field, '')
        if value:
            query[field] = value
    return query


def create_viewset(cls_model, serializer, order_field):
    class CustomViewSet(ModelViewSet):
        queryset = cls_model.objects.all()
        serializer_class = serializer
        permission_classes = [Permission]

        def get_queryset(self):
            query = query_from_request(serializer, self.request)
            queryset = cls_model.objects.filter(
                **query) if query else cls_model.objects.all()
            return queryset.order_by(order_field)

        def delete(self, request):
            def response_from_objects(num):
                if not num:
                    content = f'DELETE for model {
                        cls_model.__name__}: query did not match any objects'
                    return Response(content, status=status_codes.HTTP_404_NOT_FOUND)
                status = status_codes.HTTP_204_NO_CONTENT if num == 1 else status_codes.HTTP_200_OK
                return Response(f'DELETED {num} instances of {cls_model.__name__}', status=status)

            query = query_from_request(serializer, request)
            if query:
                objects = cls_model.objects.all().filter(**query)
                num_objects = len(objects)
                try:
                    objects.delete()
                except Exception as error:
                    return Response(error, status=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)
                return response_from_objects(num_objects)
            return Response('DELETE has got no query', status=status_codes.HTTP_400_BAD_REQUEST)

        def put(self, request):
            """gets id from query and updates instance with this ID, creates new if doesnt find any."""
            def serialize(target):
                content = JSONParser().parse(request)
                model_name = cls_model.__name__
                if target:
                    serialized = serializer(target, data=content, partial=True)
                    status = status_codes.HTTP_200_OK
                    body = f'PUT has updated {model_name} instance'
                else:
                    serialized = serializer(data=content, partial=True)
                    status = status_codes.HTTP_201_CREATED
                    body = f'PUT has created new {model_name} instance'
                if not serialized.is_valid():
                    return (
                        f'PUT could not serialize query {
                            query} into {model_name}',
                        status_codes.HTTP_400_BAD_REQUEST
                    )
                try:
                    model_obj = serialized.save()
                except Exception as error:
                    return error, status_codes.HTTP_500_INTERNAL_SERVER_ERROR
                body = f'{body} with id={model_obj.id}'
                return body, status

            query = query_from_request(serializer, request)
            target_id = query.get('id', '')
            if not target_id:
                return Response('PUT has got no id', status=status_codes.HTTP_400_BAD_REQUEST)
            try:
                target_object = cls_model.objects.get(id=target_id)
            except Exception:
                target_object = None
            content, status = serialize(target_object)
            return Response(content, status=status)

    return CustomViewSet


LessonViewSet = create_viewset(Lesson, LessonSerializer, 'subject')
SubjectViewSet = create_viewset(Subject, SubjectSerializer, 'title')
StudentViewSet = create_viewset(Student, StudentSerializer, 'full_name')
TeacherViewSet = create_viewset(Teacher, TeacherSerializer, 'full_name')
GroupViewSet = create_viewset(Group, GroupSerializer, 'title')
FacultyViewSet = create_viewset(Faculty, FacultySerializer, 'title')
