from django.contrib import admin
from django.template.defaulttags import register

from .models import Post, Comment, Category

# Register your models here.
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Category)



