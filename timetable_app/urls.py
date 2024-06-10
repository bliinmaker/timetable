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
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/register/', views.UserRegister.as_view(), name='register'),
    path('api/login/', views.UserLogin.as_view(), name='login'),
    path('api/logout/', views.UserLogout.as_view(), name='logout'),
    path('api/user/', views.UserView.as_view(), name='user'),
    path('api/session/', views.session_view, name='api-session'),
    path('api/user/<str:id>/student/', views.UserStudentDetailView.as_view(), name='user-student-detail'),
    path('api/user/<str:id>/teacher/', views.UserTeacherDetailView.as_view(), name='user-teacher-detail'),
]
