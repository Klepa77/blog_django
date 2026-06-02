from django.shortcuts import render, get_object_or_404
from articles.models import Post
from django.http import HttpResponse, JsonResponse


# Create your views here.

def home(request):
    posts = Post.objects.all()
    return render(request, 'home.html', {'posts': posts})

def post(request,pk):
    post_data = get_object_or_404(Post, pk=pk)
    return render(request, 'post.html', {'post': post_data})