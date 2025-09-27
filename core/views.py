from django.shortcuts import render
from django.views.generic.edit import CreateView,FormView
from core.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.urls import reverse_lazy
from core.forms import LoginForm
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.

# LogIn For Student/Faculty/Librarian/Admin

class LogInView(FormView):
    form_class = LoginForm
    template_name = 'core/LoginForm.html'
    success_url = reverse_lazy('admin/')

    def form_valid(self, form):
        # Process form data
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        # Authenticate User
        user = authenticate(self.request,username=username,password=password)

        if user is not None:
            login(self.request,user)

            if user.role == User.Role_choice.STUDENT:
                return redirect('stdashviewurl')
            
            elif user.role == User.Role_choice.FACULTY:
                return redirect('facdashviewurl')
            
            elif user.role == User.Role_choice.LIBRARIAN:
                return redirect('libdashviewurl')
            
        else:
            # Failed Authentication

            form.add_error(None,"Please enter correct username and password")
            return self.form_invalid(form)


class StudentDashboardView(LoginRequiredMixin,TemplateView):
    template_name = 'core/Student_dashboard.html'
    login_url = 'loginviewurl'

class LibrarianDashboardView(LoginRequiredMixin,TemplateView):
    template_name = 'core/Librarian_dashboard.html'
    login_url = 'loginviewurl'

class FacultyDashboardView(LoginRequiredMixin,TemplateView):
    template_name = 'core/Faculty_dashboard.html'
    login_url = 'loginviewurl'