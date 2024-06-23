"""Models for the Timetable application."""
from datetime import datetime, time
from uuid import uuid4
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from . import config


LESSON_SLOT_CHOICES = [
    (1, 'Первая пара'),
    (2, 'Вторая пара'),
    (3, 'Третья пара'),
    (4, 'Четвертая пара'),
    (5, 'Пятая пара'),
    (6, 'Шестая пара'),
]


def get_datetime():
    """
    Return the current datetime.

    Returns:
        Current datetime object.
    """
    return timezone.now()


def check_created(dt: datetime) -> None:
    """
    Validate if the provided datetime is greater than the current datetime.

    Args:
        dt (datetime): datetime to validate against the current datetime.

    Raises:
        ValidationError: if the provided datetime is in the past.
    """
    if dt > get_datetime():
        raise ValidationError(
            _('Datetime is bigger than current datetime!'),
            params={'created': dt}
        )


def check_modified(dt: datetime) -> None:
    """
    Validate if the provided datetime is greater than the current datetime.

    Args:
        dt (datetime): datetime to validate against the current datetime.

    Raises:
        ValidationError: if the provided datetime is in the past.
    """
    if dt > get_datetime():
        raise ValidationError(
            _('Datetime is bigger than current datetime!'),
            params={'modified': dt}
        )


class UUIDMixin(models.Model):
    """Mixin class for adding a UUID primary key field to a model.

    Attributes:
        id: UUIDField representing the primary key.
    """

    id = models.UUIDField(
        primary_key=True, blank=True, editable=False, default=uuid4
    )

    class Meta:
        """
        Define metadata options for the UUIDMixin model.

        Attributes:
            abstract (bool): Indicates that this model should be treated as an abstract base class.
        """

        abstract = True


class CreatedMixin(models.Model):
    """Mixin class for adding a 'created' field to a model.

    Attributes:
        created: DateTimeField representing the creation timestamp.
    """

    created = models.DateTimeField(
        _('created'),
        null=True, blank=True,
        default=get_datetime,
        validators=[
            check_created,
        ]
    )

    class Meta:
        """
        Define metadata options for the CreatedMixin model.

        Attributes:
            abstract (bool): Indicates that this model should be treated as an abstract base class.
        """

        abstract = True


class ModifiedMixin(models.Model):
    """Mixin class for adding a 'modified' field to a model.

    Attributes:
        modified: DateTimeField representing the last modification timestamp.
    """

    modified = models.DateTimeField(
        _('modified'),
        null=True, blank=True,
        default=get_datetime,
        validators=[
            check_modified,
        ]
    )

    class Meta:
        """
        Define metadata options for the ModifiedMixin model.

        Attributes:
            abstract (bool): Indicates that this model should be treated as an abstract base class.
        """

        abstract = True


class AppUserManager(BaseUserManager):
    """
    Custom manager for the AppUser model.

    Inherit from Django's BaseUserManager to provide custom methods for creating users.

    Methods:
        create_user(email, password=None): сreates a User instance.
        create_superuser(email, username, password=None): сreates a SuperUser instance.
    """

    def create_user(self, email, password=None):
        """
        Create a User instance.

        Args:
            email (str): email address of the user.
            password (str, optional): password of the user. Defaults to None.

        Raises:
            ValueError: if the email or password is missing.

        Returns:
            AppUser: User instance.
        """
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
        """
        Create a SuperUser instance.

        Args:
            email (str): email address of the user.
            username (str): username of the user.
            password (str, optional): password of the user. Defaults to None.

        Raises:
            ValueError: if the email, username, or password is missing.

        Returns:
            AppUser: SuperUser instance.
        """
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
    """Model representing a user.

    Attributes:
        email (models.EmailField): EmailField representing the user's email.
        username (models.CharField): CharField representing the user's username.
        is_staff (models.BooleanField): BooleanField representing user's status.
        is_superuser (models.BooleanField): BooleanField representing user's status.
        is_active (models.BooleanField): BooleanField representing user's status.
        date_joined (models.DateTimeField): DateTimeField representing the time user was created.
    """

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
        """
        Return the username of the user as a string.

        Attributes:
            username (CharField): CharField representing the user's username.

        Returns:
            str: The username of the user.
        """
        return self.username

    class Meta:
        ordering = ['username']
        verbose_name = _('app_user')
        verbose_name_plural = _('app_users')
        db_table = 'app_user'


class Faculty(UUIDMixin, CreatedMixin, ModifiedMixin):
    """
    Model representing a faculty.

    Attributes:
        title (CharField): Title of the faculty.
        code_faculty (CharField): Code of the faculty.
        description (TextField): Description of the faculty.
    """

    title = models.CharField(_('faculty'), max_length=config.CHARS_DEFAULT)
    code_faculty = models.CharField(_('code faculty'), max_length=config.CHARS_DEFAULT)
    description = models.TextField(_('description'), blank=True, null=True)

    def __str__(self):
        """
        Return a string combining the title of the faculty and its code.

        Attributes:
            title (CharField): Title of the faculty.
            code_faculty (CharField): Code of the faculty.

        Returns:
            str: A string in the format "{title} ({code_faculty}".
        """
        return '{0} ({1})'.format(self.title, self.code_faculty)

    class Meta:
        ordering = ['title']
        verbose_name = _('faculty')
        verbose_name_plural = _('faculties')
        db_table = 'faculty'


class Group(UUIDMixin, CreatedMixin, ModifiedMixin):
    """
    Model representing a study group.

    Attributes:
        title (CharField): Title of the group.
        faculty (ForeignKey): Reference to the Faculty model indicating the group's faculty.
        subjects (ManyToManyField): ManyToMany relationship to the Subject model through the SubjectGroup model.
    """

    title = models.CharField(_('group'), max_length=config.CHARS_DEFAULT)
    faculty = models.ForeignKey(Faculty, verbose_name=_('faculty'), on_delete=models.CASCADE)
    subjects = models.ManyToManyField('Subject', verbose_name=_('subjects'), through='SubjectGroup')

    def __str__(self):
        """
        Return a string combining the title of the group and the faculty it belongs to.

        Attributes:
            title (CharField): Title of the group.
            faculty (ForeignKey): Reference to the Faculty model indicating the group's faculty.

        Returns:
            str: A string in the format "{title} ({faculty})".
        """
        return '{0} ({1})'.format(self.title, self.faculty)

    class Meta:
        ordering = ['title']
        verbose_name = _('group')
        verbose_name_plural = _('groups')
        db_table = 'group'


class Subject(UUIDMixin, CreatedMixin, ModifiedMixin):
    """
    Model representing a subject.

    Attributes:
        title (CharField): Title of the subject.
        groups (ManyToManyField): ManyToMany relationship to the Group model through the SubjectGroup model.
        teachers (ManyToManyField): ManyToMany relationship to the Teacher model through the SubjectTeacher model.
    """

    title = models.CharField(_('title'), max_length=config.CHARS_DEFAULT)
    groups = models.ManyToManyField(Group, verbose_name=_('groups'), through='SubjectGroup')
    teachers = models.ManyToManyField('Teacher', verbose_name=_('teachers'), through='SubjectTeacher')

    def __str__(self):
        """
        Return the title of the subject as a string.

        Attributes:
            title (CharField): CharField representing the title of the subject.

        Returns:
            str: The title of the subject.
        """
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name = _('subject')
        verbose_name_plural = _('subjects')
        db_table = 'subject'


class Teacher(UUIDMixin, CreatedMixin, ModifiedMixin):
    """
    Model representing a teacher.

    Attributes:
        user (OneToOneField): Link to the associated AppUser model.
        full_name (CharField): Full name of the teacher.
        subjects (ManyToManyField): ManyToMany relationship to the Subject model through the SubjectTeacher model.
    """

    user = models.OneToOneField(AppUser, null=True, on_delete=models.CASCADE)
    full_name = models.CharField(_('full name'), max_length=config.CHARS_DEFAULT)
    subjects = models.ManyToManyField(Subject, verbose_name=_('subjects'), through='SubjectTeacher')

    def __str__(self):
        """
        Return the full name of the teacher as a string.

        Attributes:
            full_name (CharField): CharField representing the full name of the teacher.

        Returns:
            str: The full name of the teacher.
        """
        return self.full_name

    class Meta:
        ordering = ['full_name']
        verbose_name = _('teacher')
        verbose_name_plural = _('teachers')
        db_table = 'teacher'


class Lesson(UUIDMixin, CreatedMixin, ModifiedMixin):
    """
    Model representing a lesson.

    Attributes:
        date (DateField): Date of the lesson.
        lesson_slot (IntegerField): IntegerField representing the lesson slot.
        start_time (DateTimeField): Start time of the lesson.
        end_time (DateTimeField): End time of the lesson.
        subject (ForeignKey): Reference to the Subject model indicating the subject of the lesson.
        teacher (ForeignKey): Reference to the Teacher model indicating the teacher of the lesson.
        group (ForeignKey): Reference to the Group model indicating the group for the lesson.

    Methods:
        validate_lesson(): Validates the lesson based on various conditions.
        clean(): Cleans the lesson data before saving.
    """

    date = models.DateField(_('date'), blank=False, null=True)
    lesson_slot = models.IntegerField(_('lesson slot'), choices=LESSON_SLOT_CHOICES, blank=False, null=True)
    start_time = models.DateTimeField(_('start time'), blank=True, null=True, editable=False)
    end_time = models.DateTimeField(_('end time'), blank=True, null=True, editable=False)
    subject = models.ForeignKey(Subject, verbose_name=_('subject'), on_delete=models.CASCADE, blank=False, null=True)
    teacher = models.ForeignKey(Teacher, verbose_name=_('teacher'), on_delete=models.CASCADE, blank=False, null=True)
    group = models.ForeignKey(Group, verbose_name=_('group'), on_delete=models.CASCADE, blank=False, null=True)

    def validate_lesson(self) -> bool:
        """
        Validate the lesson based on various conditions.

        This method checks if the lesson slot is valid and sets the start and end times accordingly.

        Attributes:
            date (DateField): Date of the lesson.
            lesson_slot (IntegerField): IntegerField representing the lesson slot.
            start_time (DateTimeField): Start time of the lesson.
            end_time (DateTimeField): End time of the lesson.
            teacher (ForeignKey): Reference to the Teacher model indicating the teacher of the lesson.
            group (ForeignKey): Reference to the Group model indicating the group for the lesson.

        Returns:
            bool: True if the lesson passes all validation checks, False otherwise.

        Raises:
            ValueError: If the lesson slot is invalid.
        """
        if self.date and self.lesson_slot:
            if self.lesson_slot == 1:
                self.start_time = timezone.make_aware(datetime.combine(self.date, time(hour=9, minute=0)))
                self.end_time = timezone.make_aware(datetime.combine(self.date, time(hour=10, minute=30)))
            elif self.lesson_slot == 2:
                self.start_time = timezone.make_aware(datetime.combine(self.date, time(hour=10, minute=45)))
                self.end_time = timezone.make_aware(datetime.combine(self.date, time(hour=12, minute=15)))
            elif self.lesson_slot == 3:
                self.start_time = timezone.make_aware(datetime.combine(self.date, time(hour=13, minute=15)))
                self.end_time = timezone.make_aware(datetime.combine(self.date, time(hour=14, minute=45)))
            elif self.lesson_slot == 4:
                self.start_time = timezone.make_aware(datetime.combine(self.date, time(hour=15, minute=0)))
                self.end_time = timezone.make_aware(datetime.combine(self.date, time(hour=16, minute=30)))
            elif self.lesson_slot == 5:
                self.start_time = timezone.make_aware(datetime.combine(self.date, time(hour=16, minute=45)))
                self.end_time = timezone.make_aware(datetime.combine(self.date, time(hour=18, minute=15)))
            elif self.lesson_slot == 6:
                self.start_time = timezone.make_aware(datetime.combine(self.date, time(hour=18, minute=30)))
                self.end_time = timezone.make_aware(datetime.combine(self.date, time(hour=20, minute=00)))
            else:
                raise ValueError("Invalid lesson slot")
        try:
            teachers_lessons = Lesson.objects.filter(teacher__id=self.teacher.id)
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
        for group_lesson in group_lessons:
            if group_lesson.start_time is not None and group_lesson.end_time is not None:
                if group_lesson.start_time <= self.start_time <= group_lesson.end_time:
                    return False
                if group_lesson.start_time <= self.end_time <= group_lesson.end_time:
                    return False
        return True

    def clean(self):
        """
        Clean the lesson data before saving.

        Raises:
            ValidationError: If any of the validation checks fail, a ValidationError is raised.

        Methods:
            validate_lesson(): Called within clean() to perform additional validation on the lesson schedule.
        """
        super().clean()
        teachers = Teacher.objects.filter(subject__id=self.subject_id)
        if self.teacher not in teachers:
            raise ValidationError("It isn't teacher's {0} subject {1}.".format(self.teacher, self.subject))
        groups = Group.objects.filter(subject__id=self.subject_id)
        if self.group not in groups:
            raise ValidationError("The lesson {0} does not belong to the group {1}.".format(self.subject, self.group))
        if not self.validate_lesson():
            raise ValidationError(
                'The teacher or group is busy at this time.',
                params={'start_time': self.start_time, 'end_time': self.end_time},
            )

    def __str__(self):
        """
        Return a human-readable string representation of the lesson.

        Attributes:
            teacher (ForeignKey): Reference to the Teacher model indicating the teacher of the lesson.
            subject (ForeignKey): Reference to the Subject model indicating the subject of the lesson.
            start_time (DateTimeField): Start time of the lesson.
            end_time (DateTimeField): End time of the lesson.

        Returns:
            str: A string in the format "{teacher} {subject} - {start_time}:{end_time}".
        """
        return '{0} {1} - {2}:{3}'.format(self.teacher, self.subject, self.start_time, self.end_time)

    class Meta:
        ordering = ['start_time']
        verbose_name = _('lesson')
        verbose_name_plural = _('lessons')
        db_table = 'lesson'


class Student(UUIDMixin, ModifiedMixin, CreatedMixin):
    """
    Model representing a student enrolled in a group.

    Attributes:
        user (OneToOneField): Link to the associated AppUser model.
        full_name (CharField): Full name of the student.
        group (ForeignKey): Reference to the Group model indicating the student's group.
    """

    user = models.OneToOneField(AppUser, null=True, on_delete=models.CASCADE)
    full_name = models.CharField(verbose_name=_('full name'), max_length=config.CHARS_DEFAULT)
    group = models.ForeignKey(
        Group,
        verbose_name=_('group'),
        on_delete=models.CASCADE,
        db_column='group_id',
        blank=True,
        null=True
    )

    def __str__(self):
        """
        Return a human-readable string representation of the student.

        This method returns a string combining the student's full name and the title of their group.

        Attributes:
            full_name (CharField): Full name of the student.
            group (ForeignKey): Reference to the Group model indicating the student's group.

        Returns:
            str: A string in the format "{full_name} - {group_title}".
        """
        return '{0} - {1}'.format(self.full_name, self.group.title)

    class Meta:
        ordering = ['full_name']
        verbose_name = _('student')
        verbose_name_plural = _('students')
        db_table = 'student'


class SubjectGroup(UUIDMixin, CreatedMixin):
    """
    Intermediary model connecting Subjects and Groups, allowing many-to-many relationships.

    Attributes:
        subject (ForeignKey): Reference to the Subject model.
        group (ForeignKey): Reference to the Group model.
    """

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, db_column='group_id')

    class Meta:
        db_table = 'subject__group'
        unique_together = (('subject', 'group'),)


class SubjectTeacher(UUIDMixin, CreatedMixin):
    """
    Intermediary model connecting Subjects and Teachers, allowing many-to-many relationships.

    Attributes:
        subject (ForeignKey): Reference to the Subject model.
        teacher (ForeignKey): Reference to the Teacher model.
    """

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    class Meta:
        db_table = 'subject_teacher'
        unique_together = (('subject', 'teacher'),)
