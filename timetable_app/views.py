from django.db import models
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework import viewsets, status
from rest_framework.permissions import BasePermission
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.contrib.auth import get_user_model, login, logout
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer
from rest_framework import permissions, status
from .validations import custom_validation, validate_email, validate_password
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import Faculty, Group, Lesson, Student, Subject, Teacher, AppUser
from .serializers import (FacultySerializer, GroupSerializer, LessonSerializer,
                          StudentSerializer, SubjectSerializer,
                          TeacherSerializer)


class UserStudentDetailView(APIView):
    """
    Представление для получения данных студента по ID пользователя.
    """

    def get(self, request, id=None):
        try:
            user = AppUser.objects.get(pk=id)
            student = Student.objects.get(user=user)
            serializer = StudentSerializer(student, context={'request': request})
            return Response(serializer.data)
        except AppUser.DoesNotExist:
            return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)
        except Student.DoesNotExist:
            return Response({"error": "Студент не найден"}, status=status.HTTP_404_NOT_FOUND)


class UserTeacherDetailView(APIView):
    """
    Представление для получения данных цчителя по ID пользователя.
    """

    def get(self, request, id=None):
        try:
            user = AppUser.objects.get(pk=id)
            teacher = Teacher.objects.get(user=user)
            serializer = TeacherSerializer(teacher, context={'request': request})
            return Response(serializer.data)
        except AppUser.DoesNotExist:
            return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)
        except Teacher.DoesNotExist:
            return Response({"error": "Учитель не найден"}, status=status.HTTP_404_NOT_FOUND)


class UserRegister(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        clean_data = custom_validation(request.data)
        serializer = UserRegisterSerializer(data=clean_data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.create(clean_data)
            if user:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = (SessionAuthentication,)

    def post(self, request):
        data = request.data
        assert validate_email(data)
        assert validate_password(data)
        serializer = UserLoginSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.check_user(data)
            if not user:
                return Response({'error': 'такого пользователя нет!'}, status=status.HTTP_404_NOT_FOUND)
            login(request, user)
            return Response(serializer.data, status=status.HTTP_200_OK)


class UserLogout(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)


class UserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    ##

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({'user': serializer.data}, status=status.HTTP_200_OK)


@ensure_csrf_cookie
def session_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'isAuthenticated': False})

    return JsonResponse({'isAuthenticated': True, 'username': request.user.username, 'user_id': request.user.id})


# REST, ModelViewSet
class Permission(BasePermission):
    safe_methods = ('GET', 'HEAD', 'OPTIONS', 'PATCH')
    unsafe_methods = ('POST', 'PUT', 'DELETE')

    def has_permission(self, request, _):
        if request.method in self.safe_methods:
            return True
        elif request.method in self.unsafe_methods:
            return True
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
    doc = f"API endpoint that allows users to be viewed or edited for {cls_model.__name__}"
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
