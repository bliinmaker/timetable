from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from timetable_app.validations import custom_validation, validate_email, validate_username, validate_password

class CustomValidationTest(TestCase):
    def test_custom_validation_success(self):
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass'
        }
        try:
            custom_validation(data)
        except ValidationError as e:
            self.fail("Custom validation failed unexpectedly")

    def test_custom_validation_failure(self):
        data = {
            'email': '',
            'username': 'testuser',
            'password': 'test'
        }
        with self.assertRaises(ValidationError):
            custom_validation(data)

class ValidateEmailTest(TestCase):
    def test_validate_email_success(self):
        data = {'email': 'test@example.com'}
        self.assertTrue(validate_email(data))

    def test_validate_email_failure(self):
        data = {'email': ''}
        with self.assertRaises(ValidationError):
            validate_email(data)


class ValidateUsernameTest(TestCase):
    def test_validate_username_success(self):
        data = {'username': 'testuser'}
        self.assertTrue(validate_username(data))

    def test_validate_username_failure(self):
        data = {'username': ''}
        with self.assertRaises(ValidationError):
            validate_username(data)


class ValidatePasswordTest(TestCase):
    def test_validate_password_success(self):
        data = {'password': 'testpass'}
        self.assertTrue(validate_password(data))

    def test_validate_password_failure(self):
        data = {'password': ''}
        with self.assertRaises(ValidationError):
            validate_password(data)


