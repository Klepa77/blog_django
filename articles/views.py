from django.shortcuts import render, get_object_or_404, redirect

from articles import forms
from articles.models import Post
from django.http import HttpResponse, JsonResponse


# Create your views here.

def home(request):
    posts = Post.objects.all()
    return render(request, 'home.html', {'posts': posts})

def post(request,pk):
    post_data = get_object_or_404(Post, pk=pk)
    try:
        next_post = post_data.get_next_by_date_created()
    except Post.DoesNotExist:
        next_post = None
    try:
        prev_post = post_data.get_previous_by_date_created()
    except Post.DoesNotExist:
        prev_post = None
    return render(request, 'post.html', {'post': post_data, 'next_post': next_post, 'prev_post': prev_post})

def post_create(request):
   form = forms.PostForm(request.POST or None, request.FILES)
   if request.method == 'POST' and form.is_valid():
       form.save()
       return redirect('articles:home')
   return render(request, 'post_create.html', {'form': form})