from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from core.views import (
    LogInView,
    StudentDashboardView,
    LibrarianDashboardView,
    FacultyDashboardView,
    RequestBookView,
    BookIssuedView,
    SearchBookView,
    IssueABook,
    UserRegistrationView,
    UserView,
    UserDetailView,
    RemoveBookView,
)
urlpatterns = [
    path('',LogInView.as_view(),name='loginviewurl'),
    path('student/dashboard/',StudentDashboardView.as_view(),name='stdashviewurl'),
    path('librarian/dashboard/',LibrarianDashboardView.as_view(),name='libdashviewurl'),
    path('faculty/dashboard/',FacultyDashboardView.as_view(),name='facdashviewurl'),
    path('faculty/dashboard/requestbook',RequestBookView.as_view(),name='requestbook'),
    path('faculty/dashboard/searchbook',SearchBookView.as_view(),name='searchbook'),
    path('faculty/dashboard/bookissued',BookIssuedView.as_view(),name='bookissued'),
    path('faculty/dashboard/<int:pk>/issuebook',IssueABook.as_view(),name='issuebook'),
    path('faculty/dashboard/userview',UserView.as_view(),name='userlist'),
    path('faculty/dashboard/<str:type>/<str:pk>/',UserDetailView.as_view(),name='userdetail'),
    path('logout/',LogoutView.as_view(next_page='loginviewurl'),name='logout'),
    path('librarian/registeruser',UserRegistrationView.as_view(),name='registeruser'),
    path('<str:type>/<str:pk>/remove_book/<int:book_id>/', RemoveBookView.as_view(), name='remove_book'),
    path('admin/', admin.site.urls),
]