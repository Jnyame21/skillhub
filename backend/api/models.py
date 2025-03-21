from django.db import models
from django.contrib.auth.models import User

def get_student_folder(instance):
    return f"{instance.user.username}/"

class Student(models.Model):
    user = models.OneToOneField(User, verbose_name="User", on_delete=models.CASCADE, blank=False)
    phone_number = models.CharField(max_length=15, verbose_name="Phone number", blank=True, null=True)
    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name="Gender", blank=True, null=True)
    school = models.CharField(max_length=255, verbose_name="School", blank=True, null=True)
    program = models.CharField(max_length=255, verbose_name="Program of Study", blank=True, null=True)
    img = models.ImageField(upload_to=get_student_folder, verbose_name="Image", max_length=255, blank=True, null=True)
    current_year = models.PositiveIntegerField(verbose_name="Year of Study", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Workshop(models.Model):
    title = models.CharField(max_length=255, verbose_name="Title", blank=False, null=True)
    description = models.TextField(verbose_name="Title", blank=False, null=True)
    date = models.DateField(verbose_name="Date", blank=False, null=True)
    start_time = models.TimeField(verbose_name="Start Time", blank=False, null=True)
    end_time = models.TimeField(verbose_name="End Time", blank=False, null=True)
    location = models.CharField(max_length=255, verbose_name="Location", blank=False, null=True)
    max_participants = models.PositiveIntegerField(verbose_name="Maximum number of participants", blank=True, null=True)
    deadline = models.DateField(verbose_name="Deadline for registration", blank=False, null=True)
    students = models.ManyToManyField(Student, verbose_name= 'Students', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
