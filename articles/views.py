from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from articles import forms
from articles.models import Post, Comment, Category, Tag
from django .db.models import Q
from django.http import HttpResponse, JsonResponse


# Create your views here.

def home(request):
    search = request.GET.get('search')
    category = request.GET.get('category')
    posts = Post.objects.all().order_by('-date_created')
    posts = posts.filter(title__icontains=search) if search else posts
    posts = posts.filter(category=category) if category else posts
    categories=Category.objects.all()

    return render(request, 'home.html', {'posts': posts,
                                         'categories':categories,
                                         'category':category,'search':search})


def post(request, pk):
    post_data = get_object_or_404(Post, pk=pk)
    comments = Comment.objects.filter(post=post_data)
    try:
        next_post = post_data.get_next_by_date_created()
    except Post.DoesNotExist:
        next_post = None
    try:
        prev_post = post_data.get_previous_by_date_created()
    except Post.DoesNotExist:
        prev_post = None
    return render(request, 'post.html',
                  {'post': post_data, 'next_post': next_post,
                   'prev_post': prev_post,'comments': comments})


@login_required(login_url='/users/sign_in')
def post_create(request):
    form = forms.PostForm(request.POST or None, request.FILES)
    if request.method == 'POST' and form.is_valid():
        instance = form.save(commit=False)
        instance.author = request.user
        instance.save()
        return redirect('articles:home')
    return render(request, 'post_create.html', {'form': form})


@login_required(login_url='/users/sign_in')
def post_edit(request, pk):
    article = Post.objects.get(pk=pk)
    form = forms.PostForm(request.POST or None, request.FILES or None,
                          instance=article)
    if article.author != request.user:
        return redirect('users:forbidden')

    if form.is_valid():
        form.save()
        return redirect('articles:home')
    return render(
        request,
        'post_edit.html',
        {'form': form, 'article': article})


@login_required(login_url='/users/sign_in')
def post_delete(request, pk):
    article = Post.objects.get(pk=pk)

    if article.author != request.user:
        return redirect('users:forbidden')

    if request.method == "POST":
        article.delete()
    return redirect('articles:home')


def comment_create(request,post_pk):
    post_data = Post.objects.get(pk=post_pk)
    body = request.POST.get('body')

    if request.method == 'POST':
        instance = Comment()
        instance.user = request.user
        instance.post = post_data
        instance.body = body
        instance.save()
    return redirect('articles:post', pk=post_pk)

@login_required(login_url='/users/sign_in')
def comment_delete(request,comment_pk):
    comment = Comment.objects.get(pk=comment_pk)
    if comment.user != request.user:
        return redirect('users:forbidden')

    if request.method == "POST":
        comment.delete()
    return redirect('articles:post', pk=comment.post.pk)

def like(request,pk):
    article = Post.objects.get(pk=pk)

    if request.user not in article.likes.all():
        article.likes.add(request.user)
        article.dislikes.remove(request.user)
    else:
        article.likes.remove(request.user)
    return redirect('articles:post', pk=pk)

def dislike(request,pk):
    article = Post.objects.get(pk=pk)

    if request.user not in article.dislikes.all():
        article.dislikes.add(request.user)
        article.likes.remove(request.user)
    else:
        article.dislikes.remove(request.user)

    return redirect('articles:post', pk=pk)


def comment_likes(request,pk):
    comment = Comment.objects.get(pk=pk)
    if request.user not in comment.likes.all():
        comment.likes.add(request.user)
        comment.dislikes.remove(request.user)
    else:
        comment.likes.remove(request.user)
    return redirect('articles:post', pk=comment.post.pk)

def comment_dislikes(request,pk):
    comment = Comment.objects.get(pk=pk)
    if request.user not in comment.dislikes.all():
        comment.dislikes.add(request.user)
        comment.likes.remove(request.user)
    else:
        comment.dislikes.remove(request.user)
    return redirect('articles:post', pk=comment.post.pk)


def fetch_tags(request):
    search = request.GET.get('search')
    tags = Tag.objects.filter(name__icontains=search)
    tags = list(tags.values_list('name', flat=True))if search else []
    return JsonResponse({'tags': tags, 'count': len(tags)})