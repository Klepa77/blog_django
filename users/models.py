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
