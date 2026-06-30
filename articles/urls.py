from django.urls import path
from . import views


urlpatterns=[
    path('',views.home,name='home'),
    path('post/<int:pk>',views.post,name='post'),
    path('post_create/',views.post_create,name='post_create'),
    path('post_edit/<int:pk>',views.post_edit,name='post_edit'),
    path('post_delete/<int:pk>',views.post_delete,name='post_delete'),
    path('comment_create/<int:post_pk>',views.comment_create,
         name='comment_create'),
    path('comment_delete/<int:comment_pk>',views.comment_delete,
         name='comment_delete'),
    path('likes/<int:pk>',views.like,name='likes'),
    path('dislikes/<int:pk>',views.dislike,name='dislikes'),




]