"""
Validates data for various operations in the application.

This module provides functions for validating data used across different parts of the application.
"""

from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
UserModel = get_user_model()


def custom_validation(data):
    """
    Validate general data against common criteria.

    Performs basic validation checks on the provided data dictionary.

    Args:
        data (dict): A dictionary containing data to be validated.

    Raises:
        ValidationError: If any of the validation checks fail.
    """
    email = data['email'].strip()
    username = data['username'].strip()
    password = data['password'].strip()
    if not email or UserModel.objects.filter(email=email).exists():
        raise ValidationError('choose another email')
    if not password or len(password) < 8:
        raise ValidationError('choose another password, min 8 characters')
    if not username:
        raise ValidationError('choose another username')
    return data


def validate_email(data):
    """
    Validate that an email address is present and not empty.

    Ensures that the 'email' key in the provided data dictionary contains a non-empty string.

    Args:
        data (dict): A dictionary containing data to be validated, expected to have a key 'email'.

    Returns:
        bool: True if the email is valid, False otherwise.

    Raises:
        ValidationError: If the email is not valid.
    """
    email = data['email'].strip()
    if not email:
        raise ValidationError('an email is needed')
    return True


def validate_username(data):
    """
    Validate that a username is present and not empty.

    Ensures that the 'username' key in the provided data dictionary contains a non-empty string.

    Args:
        data (dict): A dictionary containing data to be validated, expected to have a key 'username'.

    Returns:
        bool: True if the username is valid, False otherwise.

    Raises:
        ValidationError: If username checks fail.
    """
    username = data['username'].strip()
    if not username:
        raise ValidationError('choose another username')
    return True


def validate_password(data):
    """
    Validate that a password is present and meet minimum length criteria.

    Ensures that the 'password' key in the provided data dictionary contains a non-empty string.

    Args:
        data (dict): A dictionary containing data to be validated, expected to have a key 'password'.

    Returns:
        bool: True if the password is valid, False otherwise.

    Raises:
        ValidationError: If the password is not valid.
    """
    password = data['password'].strip()
    if not password:
        raise ValidationError('a password is needed')
    return True
