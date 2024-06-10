from rest_framework import serializers
from .models import Faculty, Group, Lesson, Student, Subject, Teacher
from django.contrib.auth import get_user_model, authenticate


UserModel = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = '__all__'

    def create(self, clean_data):
        user_obj = UserModel.objects.create_user(email=clean_data['email'], password=clean_data['password'])
        user_obj.username = clean_data['username']
        user_obj.save()
        return user_obj


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def check_user(self, clean_data):
        user = authenticate(username=clean_data['email'], password=clean_data['password'])
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('id', 'email', 'username')


class FacultySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Faculty
        fields = [
            'id', 'title', 'code_faculty', 'description',
        ]


class SubjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Subject
        fields = [
            'id', 'title',
        ]


class TeacherSerializer(serializers.HyperlinkedModelSerializer):
    subjects = SubjectSerializer(many=True, read_only=True)

    class Meta:
        model = Teacher
        fields = [
            'id', 'full_name', 'subjects',
        ]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    faculty = FacultySerializer(many=False, read_only=True)
    subjects = SubjectSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = [
            'id', 'title', 'faculty', 'subjects',
        ]


class StudentSerializer(serializers.HyperlinkedModelSerializer):
    group = GroupSerializer(many=False, read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'full_name', 'group',
        ]


class LessonSerializer(serializers.HyperlinkedModelSerializer):
    teacher = TeacherSerializer(many=False, read_only=True)
    group = GroupSerializer(many=False, read_only=True)
    subject = SubjectSerializer(many=False, read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'duration', 'start_time', 'end_time', 'subject', 'teacher', 'group',]
