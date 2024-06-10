from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin

from .models import (Faculty, Group, Lesson, Student, Subject, SubjectGroup,
                     SubjectTeacher, Teacher, AppUser)


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


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = AppUser
        fields = ('email',)

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    list_display = ("email",)
    ordering = ("email",)
    readonly_fields = ('date_joined',)

    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'password', 'is_superuser', 'is_staff', 'is_active')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password', 'is_superuser', 'is_staff', 'is_active')
        }),
    )

    filter_horizontal = ()


admin.site.register(AppUser, CustomUserAdmin)
