from django.contrib import admin
from core.models import User,Student,Faculty,Librarian,Book,BookRequest
# Register your models here.

admin.site.register(User)
admin.site.register(Student)
admin.site.register(Faculty)
admin.site.register(Librarian)
admin.site.register(Book)
admin.site.register(BookRequest)


