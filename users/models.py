from django.db import models
from django.contrib.auth.models import AbstractUser


class School(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class User(AbstractUser):
    school = models.ForeignKey(School, blank=True, null=True, on_delete=models.SET_NULL)


class UserGroup(models.TextChoices):
    STUDENT = "Student"
    SCHOOL = "School"
