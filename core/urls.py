from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from core.views import (
    LogInView,
    StudentDashboardView,
    LibrarianDashboardView,
    FacultyDashboardView,
)
urlpatterns = [
    path('',LogInView.as_view(),name='loginviewurl'),
    path('student/dashboard/',StudentDashboardView.as_view(),name='stdashviewurl'),
    path('librarian/dashboard/',LibrarianDashboardView.as_view(),name='libdashviewurl'),
    path('faculty/dashboard/',FacultyDashboardView.as_view(),name='facdashviewurl'),
    path('logout/',LogoutView.as_view(next_page='loginviewurl'),name='logout'),
    path('admin/', admin.site.urls),
]