from django.contrib import admin
from django.template.defaulttags import register

from. models import Post

# Register your models here.
admin.site.register(Post)

