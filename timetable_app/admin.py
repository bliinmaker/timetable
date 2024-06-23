"""
Defines administrative interfaces for various models in the timetable application.

This module contains definitions for Django admin interfaces.

Classes:
    SubjectGroupInline: Inline admin interface for SubjectGroup model.
    SubjectTeacherInline: Inline admin interface for SubjectTeacher model.
    FacultyAdmin: Admin configuration for the Faculty model, enabling filtering by title.
    GroupAdmin: Admin configuration for the Group model.
    SubjectAdmin: Admin configuration for the Subject model.
    TeacherAdmin: Admin configuration for the Teacher model.
    LessonAdmin: Admin configuration for the Lesson model, enabling filtering by start time, subject, and teacher.
    StudentAdmin: Admin configuration for the Student model, enabling filtering by group.
    UserCreationForm: Custom form for user creation, allowing setting password during save operation.
    CustomUserAdmin: Customized UserAdmin class for AppUser model, specifying fields and fieldsets.
"""

from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin

from .models import (Faculty, Group, Lesson, Student, Subject, SubjectGroup, SubjectTeacher, Teacher, AppUser)


class SubjectGroupInline(admin.TabularInline):
    """
    Inline admin interface for SubjectGroup model.

    Allows editing of SubjectGroup instances within another model's admin interface.
    """

    model = SubjectGroup
    extra = 1


class SubjectTeacherInline(admin.TabularInline):
    """
    Inline admin interface for SubjectTeacher model.

    Allows editing of SubjectTeacher instances within another model's admin interface.
    """

    model = SubjectTeacher
    extra = 1


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Faculty model.

    Defines custom admin options for the Faculty model, including filtering by title.
    """

    model = Faculty
    list_filter = (
        'title',
    )


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Group model.

    Defines custom admin options for the Group model.
    """

    model = Group
    inlines = (SubjectGroupInline,)
    list_filter = (
        'faculty',
    )


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Subject model.

    Defines custom admin options for the Subject model.
    """

    model = Subject
    inlines = (SubjectGroupInline, SubjectTeacherInline)
    list_filter = (
        'group',
        'teacher',
    )


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Teacher model.

    Defines custom admin options for the Teacher model.
    """

    model = Teacher
    inlines = (SubjectTeacherInline,)
    list_filter = (
        'subject',
    )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Lesson model.

    Enables filtering by start_time, subject, and teacher.
    """

    model = Lesson
    list_filter = (
        'start_time',
        'subject',
        'teacher',
    )


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Student model.

    Enables filtering by group.
    """

    model = Student
    list_filter = (
        'group',
    )


class UserCreationForm(forms.ModelForm):
    """
    Custom form for creating new users.

    Extends ModelForm to customize user creation in admin interface, allowing password setting during save operation.

    Attributes:
        Meta.model: Specifies AppUser model for form.
        Meta.fields: Defines email field for form.

    Methods:
        save(commit=True): Overrides save method to set password for the user.
    """

    class Meta:
        model = AppUser
        fields = ('email',)

    def save(self, commit=True):
        """
        Save the user instance with set password.

        Args:
            commit (bool, optional): Whether to save the user instance immediately. Defaults to True.

        Returns:
            AppUser: The created AppUser instance.
        """
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class CustomUserAdmin(UserAdmin):
    """
    Customized UserAdmin class for AppUser model.

    Attributes:
        add_form: Specifies UserCreationForm for adding new users.
        list_display: Defines fields to display in the list view.
        ordering: Specifies default ordering for the list view.
        readonly_fields: Defines fields to be displayed as read-only in the admin interface.
        fieldsets: Customizes fields displayed in the edit form.
        add_fieldsets: Customizes fields displayed in the add form.
        filter_horizontal: Specifies fields to use horizontal filter interface.
    """

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
