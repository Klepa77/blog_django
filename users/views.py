from django.shortcuts import render,redirect
from django. contrib.auth import login,logout
from .forms import SignUpForm,SignInForm
# Create your views here.

def sign_up(request):
    form = SignUpForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        return redirect('user:sign_in')
    return render(request, 'sign_up.html', {'form': form})

def sign_in(request):
    form = SignInForm(data = request.POST or None)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('articles:home')
    return render(request, 'sign_in.html', {'form': form})


def sign_out(request):
    logout(request)
    return redirect('users:sign_in')

def forbidden(request):
    return render(request, '403.html')