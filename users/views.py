from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .forms import SignUpForm, SignInForm, ResendActivationForm
from .emails import send_activation_email

# Create your views here.
AUTH_BACKEND = 'django.contrib.auth.backends.ModelBackend'


def sign_up(request):
    form = SignUpForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        send_activation_email(request, user)
        return redirect('users:sign_in')
    return render(request, 'sign_up.html', {'form': form})


def sign_in(request):
    form = SignInForm(data=request.POST or None)
    if form.is_valid():
        user = form.get_user()
        login(request, user, backend=AUTH_BACKEND)
        return redirect('articles:home')
    return render(request, 'sign_in.html', {'form': form})


def sign_out(request):
    logout(request)
    return redirect('users:sign_in')


def forbidden(request):
    return render(request, '403.html')


def activate(request, uidb64, token):
    try:
        user = User.objects.get(pk=force_str(urlsafe_base64_decode(uidb64)))
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, 'Ссылка не действительна или устарела. '
                                'Запросите новую')
        return redirect('users:resend_activation')
    if not user.is_active:
        user.is_active = True
        user.save(update_fields=['is_active'])

    login(request, user, backend=AUTH_BACKEND)
    messages.success(request, 'email успешно подтвержден')
    return redirect('articles:home')


def resend_activation(request):
    form = ResendActivationForm(request.POST or None)
    if form.is_valid():
        user = User.objects.filter(email__iexact=form.cleaned_data['email'],
                                   is_active=False).first()
        if user:
            send_activation_email(request, user)
        return render(request, 'check_email.html',
                      {'email': form.cleaned_data['email']})
    return render(request, 'resend_activation.html', {'form': form})