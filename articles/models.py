from django.contrib.auth.models import User
from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg',upload_to="posts",
                              blank=True)


    def __str__(self):
        return self.title

    def snippet(self):
        return self.text[:20] + "... read more"

class Person(models.Model):
    name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    age = models.IntegerField()

    def __str__(self):
        return f"{self.name} {self.last_name}"

