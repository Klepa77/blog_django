from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class GithubAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='github_account')
    github_id = models.BigIntegerField(unique=True)
    login = models.CharField(max_length=120)
    avatar_url = models.URLField(blank=True)

    def __str__(self):
        return self.user.username


def avatar_upload_to(instance, filename):
    return f"avatars/{instance.user_id}/{filename}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='profile')
    avatar = models.ImageField(blank=True, upload_to=avatar_upload_to)
    bio = models.TextField(blank=True, max_length=500)

    def __str__(self):
        return self.user.username
