"""
Serializers for the timetable application.

This module defines serializers for various models used in the timetable application.
"""

from rest_framework import serializers
from .models import Faculty, Group, Lesson, Student, Subject, Teacher
from django.contrib.auth import get_user_model, authenticate


UserModel = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new user.

    Handles the registration of new users by validating the provided data and creating a new user instance.

    Attributes:
        Meta.model: Specifies the model to serialize, which is the UserModel.
        Meta.fields: Defines fields to be included in serialization, set to '__all__' to include all fields.

    Methods:
        create(clean_data): Creates and saves a new user instance using validated data.
            Args:
                clean_data (dict): Validated data to create a new user.

            Returns:
                UserModel: The newly created user instance.
    """

    class Meta:
        model = UserModel
        fields = '__all__'

    def create(self, clean_data):
        """
        Create a new user instance.

        Args:
            clean_data (dict): Validated data for creating a new user.

        Returns:
            UserModel: The newly created user instance.
        """
        user_obj = UserModel.objects.create_user(email=clean_data['email'], password=clean_data['password'])
        user_obj.username = clean_data['username']
        user_obj.save()
        return user_obj


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for logging in users.

    Validates user credentials and authenticates the user.

    Attributes:
        email (EmailField): Email field for authentication.
        password (CharField): Password field for authentication.

    Methods:
        check_user(clean_data): Authenticates the user with the provided credentials.
            Args:
                clean_data (dict): Data containing 'email' and 'password'.

            Returns:
                UserModel: The authenticated user instance or None if authentication fails.
    """

    email = serializers.EmailField()
    password = serializers.CharField()

    def check_user(self, clean_data):
        """
        Authenticate the user.

        Validates the provided credentials and returns the authenticated user instance if successful, otherwise None.

        Args:
            clean_data (dict): A dictionary containing 'email' and 'password' keys with validated credentials.

        Returns:
            UserModel: The authenticated user instance or None if authentication fails.
        """
        return authenticate(username=clean_data['email'], password=clean_data['password'])


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user instances.

    Provides serialization for user instances, including id, email, and username.

    Attributes:
        Meta.model: Specifies the model to serialize, which is the UserModel.
        Meta.fields: Defines fields to be included in serialization, specifically 'id', 'email', and 'username'.
    """

    class Meta:
        model = UserModel
        fields = ('id', 'email', 'username')


class FacultySerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for faculty instances.

    Provides serialization for faculty instances, including id, title, code_faculty, and description.

    Attributes:
        Meta.model: Specifies the model to serialize, which is the Faculty model.
        Meta.fields: Defines fields to be included in serialization.
    """

    class Meta:
        model = Faculty
        fields = [
            'id', 'title', 'code_faculty', 'description',
        ]


class SubjectSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for subject instances.

    Provides serialization for subject instances, including id and title.

    Attributes:
        Meta.model: Specifies the model to serialize, which is the Subject model.
        Meta.fields: Defines fields to be included in serialization.
    """

    class Meta:
        model = Subject
        fields = [
            'id', 'title',
        ]


class TeacherSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for teacher instances.

    Provides serialization for teacher instances, including id, full_name, and subjects.

    Attributes:
        subjects (SubjectSerializer): Nested serializer for subjects associated with the teacher.
        Meta.model: Specifies the model to serialize, which is the Teacher model.
        Meta.fields: Defines fields to be included in serialization.
    """

    subjects = SubjectSerializer(many=True, read_only=True)

    class Meta:
        model = Teacher
        fields = [
            'id', 'full_name', 'subjects',
        ]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for group instances.

    Provides serialization for group instances, including id, title, faculty, and subjects.

    Attributes:
        faculty (FacultySerializer): Nested serializer for the faculty associated with the group.
        subjects (SubjectSerializer): Nested serializer for subjects associated with the group.
        Meta.model: Specifies the model to serialize, which is the Group model.
        Meta.fields: Defines fields to be included in serialization.
    """

    faculty = FacultySerializer(many=False, read_only=True)
    subjects = SubjectSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = [
            'id', 'title', 'faculty', 'subjects',
        ]


class StudentSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for student instances.

    Provides serialization for student instances, including id, full_name, and group.

    Attributes:
        group (GroupSerializer): Nested serializer for the group associated with the student.
        Meta.model: Specifies the model to serialize, which is the Student model.
        Meta.fields: Defines fields to be included in serialization.
    """

    group = GroupSerializer(many=False, read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'full_name', 'group',
        ]


class LessonSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for lesson instances.

    Provides serialization for lesson instances.

    Attributes:
        teacher (TeacherSerializer): Nested serializer for the teacher associated with the lesson.
        group (GroupSerializer): Nested serializer for the group associated with the lesson.
        subject (SubjectSerializer): Nested serializer for the subject of the lesson.
        Meta.model: Specifies the model to serialize, which is the Lesson model.
        Meta.fields: Defines fields to be included in serialization.
    """

    teacher = TeacherSerializer(many=False, read_only=True)
    group = GroupSerializer(many=False, read_only=True)
    subject = SubjectSerializer(many=False, read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'lesson_slot', 'date', 'start_time', 'end_time', 'subject', 'teacher', 'group', ]
