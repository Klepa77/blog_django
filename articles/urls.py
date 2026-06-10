from django.urls import path
from . import views


urlpatterns=[
    path('',views.home,name='home'),
    path('post/<int:pk>',views.post,name='post'),
    path('post_create/',views.post_create,name='post_create'),
    path('post_edit/<int:pk>',views.post_edit,name='post_edit'),
    path('post_delete/<int:pk>',views.post_delete,name='post_delete'),




]