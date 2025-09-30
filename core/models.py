from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.

class User(AbstractUser):
    class Role_choice(models.TextChoices):
        STUDENT = "STU", "Student"
        FACULTY = "FAC", "Faculty"
        LIBRARIAN = "LIB", "Librarian"
        ADMIN = "ADM", "Admin"
    
    role = models.CharField(max_length=50,choices=Role_choice.choices,default=Role_choice.STUDENT)

    def __str__(self):
        return f"{self.role} - {self.username}"


class Book(models.Model):
    class Category(models.TextChoices):
        SCIENCE = "SCI", "Science"
        ENGINEERING = "ENG", "Engineering"
        LITERATURE = "LIT", "Literature"
        HISTORY = "HIS", "History"
        TECHNOLOGY = "TECH", "Technology"
        OTHER = "OTH", "Other"

    title = models.CharField(max_length=255, verbose_name="Book Title")
    author = models.CharField(max_length=255, verbose_name="Author")
    isbn = models.CharField(max_length=13, unique=True, verbose_name="ISBN")
    category = models.CharField(
        max_length=10,
        choices=Category.choices,
        default=Category.OTHER,
        verbose_name="Category"
    )
    publisher = models.CharField(max_length=255, blank=True, null=True, verbose_name="Publisher")
    published_year = models.PositiveIntegerField(blank=True, null=True, verbose_name="Published Year")

    total_copies = models.PositiveIntegerField(default=1, verbose_name="Total Copies")
    available_copies = models.PositiveIntegerField(default=1, verbose_name="Available Copies")

    added_date = models.DateTimeField(default=timezone.now, verbose_name="Added to Library")

    def __str__(self):
        return f"{self.title} by {self.author} ({self.isbn})"

    @property
    def is_available(self):
        return self.available_copies > 0


class Student(models.Model):
    name = models.CharField(max_length=50,null=False,verbose_name='FULL NAME')
    usn = models.CharField(max_length=50,primary_key=True,verbose_name='USN')
    email = models.EmailField(max_length=254,null=False,verbose_name='EMAIL')
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='studentuser',null=True,blank=True)
    book = models.ManyToManyField(Book, verbose_name='Books',related_name='alloted_books_by_std',blank=True)

    def __str__(self):
        return f"{self.name} ({self.usn})"


    
class Faculty(models.Model):
    name = models.CharField(max_length=50,null=False,verbose_name='FULL NAME')
    id = models.CharField(max_length=50,primary_key=True,verbose_name='ID')
    email = models.EmailField(max_length=254,null=False,verbose_name='EMAIL')
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='facultyuser',null=True,blank=True)
    book = models.ManyToManyField(Book, verbose_name='Books',related_name='alloted_books_by_faculty',blank=True)

    def __str__(self):
        return f"{self.name} ({self.id})"



class Librarian(models.Model):
    name = models.CharField(verbose_name='FULL NAME', max_length=50)
    email = models.CharField(verbose_name='EMAIL', max_length=50)
    user = models.OneToOneField(User, verbose_name='USER',related_name='libuser',on_delete=models.CASCADE,null=True,blank=True)

    def __str__(self):
        return f"{self.name} - Librarian"

@receiver(post_save, sender=Librarian)
def create_librarian_user(sender,instance,created, **kwargs):
    if created and not instance.user:
        user = User.objects.create_user(
            username=instance.email,
            email=instance.email,
            password='123',
            role = User.Role_choice.LIBRARIAN,
        )
        instance.user = user
        instance.save()

class BookRequest(models.Model):
    REQUEST_STATUS = [
        ("PENDING", "Pending"),
        ("REVIEWED", "Reviewed"),
        ("REJECTED", "Rejected"),
    ]
     
    requestedBy = models.ForeignKey(User, verbose_name='RequestedBy', on_delete=models.CASCADE)
    # librarian = models.ForeignKey(Librarian, verbose_name=RequestedTo, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)                  
    author = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)     
    status = models.CharField(max_length=10, choices=REQUEST_STATUS, default="PENDING")
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.requestedBy.role} - {self.requestedBy.username}"
    
    
class Notification(models.Model):
    title = models.CharField(max_length=50,null=False,blank=False,verbose_name='Title')
    message = models.TextField(verbose_name='Message',max_length=1000)
    user = models.ForeignKey(Librarian, verbose_name="User", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class Fine(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="fines"
    )
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="fines"
    )
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    paid = models.BooleanField(default=False)
    payment_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        status = "Paid" if self.paid else "Unpaid"
        return f"Fine: {self.book.title} - {self.amount} ({status})"