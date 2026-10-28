from django.urls import path
from . import views

urlpatterns = [
    path('sign_up/', views.sign_up, name='sign_up'),
    path('sign_in/', views.sign_in, name='sign_in'),
    path('sign_out/', views.sign_out, name='sign_out'),
    path('403/', views.forbidden, name='forbidden'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('activate/resent', views.resend_activation, name='resend_activation'),
    path('magic/', views.magic_link_request, name='magic_link'),
    path('magic/<str:token>', views.magic_login, name='magic_login'),
    path('password/reset', views.password_reset, name='password_reset'),
    path('password/reset/done', views.password_reset_done,
         name='password_reset_done'),
    path('password/reset/<uidb64>/<token>', views.password_reset_confirm,
         name='password_reset_confirm'),
]
