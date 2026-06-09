from django.urls import path
from . import views


urlpatterns=[
    path('',views.home,name='home'),
    path('post/<int:pk>',views.post,name='post'),
    path('post_create/',views.post_create,name='post_create'),




]