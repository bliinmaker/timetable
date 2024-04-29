from datetime import datetime, timezone
from uuid import uuid4

from django.conf.global_settings import AUTH_USER_MODEL
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from . import config


def get_datetime():
    return datetime.now(timezone.utc)


def check_created(dt: datetime) -> None:
    if dt > get_datetime():
        raise ValidationError(
            _('Datetime is bigger than current datetime!'),
            params={'created': dt}
        )


def check_modified(dt: datetime) -> None:
    if dt > get_datetime():
        raise ValidationError(
            _('Datetime is bigger than current datetime!'),
            params={'modified': dt}
        )


class UUIDMixin(models.Model):
    id = models.UUIDField(
        primary_key=True, blank=True, editable=False, default=uuid4
    )

    class Meta:
        abstract = True


class CreatedMixin(models.Model):
    created = models.DateTimeField(
        _('created'),
        null=True, blank=True,
        default=get_datetime,
        validators=[
            check_created,
        ]
    )

    class Meta:
        abstract = True


class ModifiedMixin(models.Model):
    modified = models.DateTimeField(
        _('modified'),
        null=True, blank=True,
        default=get_datetime,
        validators=[
            check_modified,
        ]
    )

    class Meta:
        abstract = True


class Faculty(UUIDMixin):
    title = models.CharField(_('faculty'), max_length=config.CHARS_DEFAULT)
    code_faculty = models.CharField(_('code faculty'), max_length=config.CHARS_DEFAULT)
    description = models.TextField(_('description'), blank=True, null=True)

    def __str__(self):
        return f'{self.title} ({self.code_faculty})'

    class Meta:
        ordering = ['title']
        verbose_name = _('faculty')
        verbose_name_plural = _('faculties')
        db_table = 'faculty'


class Group(UUIDMixin):
    title = models.CharField(_('group'), max_length=config.CHARS_DEFAULT)
    faculty = models.ForeignKey(Faculty, verbose_name=_(
        'faculty'), on_delete=models.CASCADE)
    lessons = models.ManyToManyField(
        'Lesson', verbose_name=_('lessons'), through='LessonGroup')
    subjects = models.ManyToManyField(
        'Subject', verbose_name=_('subjects'), through='SubjectGroup')

    def clean(self):
        for lesson in self.lessons.all():
            if lesson.subject not in self.subjects.all():
                raise ValidationError(
                    f"The lesson {lesson} does not match the group's subjects."
                )

    def __str__(self):
        return f'{self.title} ({self.faculty})'

    class Meta:
        ordering = ['title']
        verbose_name = _('group')
        verbose_name_plural = _('groups')
        db_table = 'class'


class Subject(UUIDMixin):
    title = models.CharField(_('title'), max_length=config.CHARS_DEFAULT)
    groups = models.ManyToManyField(
        Group, verbose_name=_('groups'), through='SubjectGroup')
    teachers = models.ManyToManyField(
        'Teacher', verbose_name=_('teachers'), through='SubjectTeacher')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name = _('subject')
        verbose_name_plural = _('subjects')
        db_table = 'subject'


class Teacher(UUIDMixin):
    user = models.OneToOneField(
        AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    full_name = models.CharField(
        _('full name'), max_length=config.CHARS_DEFAULT)
    subjects = models.ManyToManyField(
        Subject, verbose_name=_('subjects'), through='SubjectTeacher')

    def __str__(self):
        return self.full_name

    class Meta:
        ordering = ['full_name']
        verbose_name = _('teacher')
        verbose_name_plural = _('teachers')
        db_table = 'teacher'


class Lesson(UUIDMixin):
    start_time = models.DateTimeField(_('start time'), default=get_datetime)
    subject = models.ForeignKey(Subject, verbose_name=_(
        'subject'), on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, verbose_name=_(
        'teacher'), on_delete=models.CASCADE)
    groups = models.ManyToManyField(
        Group, verbose_name=_('groups'), through='LessonGroup')

    def clean(self):
        teachers = Teacher.objects.filter(subject__id=self.subject_id)
        if self.teacher not in teachers:
            raise ValidationError(
                f"The teacher {self.teacher} is not assigned to teach the subject {self.subject}"
            )
        for group in self.groups.all():
            if self.subject not in group.subjects.all():
                raise ValidationError(
                    f"The subject {self.subject} is not included in the group {group}"
                )

    def __str__(self):
        return f'{self.day} {self.precise_time}, {self.subject}'

    class Meta:
        ordering = ['start_time']
        verbose_name = _('lesson')
        verbose_name_plural = _('lessons')
        db_table = 'lesson'


class Student(UUIDMixin, CreatedMixin):
    user = models.OneToOneField(
        AUTH_USER_MODEL,  null=True, on_delete=models.CASCADE)
    full_name = models.CharField(verbose_name=_(
        'full name'), max_length=config.CHARS_DEFAULT)
    group = models.ForeignKey(Group, verbose_name=_(
        'group'), on_delete=models.CASCADE, db_column='class_id', blank=True, null=True)

    def __str__(self):
        return {self.full_name, self.group.title}

    class Meta:
        ordering = ['full_name']
        verbose_name = _('student')
        verbose_name_plural = _('students')
        db_table = 'student'


class LessonGroup(UUIDMixin):
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, db_column='class_id')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)

    class Meta:
        db_table = 'lesson_group'


class SubjectGroup(UUIDMixin):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, db_column='class_id')

    class Meta:
        db_table = 'subject__group'
        unique_together = (('subject', 'group'),)


class SubjectTeacher(UUIDMixin):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    class Meta:
        db_table = 'subject_teacher'
        unique_together = (('subject', 'teacher'),)
