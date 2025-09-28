from core.models import BookRequest,User
from django import forms
class LoginForm(forms.Form):
  username = forms.CharField(required=True)
  password = forms.CharField(required=True)


class RequestBookForm(forms.ModelForm):
  class Meta:
    model = BookRequest
    fields = ['title','author','description']

class UserRegistrationForm(forms.ModelForm):
  usn = forms.CharField(required=False)      # for students
  faculty_id = forms.CharField(required=False)  # for faculty
  class Meta:
    model = User
    fields = ['username', 'first_name', 'last_name', 'password', 'role']