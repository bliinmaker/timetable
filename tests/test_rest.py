from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from timetable_app.models import AppUser, Faculty, Group, Subject, Teacher, Lesson, Student

def create_viewset_test(model_class, url, creation_attrs):
    class ViewSetTest(TestCase):
        def setUp(self):
            self.client = APIClient()
            self.user = AppUser.objects.create_user(email='user@example.com', password='user')
            self.superuser = AppUser.objects.create_superuser(email='superuser@example.com', username='superuser', password='superuser')
            self.user_token = Token.objects.create(user=self.user)
            self.superuser_token = Token.objects.create(user=self.superuser)

        def get(self, user: AppUser, token: Token):
            self.client.force_authenticate(user=user, token=token)
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        def test_get_by_user(self):
            self.get(self.user, self.user_token)

        def test_get_by_superuser(self):
            self.get(self.superuser, self.superuser_token)

        def manage(self, user: AppUser, token: Token, post_status: int, put_status: int, delete_status: int):
            self.client.force_authenticate(user=user, token=token)

            # POST
            response = self.client.post(url, creation_attrs)
            self.assertEqual(response.status_code, post_status)

            # Создание существующего объекта для дальнейших тестов
            created_id = model_class.objects.create(**creation_attrs).id

            # PUT
            response = self.client.put(f'{url}{created_id}/', creation_attrs)
            self.assertEqual(response.status_code, put_status)

            # DELETE
            response = self.client.delete(f'{url}{created_id}/')
            self.assertEqual(response.status_code, delete_status)

        def test_manage_user(self):
            self.manage(
                self.user, self.user_token,
                post_status=status.HTTP_403_FORBIDDEN,
                put_status=status.HTTP_403_FORBIDDEN,
                delete_status=status.HTTP_403_FORBIDDEN,
            )

        def test_manage_superuser(self):
            self.manage(
                self.superuser, self.superuser_token,
                post_status=status.HTTP_201_CREATED,
                put_status=status.HTTP_200_OK,
                delete_status=status.HTTP_204_NO_CONTENT,
            )

    return ViewSetTest

SubjectViewSetTest = create_viewset_test(
    Subject, '/api/subjects/', {'title': 'Химия'})
StudentViewSetTest = create_viewset_test(
    Student, '/api/students/', {'full_name': 'Бартович Михаил'})
TeacherViewSetTest = create_viewset_test(
    Teacher, '/api/teachers/', {'full_name': 'Верховой Игорь'})
FacultyViewSetTest = create_viewset_test(
    Faculty, '/api/faculties/', {
        'title': 'Гуманитарные науки',
        'code_faculty': 'HN-23',
        'description': '',
    })
