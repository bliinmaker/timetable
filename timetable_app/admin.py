from django.contrib import admin

from .models import (Faculty, Group, Lesson, Student, Subject, SubjectGroup,
                     SubjectTeacher, Teacher)


class SubjectGroupInline(admin.TabularInline):
    model = SubjectGroup
    extra = 1


class SubjectTeacherInline(admin.TabularInline):
    model = SubjectTeacher
    extra = 1


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    model = Faculty
    list_filter = (
        'title',
    )


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    model = Group
    inlines = (SubjectGroupInline,)
    list_filter = (
        'faculty',
    )


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    model = Subject
    inlines = (SubjectGroupInline, SubjectTeacherInline)
    list_filter = (
        'group',
        'teacher',
    )


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    model = Teacher
    inlines = (SubjectTeacherInline,)
    list_filter = (
        'subject',
    )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    model = Lesson
    list_filter = (
        'start_time',
        'subject',
        'teacher',
    )


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    model = Student
    list_filter = (
        'group',
    )
