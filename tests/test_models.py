"""Module for testing models."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import timedelta, datetime
from django.core.exceptions import ValidationError
from datetime import date
from rest_framework.test import APIClient
from typing import Iterable
from django.utils.timezone import timezone
from timetable_app.models import AppUser, Faculty, Group, Subject, Teacher, Lesson, Student, check_created, check_modified


from django.test import TestCase, SimpleTestCase
from django.utils.module_loading import import_string

def create_model_test(model_class, valid_attrs: dict, bunch_of_invalid_attrs: Iterable = None):
    """Create test for model.

    Args:
        model_class: model which we need to test
        valid_attrs: valid attrs for succsessfuly creating model.
        bunch_of_invalid_attrs: invalid attrs for unsuccsessfuly creating models.

    Returns:
        _type_: _description_
    """
    class ModelTest(TestCase):
        def test_unsuccessful_creation(self):
            if bunch_of_invalid_attrs:
                for invalid_attrs in bunch_of_invalid_attrs:
                    self.check_raises_invalid_attrs(invalid_attrs)

        def check_raises_invalid_attrs(self, invalid_attrs):
            with self.assertRaises(ValidationError):
                self.try_save(invalid_attrs)

        def test_successful_creation(self):
            self.try_save(valid_attrs)

        def try_save(self, attrs):
            instance = model_class(**attrs)
            instance.full_clean()
            instance.save()

    return ModelTest


class AuthorizationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.superuser = get_user_model().objects.create_superuser(username='superuser', password='12345', email='superuser@example.com')
        self.user = get_user_model().objects.create_user(password='12345', email='normal@example.com')

    def test_superuser_access(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get('/api/lessons/')
        self.assertEqual(response.status_code, 200)

    def test_normal_user_access(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/lessons/')
        self.assertEqual(response.status_code, 200)


def get_valid_appuser_attrs():
    return {
        'email': 'test@example.com',
        'username': 'testuser',
    }

def get_invalid_appuser_attrs():
    return (
        {},
        {'email': 'test@example.com'},
        {'username': 'testuser'},
    )

class AppUserModelTest(TestCase):
    def setUp(self):
        self.valid_attrs = get_valid_appuser_attrs()
        self.invalid_attrs = get_invalid_appuser_attrs()

    def test_appuser_creation(self):
        self.assertTrue(create_model_test(AppUser, self.valid_attrs))
        self.assertTrue(create_model_test(AppUser, self.invalid_attrs))


def get_valid_faculty_attrs():
    return {
        'title': 'Computer Science',
        'code_faculty': 'CS101',
        'description': 'Study computer science fundamentals.'
    }

def get_invalid_faculty_attrs():
    return (
        {'title': '', 'code_faculty': 'CS101', 'description': 'Some description.'},
        {'title': 'Computer Science', 'code_faculty': '', 'description': 'Some description.'},
        {'title': 'Computer Science', 'code_faculty': 'CS101', 'description': ''},
    )

class FacultyModelTest(TestCase):
    def setUp(self):
        self.valid_attrs = get_valid_faculty_attrs()
        self.invalid_attrs = get_invalid_faculty_attrs()

    def test_faculty_creation(self):
        self.assertTrue(create_model_test(Faculty, self.valid_attrs))

    def test_faculty_validation(self):
        self.assertTrue(create_model_test(Faculty, self.invalid_attrs))


def get_valid_subject_attrs():
    return {
        'title': 'Основы программирования',
    }

def get_invalid_subject_attrs():
    return (
        {'title': ''},
    )

class SubjectModelTest(TestCase):
    def setUp(self):
        self.valid_attrs = get_valid_subject_attrs()
        self.invalid_attrs = get_invalid_subject_attrs()

    def test_subject_creation(self):
        self.assertTrue(create_model_test(Subject, self.valid_attrs))
        self.assertTrue(create_model_test(Subject, self.invalid_attrs))

def get_valid_teacher_attrs():
    return {
        'full_name': 'Иванов Иван Иванович',
        'subjects': Subject.objects.all(),
    }

def get_invalid_teacher_attrs():
    return (
        {'full_name': '', 'subjects': Subject.objects.all()},
        {'full_name': 'Иванов Иван Иванович', 'subjects': []},
    )

class TeacherModelTest(TestCase):
    def setUp(self):
        self.valid_attrs = get_valid_teacher_attrs()
        self.invalid_attrs = get_invalid_teacher_attrs()

    def test_teacher_creation(self):
        self.assertTrue(create_model_test(Teacher, self.valid_attrs))
        self.assertTrue(create_model_test(Teacher, self.invalid_attrs))

def get_valid_lesson_attrs():
    today_date = date.today()
    return {
        'date': today_date,
        'lesson_slot': 1,
        'subject': Subject.objects.first(),
        'teacher': Teacher.objects.first(),
        'group': Group.objects.first(),
    }

def get_invalid_lesson_attrs():
    today_date = date.today()
    return (
        {'date': None, 'lesson_slot': 1, 'subject': Subject.objects.first(), 'teacher': Teacher.objects.first(), 'group': Group.objects.first()},
        {'date': today_date, 'lesson_slot': 7, 'subject': Subject.objects.first(), 'teacher': Teacher.objects.first(), 'group': Group.objects.first()},
    )

class LessonModelTest(TestCase):
    def setUp(self):
        self.valid_attrs = get_valid_lesson_attrs()
        self.invalid_attrs = get_invalid_lesson_attrs()

    def test_lesson_creation(self):
        self.assertTrue(create_model_test(Lesson, self.valid_attrs))
        self.assertTrue(create_model_test(Lesson, self.invalid_attrs))

def get_valid_student_attrs():
    return {
        'full_name': 'Пупкин Василий Васильевич',
        'group': Group.objects.first(),
    }

def get_invalid_student_attrs():
    return (
        {'full_name': '', 'group': Group.objects.first()},
        {'full_name': 'Пупкин Василий Васильевич', 'group': None},
    )

class StudentModelTest(TestCase):
    def setUp(self):
        self.valid_attrs = get_valid_student_attrs()
        self.invalid_attrs = get_invalid_student_attrs()

    def test_student_creation(self):
        self.assertTrue(create_model_test(Student, self.valid_attrs))
        self.assertTrue(create_model_test(Student, self.invalid_attrs))

class LessonTimeValidationTest(TestCase):
    def setUp(self):
        self.lesson1 = Lesson.objects.create(date=date.today(), lesson_slot=1)
        self.lesson2 = Lesson.objects.create(date=date.today(), lesson_slot=1)

    def test_no_overlapping_times(self):
        with self.assertRaises(ValidationError):
            self.lesson2.clean()

    def test_within_slot_bounds(self):
        self.lesson2.lesson_slot = 7
        with self.assertRaises(ValidationError):
            self.lesson2.clean()


class LessonValidationTest(TestCase):
    def test_validate_lesson_with_existing_conflict(self):
        Lesson.objects.create(date=date.today(), lesson_slot=1)
        lesson = Lesson.objects.create(date=date.today(), lesson_slot=1)
        with self.assertRaises(ValidationError):
            lesson.clean()

    def test_validate_lesson_with_future_date(self):
        lesson = Lesson.objects.create(date=date.today() + timedelta(days=1), lesson_slot=1)
        with self.assertRaises(ValidationError):
            lesson.clean()


PAST = datetime(datetime.today().year-1, 1, 1, 1, 1, 1, 1, tzinfo=timezone.utc)
FUTURE = datetime(datetime.today().year+1, 1, 1, 1, 1, 1, 1, tzinfo=timezone.utc)


validators_pass = (
    (check_created, PAST),
    (check_modified, PAST),
)

validators_fail = (
    (check_created, FUTURE),
    (check_modified, FUTURE),
)

def create_val_test(validator, value, valid=True):
    def test(self):
        with self.assertRaises(ValidationError):
            validator(value)
    return lambda _ : validator(value) if valid else test

invalid_methods = {f'test_inval_{args[0].__name__}': create_val_test(*args, valid=False) for args in validators_fail}
valid_methods = {f'test_val_{args[0].__name__}': create_val_test(*args) for args in validators_pass}

ValidatorsTest = type('ValidatorsTest', (TestCase,), invalid_methods | valid_methods)