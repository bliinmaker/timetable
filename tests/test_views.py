from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from timetable_app.models import AppUser, Subject, Student, Teacher
from django.test import TestCase
from uuid import uuid4
from rest_framework.authtoken.models import Token
from timetable_app.serializers import UserRegisterSerializer

from rest_framework.test import APITestCase
from rest_framework import status

class SubjectViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.subject = Subject.objects.create(title="Математика")

    def test_api_can_get_subjects(self):
        response = self.client.get('/api/subjects/')
        self.assertEqual(response.status_code, 200)

class UserRegisterTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_new_user(self):
        url = reverse('register')
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'password123',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(AppUser.objects.filter(email='newuser@example.com').exists())


class UserLoginTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = AppUser.objects.create_user(email='loginuser@example.com', password='password123')

    def test_login_valid_credentials(self):
        url = reverse('login')
        data = {
            'email': 'loginuser@example.com',
            'password': 'password123',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

    def test_login_invalid_credentials(self):
        url = reverse('login')
        data = {
            'email': 'invaliduser@example.com',
            'password': 'wrongpassword',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 404)


class CsrfTokenTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_csrf_token(self):
        url = reverse('csrf-token')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('csrf_token', response.data)


class UserDetailsViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Проверяем, существует ли уже пользователь с таким email
        self.user = AppUser.objects.create_user(email='user@example.com', password='user')
        self.user_token = Token.objects.create(user=self.user)
     
        # Создание студента и учителя для тестирования
        self.student = Student.objects.create(user=self.user, full_name='John Doe')
        self.teacher = Teacher.objects.create(user=self.user, full_name='Jane Smith')

    def test_student_detail_view(self):
        self.client.force_authenticate(user=self.user, token=self.user_token)

        detail_url = f'/api/user/{self.user.id}/student/'
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], 'John Doe')

    def test_teacher_detail_view(self):
        self.client.force_authenticate(user=self.user, token=self.user_token)
        detail_url = f'/api/user/{self.user.id}/teacher/'
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], 'Jane Smith')

    def test_nonexistent_user_student_detail_view(self):
        self.client.force_authenticate(user=self.user, token=self.user_token)
        nonexistent_id = uuid4()
        detail_url = f'/api/user/{nonexistent_id}/student/'
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Пользователь не найден')

    def test_nonexistent_user_teacher_detail_view(self):
        self.client.force_authenticate(user=self.user, token=self.user_token)
        nonexistent_id = uuid4()
        detail_url = f'/api/user/{nonexistent_id}/teacher/'
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Пользователь не найден')
