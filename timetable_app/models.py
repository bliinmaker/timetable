from datetime import datetime, timedelta
from uuid import uuid4

from timetable.settings import AUTH_USER_MODEL
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from . import config


def get_datetime():
    return timezone.now()


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


class AppUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('An email is required.')
        if not password:
            raise ValueError('A password is required.')
        email = self.normalize_email(email)
        user = self.model(email=email)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, password=None):
        if not email:
            raise ValueError('An email is required.')
        if not password:
            raise ValueError('A password is required.')
        user = self.create_user(email, password)
        user.username = username
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class AppUser(AbstractBaseUser, PermissionsMixin, UUIDMixin):
    email = models.EmailField(max_length=50, unique=True)
    username = models.CharField(max_length=50)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = AppUserManager()

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['username']
        verbose_name = _('app_user')
        verbose_name_plural = _('app_users')
        db_table = 'app_user'


class Faculty(UUIDMixin, CreatedMixin, ModifiedMixin):
    title = models.CharField(_('faculty'), max_length=config.CHARS_DEFAULT)
    code_faculty = models.CharField(
        _('code faculty'), max_length=config.CHARS_DEFAULT)
    description = models.TextField(_('description'), blank=True, null=True)

    def __str__(self):
        return f'{self.title} ({self.code_faculty})'

    class Meta:
        ordering = ['title']
        verbose_name = _('faculty')
        verbose_name_plural = _('faculties')
        db_table = 'faculty'


class Group(UUIDMixin, CreatedMixin, ModifiedMixin):
    title = models.CharField(_('group'), max_length=config.CHARS_DEFAULT)
    faculty = models.ForeignKey(Faculty, verbose_name=_(
        'faculty'), on_delete=models.CASCADE)
    subjects = models.ManyToManyField(
        'Subject', verbose_name=_('subjects'), through='SubjectGroup')

    def __str__(self):
        return f'{self.title} ({self.faculty})'

    class Meta:
        ordering = ['title']
        verbose_name = _('group')
        verbose_name_plural = _('groups')
        db_table = 'group'


class Subject(UUIDMixin, CreatedMixin, ModifiedMixin):
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


class Teacher(UUIDMixin, CreatedMixin, ModifiedMixin):
    user = models.OneToOneField(
        AppUser, null=True, on_delete=models.CASCADE)
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


class Lesson(UUIDMixin, CreatedMixin, ModifiedMixin):
    duration = models.IntegerField(
        _('duration'), default=90, blank=False, null=True)
    start_time = models.DateTimeField(
        _('start time'), default=get_datetime, blank=False, null=True)
    end_time = models.DateTimeField(
        _('end time'), null=True, blank=True, editable=False)
    subject = models.ForeignKey(Subject, verbose_name=_(
        'subject'), on_delete=models.CASCADE, blank=False, null=True)
    teacher = models.ForeignKey(Teacher, verbose_name=_(
        'teacher'), on_delete=models.CASCADE, blank=False, null=True)
    group = models.ForeignKey(Group, verbose_name=_(
        'group'), on_delete=models.CASCADE, blank=False, null=True)

    def validate_lesson(self) -> bool:
        self.end_time = self.start_time + timedelta(minutes=self.duration)
        try:
            teachers_lessons = Lesson.objects.filter(
                teacher__id=self.teacher.id)
        except ObjectDoesNotExist:
            return False
        if self.start_time is None or self.end_time is None:
            return False
        for lesson in teachers_lessons:
            if lesson.start_time is not None and lesson.end_time is not None:
                if lesson.start_time <= self.start_time <= lesson.end_time:
                    return False
                if lesson.start_time <= self.end_time <= lesson.end_time:
                    return False
        try:
            group_lessons = Lesson.objects.filter(group__id=self.group.id)
        except ObjectDoesNotExist:
            return False
        for lesson in group_lessons:
            if lesson.start_time is not None and lesson.end_time is not None:
                if lesson.start_time <= self.start_time <= lesson.end_time:
                    return False
                if lesson.start_time <= self.end_time <= lesson.end_time:
                    return False
        return True

    def clean(self):
        super().clean()
        teachers = Teacher.objects.filter(subject__id=self.subject_id)
        if self.teacher not in teachers:
            raise ValidationError(
                f"The teacher {self.teacher} is not assigned to teach the subject {self.subject}."
            )
        groups = Group.objects.filter(subject__id=self.subject_id)
        if self.group not in groups:
            raise ValidationError(
                f"The lesson {self.subject} does not belong to the group {self.group}."
            )
        if not self.validate_lesson():
            raise ValidationError(
                'The teacher or group is busy at this time.',
                params={'start_time': self.start_time,
                        'end_time': self.end_time},
            )

    def __str__(self):
        return f'{self.teacher} {self.subject} - {self.start_time}:{self.end_time}'

    class Meta:
        ordering = ['start_time']
        verbose_name = _('lesson')
        verbose_name_plural = _('lessons')
        db_table = 'lesson'


@receiver(pre_save, sender=Lesson)
def update_end_time(sender, instance, **kwargs):
    if isinstance(instance.start_time, str):
        instance.start_time = datetime.datetime.strptime(
            instance.start_time, '%Y-%m-%d %H:%M:%S')
    instance.end_time = instance.start_time + \
        timedelta(minutes=instance.duration)


class Student(UUIDMixin, ModifiedMixin, CreatedMixin):
    user = models.OneToOneField(
        AppUser,  null=True, on_delete=models.CASCADE)
    full_name = models.CharField(verbose_name=_(
        'full name'), max_length=config.CHARS_DEFAULT)
    group = models.ForeignKey(Group, verbose_name=_(
        'group'), on_delete=models.CASCADE,
        db_column='group_id', blank=True, null=True)

    def __str__(self):
        return f'{self.full_name} - {self.group.title}'

    class Meta:
        ordering = ['full_name']
        verbose_name = _('student')
        verbose_name_plural = _('students')
        db_table = 'student'


class SubjectGroup(UUIDMixin, CreatedMixin):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, db_column='group_id')

    class Meta:
        db_table = 'subject__group'
        unique_together = (('subject', 'group'),)


class SubjectTeacher(UUIDMixin, CreatedMixin):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    class Meta:
        db_table = 'subject_teacher'
        unique_together = (('subject', 'teacher'),)
