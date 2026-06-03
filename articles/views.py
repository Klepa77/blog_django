from django.shortcuts import render, get_object_or_404
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
