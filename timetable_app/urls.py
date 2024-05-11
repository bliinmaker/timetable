"""timatable_app URL Configuration."""
from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'lessons', views.LessonViewSet)
router.register(r'teachers', views.TeacherViewSet)
router.register(r'subjects', views.SubjectViewSet)
router.register(r'students', views.StudentViewSet)
router.register(r'faculties', views.FacultyViewSet)
router.register(r'groups', views.GroupViewSet)

urlpatterns = [
    path('', views.custom_main, name='homepage'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('rest/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
