from rest_framework import serializers

from .models import Faculty, Group, Lesson, Student, Subject, Teacher


class SubjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Subject
        fields = [
            'id', 'title',
            'created', 'modified',
        ]


class StudentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Student
        fields = [
            'id', 'full_name', 'group',
            'created', 'modified',
        ]


class TeacherSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Teacher
        fields = [
            'id', 'full_name',
            'created', 'modified',
        ]


class LessonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            'id', 'duration', 'start_time', 'end_time',
            'subject', 'teacher', 'group',
            'created', 'modified',
        ]


class FacultySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Faculty
        fields = [
            'id', 'title', 'code_faculty', 'description',
            'created', 'modified',
        ]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = [
            'id', 'title', 'faculty',
            'created', 'modified',
        ]
