"""Module for all view."""

from django.db import models
from rest_framework import viewsets, status
from rest_framework.permissions import BasePermission as RestFrameworkBasePermission
from rest_framework.response import Response
from django.middleware import csrf
from django.http import JsonResponse
from django.contrib.auth import login, logout
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from .serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    UserSerializer,
    FacultySerializer,
    GroupSerializer,
    LessonSerializer,
    StudentSerializer,
    SubjectSerializer,
    TeacherSerializer
)
from rest_framework import permissions
from .validations import custom_validation, validate_email, validate_password
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import Faculty, Group, Lesson, Student, Subject, Teacher, AppUser


class UserStudentDetailView(APIView):
    """View for getting student details by ID."""

    def get(self, request, user_id=None):
        """
        Retrieve and return detailed information about a student identified by their unique ID.

        Parameters:
            request (HttpRequest): The HTTP request object.
            user_id (int, optional): The ID of the student whose details are to be retrieved. Defaults to None.

        Returns:
            Response: An HTTP response containing the serialized student details.
        """
        try:
            user = AppUser.objects.get(pk=user_id)
            student = Student.objects.get(user=user)
            serializer = StudentSerializer(student, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except AppUser.DoesNotExist:
            return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)
        except Student.DoesNotExist:
            return Response({"error": "Студент не найден"}, status=status.HTTP_404_NOT_FOUND)


class UserTeacherDetailView(APIView):
    """View for getting teacher details by ID."""

    def get(self, request, user_id=None):
        """
        Retrieve and return detailed information about a teacher identified by their unique ID.

        Parameters:
            request (HttpRequest): The HTTP request object.
            user_id (int, optional): The ID of the teacher whose details are to be retrieved. Defaults to None.

        Returns:
            Response: An HTTP response containing the serialized teacher details.
        """
        try:
            user = AppUser.objects.get(pk=user_id)
            teacher = Teacher.objects.get(user=user)
            serializer = TeacherSerializer(teacher, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except AppUser.DoesNotExist:
            return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)
        except Teacher.DoesNotExist:
            return Response({"error": "Учитель не найден"}, status=status.HTTP_404_NOT_FOUND)


class UserRegister(APIView):
    """
    Handles user registration requests.

    Attributes:
        permission_classes (tuple): A tuple defining the permission classes for this view.

    Methods:
        post(self, request): Processes POST requests to register a new user.
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        """
        Register a new user with the provided data.

        Parameters:
            request (HttpRequest): The HTTP request object containing the registration data.

        Returns:
            Response: An HTTP response containing the serialized user details upon successful registration.
        """
        clean_data = custom_validation(request.data)
        serializer = UserRegisterSerializer(data=clean_data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.create(clean_data)
            if user:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
    """
    Handles user login requests.

    Attributes:
        permission_classes (tuple): A tuple defining the permission classes for this view.
        authentication_classes (tuple): A tuple defining the authentication classes for this view.

    Methods:
        post(self, request): Processes POST requests to log in a user.
    """

    permission_classes = (permissions.AllowAny,)
    authentication_classes = (SessionAuthentication,)

    def post(self, request):
        """
        Authenticate a user with the provided credentials.

        Parameters:
            request (HttpRequest): The HTTP request object containing the login data.

        Returns:
            Response: An HTTP response containing the serialized user details upon successful login.
        """
        user_data = request.data
        assert validate_email(user_data)
        assert validate_password(user_data)
        serializer = UserLoginSerializer(data=user_data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.check_user(user_data)
            if not user:
                return Response({'error': 'такого пользователя нет!'}, status=status.HTTP_404_NOT_FOUND)
            login(request, user)
            return Response(serializer.data, status=status.HTTP_200_OK)


class UserLogout(APIView):
    """
    Logs out the currently authenticated user.

    Attributes:
        permission_classes (tuple): A tuple defining the permission classes for this view.
        authentication_classes (tuple): indicating that no authentication is required for this operation.

    Methods:
        post(self, request): Handles POST requests to log out the user.
    """

    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request):
        """
        Clear the user's session, logging them out.

        Parameters:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: An HTTP response indicating success (status code 200).
        """
        logout(request)
        return Response(status=status.HTTP_200_OK)


class UserView(APIView):
    """
    View for retrieving information about the currently authenticated user.

    This view uses the UserSerializer to serialize the user's data and returns it in the response.
    Requires the user to be authenticated due to the IsAuthenticated permission class.

    Attributes:
        permission_classes (tuple): A tuple defining the permission classes for this view.
        authentication_classes (tuple): A tuple defining the authentication classes for this view.
    """

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def get(self, request):
        """
        Retrieve and return the serialized data of the currently authenticated user.

        Parameters:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: An HTTP response containing the serialized user data.
        """
        serializer = UserSerializer(request.user)
        return Response({'user': serializer.data}, status=status.HTTP_200_OK)


class CsrfTokenView(APIView):
    """
    View for obtaining CSRF token for the current request.

    This view is accessible to any user, including unauthenticated ones, due to the AllowAny permission class.
    It retrieves the CSRF token associated with the current request and returns it in the response.

    Attributes:
        permission_classes (tuple): A tuple defining the permission classes for this view.
    """

    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        """
        Obtain and return the CSRF token for the current request.

        Parameters:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: An HTTP response containing the CSRF token.
        """
        csrf_token = csrf.get_token(request)

        return Response(
            data={'csrf_token': csrf_token},
            status=status.HTTP_200_OK
        )


@ensure_csrf_cookie
def session_view(request):
    """
    Check if the user is authenticated and return relevant information.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response indicating whether the user is authenticated.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'isAuthenticated': False})

    return JsonResponse({'isAuthenticated': True, 'username': request.user.username, 'user_id': request.user.id})


class Permission(RestFrameworkBasePermission):
    """
    A custom permission class that restricts access based on HTTP method safety.

    Attributes:
        safe_methods (tuple): tuple of HTTP methods considered safe.
        unsafe_methods (tuple): tuple of HTTP methods considered unsafe.
    """

    safe_methods = ('GET', 'HEAD', 'OPTIONS', 'PATCH')
    unsafe_methods = ('POST', 'PUT', 'DELETE')

    def has_permission(self, request, extra_param):
        """
        Determine if the request method is allowed based on the defined safe and unsafe methods.

        Parameters:
            request: incoming HTTP request.
            extra_param: unused parameter to match the method signature.

        Returns:
            bool: True if the request method is either safe or unsafe, False otherwise.
        """
        if request.method in self.safe_methods:
            return True
        return request.user.is_superuser or request.user.is_staff


def query_from_request(request, serializer=None):
    """
    Extract query parameters from the request and filter them based on the fields of the provided serializer.

    If a serializer is passed, it constructs a dictionary of query parameters from the request's GET data,
    filtering only those fields present in the serializer's Meta.fields list. Otherwise, it simply returns
    the raw GET data from the request.

    Parameters:
        request: HTTP request object containing the query parameters.
        serializer: optional serializer instance.

    Returns:
        dict: dictionary of filtered query parameters if a serializer was provided.
    """
    if serializer:
        query = {}
        for attr in serializer.Meta.fields:
            attr_value = request.GET.get(attr, '')
            if attr_value:
                query[attr] = attr_value
        return query
    return request.GET


def create_viewset(cls_model: models.Model, serializer, order_field: str):
    """
    Create and return a ViewSet class for the specified model, using the provided serializer and sorting field.

    Parameters:
        cls_model (models.Model): Django model class for which the ViewSet is created.
        serializer: serializer to be used for serializing the model data.
        order_field (str): name of the field by which the data will be sorted in the queryset.

    Returns:
    - Type[class_name]: ViewSet associated with the cls_model model, using the specified serializer and sorting.
    """
    class_name = "{0}ViewSet".format(cls_model.__name__)
    doc = "API endpoint that allows users to be viewed or edited for {0}".format(cls_model.__name__)
    return type(class_name, (viewsets.ModelViewSet,), {
        "__doc__": doc,
        "serializer_class": serializer,
        "queryset": cls_model.objects.all().order_by(order_field),
        "permission_classes": [Permission],
        "get_queryset": lambda self, *args, **kwargs: (
            cls_model.objects.filter(
                **query_from_request(self.request, serializer),
            ).order_by(order_field)
    )})


LessonViewSet = create_viewset(Lesson, LessonSerializer, 'subject')
SubjectViewSet = create_viewset(Subject, SubjectSerializer, 'title')
StudentViewSet = create_viewset(Student, StudentSerializer, 'full_name')
TeacherViewSet = create_viewset(Teacher, TeacherSerializer, 'full_name')
GroupViewSet = create_viewset(Group, GroupSerializer, 'title')
FacultyViewSet = create_viewset(Faculty, FacultySerializer, 'title')
