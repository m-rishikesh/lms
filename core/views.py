from django.shortcuts import render,get_object_or_404
from django.views.generic.edit import CreateView,FormView
from django.views.generic import ListView,DetailView,DeleteView
from core.models import User,Book,BookRequest,Student,Faculty,Notification
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from core.forms import LoginForm,RequestBookForm,UserRegistrationForm,NotificationForm,FinePaymentForm
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q,Sum,Count
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

class SearchBookView(LoginRequiredMixin,ListView):
    model: Book
    template_name = 'core/searchedbooklist.html'
    context_object_name = 'books'

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            get_list = Book.objects.filter(title__icontains=query)
            print(get_list)
            return get_list
        return None

class RequestBookView(LoginRequiredMixin,FormView):
    form_class = RequestBookForm
    template_name = 'core/RequestedBookForm.html'
    success_url = reverse_lazy("requestbook")

    def form_valid(self, form):
        book = form.save(commit=False)
        user = self.request.user
        book.requestedBy = user
        book.save()
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['RequestList'] = BookRequest.objects.filter(requestedBy=self.request.user)
        return context
    
class BookIssuedView(LoginRequiredMixin,ListView):
    model = User
    template_name = 'core/bookissued.html'
    context_object_name = 'bookissued'

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'studentuser'):
            return user.studentuser.book.all()
        elif hasattr(user, 'facultyuser'):
            return user.facultyuser.book.all()
        return Book.objects.none()
    
class IssueABook(LoginRequiredMixin,View):
    def post(self,request,pk):
        getSelectedBook = get_object_or_404(Book,pk=pk)
        user = self.request.user
        student = getattr(user, 'studentuser', None)
        faculty = getattr(user, 'facultyuser', None)
        if student:
            if  student.book.count() < 2:
                student.book.add(getSelectedBook)
                student.save()
            else:
                 return HttpResponse(
        "<h1>Enough books issued</h1><p>You can only have 2 books at a time.</p>"
            )
        elif faculty:
            if faculty.book.count() < 2:
                faculty.book.add(getSelectedBook)
                faculty.save()
            else:
                 return HttpResponse(
        "<h1>Enough books issued</h1><p>You can only have 2 books at a time.</p>"
            )
        return redirect('bookissued')

class UserRegistrationView(LoginRequiredMixin,UserPassesTestMixin,CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'core/UserRegistrationForm.html'
    context_object_name = 'RegisteredData'
    success_url = reverse_lazy('libdashviewurl')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.date_joined = timezone.now()
        user.email = user.username
        user.set_password(form.cleaned_data['password'])
        user.save()
        role = form.cleaned_data['role']
        if role == User.Role_choice.STUDENT:
            Student.objects.create(
                name=user.get_full_name(),
                email=user.email,
                usn=form.cleaned_data['usn'],  
                user=user
            )
        elif role == User.Role_choice.FACULTY:
            Faculty.objects.create(
                name=user.get_full_name(),
                email=user.email,
                id=form.cleaned_data['faculty_id'], 
                user=user
            )
        return HttpResponse('<h1>successfully registered</h1>')    
    
    def test_func(self):
        return self.request.user.is_staff
    
class UserView(LoginRequiredMixin,UserPassesTestMixin,ListView):
    template_name = 'core/searchUser.html'
    context_object_name = 'UserList'

    def get_queryset(self):
        query = self.request.GET.get("q") 
        students = Student.objects.all()
        faculty = Faculty.objects.all()
        if query:
            students = students.filter(Q(name__icontains=query) | Q(usn__icontains=query))
            # Filter faculty by name or ID
            faculty = faculty.filter(Q(name__icontains=query) | Q(id__icontains=query))
        return list(students) + list(faculty)
    
    def test_func(self):
        return self.request.user.is_staff
    
class UserDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    template_name = 'core/user_detail.html'
    context_object_name = 'profile'

    def get_object(self):
        # Determine if it's a student or faculty by GET parameter or pk
        profile_type = self.kwargs.get('type')
        pk = self.kwargs.get('pk')
        if profile_type == 'student':
            return Student.objects.get(usn=pk)
        elif profile_type == 'faculty':
            return Faculty.objects.get(id=pk)

    def test_func(self):
        return self.request.user.is_staff
    
class RemoveBookView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, type, pk, book_id):
        if type == 'student':
            profile = get_object_or_404(Student, usn=pk)
        elif type == 'faculty':
            profile = get_object_or_404(Faculty, id=pk)
        else:
            return redirect('user_list')

        book = get_object_or_404(Book, id=book_id)
        profile.book.remove(book)
        return redirect('userdetail', type=type, pk=pk)

    def test_func(self):
        return self.request.user.is_staff


class manageCatalougeView(LoginRequiredMixin,UserPassesTestMixin,View):
    template_name = 'core/managecatalouge.html'
    def get(self,request,*args,**kwargs):

        book_by_genre = Book.objects.values('category').annotate(
            total_copies=Sum('total_copies'),
            available_copies = Sum('available_copies'),
            total_book_by_genre = Count('id')
            )

        books = Book.objects.all()
        category_choices = Book.Category.choices

        return render(request,self.template_name,{
            "books_by_genre": book_by_genre,
            "books": books,
            "category_choices": category_choices,
        })
    
    def post(self,request,*args,**kwargs):
        action = request.POST.get("action")

        if action == 'add':
            Book.objects.create(
                title=request.POST.get("title"),
                author=request.POST.get("author"),
                isbn=request.POST.get("isbn"),
                category=request.POST.get("category"),
                publisher=request.POST.get("publisher"),
                published_year=request.POST.get("published_year") or None,
                total_copies=int(request.POST.get("total_copies", 1)),
                available_copies=int(request.POST.get("total_copies", 1)),
            )

        if action == 'delete':
            book_id = request.POST.get("book_id")
            Book.objects.filter(id=book_id).delete()

        return redirect('manage-catalouge')
    
    def test_func(self):
        return self.request.user.is_staff
    
class NotificationView(LoginRequiredMixin,UserPassesTestMixin,FormView):
    form_class = NotificationForm
    template_name = 'core/notification.html'
    success_url = reverse_lazy('notification')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_staff

class RequestedBookView(LoginRequiredMixin,UserPassesTestMixin,ListView):
    model=BookRequest
    template_name = 'core/requestedbook.html'
    context_object_name = 'requests'

    def test_func(self):
        return self.request.user.is_staff
    
class deleteRequestedBookView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model=BookRequest
    template_name = 'core/deleterequests.html'
    success_url = reverse_lazy('requestedbooks')
    def test_func(self):
        return self.request.user.is_staff
    
class NotificationSharedView(LoginRequiredMixin,ListView):
    model = Notification
    template_name = 'core/showNotification.html'
    context_object_name = 'notifications'

class FinePaymentView(LoginRequiredMixin, FormView):
    template_name = "core/fine_payment.html"
    form_class = FinePaymentForm
    success_url = reverse_lazy("fine_payment")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        student = Student.objects.get(user=self.request.user)
        form.fields["book"].queryset = student.book.all()
        return form

    def form_valid(self, form):
        student = Student.objects.get(user=self.request.user)
        fine = form.save(commit=False)
        fine.student = student
        fine.paid = True   
        fine.save()
        return super().form_valid(form)

