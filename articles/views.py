from django.contrib.auth.models import User
from django.contrib.messages.context_processors import messages
from django.core.signals import request_started
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from articles import forms
from articles.models import *
from django.db.models import Q, F, Count
from django.http import HttpResponse, JsonResponse, Http404
from django.core.paginator import Paginator
from .utils import increment_views


# Create your views here.
@login_required(login_url='/users/sign_in')
def home(request):
    page = request.GET.get('page')
    search = request.GET.get('search')
    category = request.GET.get('category')
    tag = request.GET.get('tag')
    sort = request.GET.get('sort')
    author = request.GET.get('author')
    favorite_only = request.GET.get('favorite')
    like_only = request.GET.get('like')
    selected_author = User.objects.filter(
        pk=author).first() if author else None

    own_posts = bool(author) and str(request.user.pk) == author

    posts = (Post.objects.all() if own_posts else
             Post.objects.published).order_by(
        '-date_created')
    hidden_authors = HiddenAuthor.objects.filter(
        user=request.user).values_list('author', flat=True)
    posts = posts.exclude(author__in=hidden_authors)
    posts = posts.filter(title__icontains=search) if search else posts
    posts = posts.filter(category=category) if category else posts
    posts = posts.filter(tags__name=tag) if tag else posts
    posts = posts.filter(author=author) if author else posts
    if favorite_only and request.user.is_authenticated:
        favorite_post_ids = Favorite.objects.filter(
            user=request.user).values_list('post_id', flat=True)
        posts = posts.filter(pk__in=favorite_post_ids)
    posts = posts.filter(likes=request.user) if like_only else posts
    posts = posts.order_by('-date_created') if sort == 'new_first' else posts
    posts = posts.order_by('date_created') if sort == 'old_first' else posts
    posts = posts.annotate(
        comments_count=Count('comment'),
        popular=F('likes') * 5 - F('dislikes') * 5 + F(
            'comments_count') * 15 + F('views')
    ).order_by('popular') if sort == 'popular_first' else posts

    categories = Category.objects.all()
    paginator = Paginator(posts, 3)
    page_object = paginator.get_page(page)
    sort_options = {
        'new_first': 'Сначала новые',
        'old_first': 'Сначала старые',
        'popular_first': 'Сначала популярные',

    }

    return render(request,
                  'home.html',
                  {'posts': page_object,
                   'own_posts': own_posts,
                   'categories': categories,
                   'category': category,
                   'search': search,
                   'sort_options': sort_options.items(),
                   'selected_author': selected_author,

                   })


def post(request, pk):
    post_data = get_object_or_404(Post, pk=pk)
    if not post_data.can_view(request.user):
        raise Http404
    comments = Comment.objects.filter(post=post_data, parent=None)
    is_favorite = post_data.favorite_set.filter(user=request.user).exists() \
        if request.user.is_authenticated else False
    is_hidden_author = HiddenAuthor.objects.filter(user=request.user).exists() \
        if request.user.is_authenticated else False
    increment_views(request, post_data)

    published = {'status': Post.Status.PUBLISHED, }

    try:
        next_post = post_data.get_next_by_date_created(**published)
    except Post.DoesNotExist:
        next_post = None
    try:
        prev_post = post_data.get_previous_by_date_created(**published)
    except Post.DoesNotExist:
        prev_post = None
    return render(request, 'post.html',
                  {'post': post_data, 'next_post': next_post,
                   'prev_post': prev_post, 'comments': comments,
                   'is_favorite': is_favorite})


@login_required(login_url='/users/sign_in')
def post_create(request):
    form = forms.PostForm(request.POST or None, request.FILES)
    if request.method == 'POST' and form.is_valid():
        instance = form.save(commit=False)
        instance.author = request.user

        if request.user.is_staff:
            instance.status = Post.Status.PUBLISHED
        else:
            instance.status = Post.Status.PENDING

        instance.save()
        raw_tags = request.POST.get("tags", "")
        tag_objects = resolve_tags(raw_tags)
        instance.tags.set(tag_objects)
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
        instance = form.save(commit=False)
        if not request.user.is_staff:
            instance.status = Post.Status.PENDING
            instance.moderation_note = ""
        instance.save()
        form.save_m2m()
        if not instance.is_published:
            messages.info(request, 'Изменения отправлены на модерацию')
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


def comment_create(request, post_pk):
    post_data = Post.objects.get(pk=post_pk)
    body = request.POST.get('body')
    parent_id = request.POST.get('parent')

    if request.method == 'POST':
        instance = Comment()
        instance.user = request.user
        instance.post = post_data
        instance.body = body
        if parent_id:
            main_comment = Comment.objects.get(pk=parent_id)
            instance.parent = main_comment
        instance.save()
    return redirect('articles:post', pk=post_pk)


@login_required(login_url='/users/sign_in')
def comment_delete(request, comment_pk):
    comment = Comment.objects.get(pk=comment_pk)
    if comment.user != request.user:
        return redirect('users:forbidden')

    if request.method == "POST":
        comment.delete()
    return redirect('articles:post', pk=comment.post.pk)


def like(request, pk):
    article = Post.objects.get(pk=pk)

    if request.user not in article.likes.all():
        article.likes.add(request.user)
        article.dislikes.remove(request.user)
    else:
        article.likes.remove(request.user)
    return redirect('articles:post', pk=pk)


def dislike(request, pk):
    article = Post.objects.get(pk=pk)

    if request.user not in article.dislikes.all():
        article.dislikes.add(request.user)
        article.likes.remove(request.user)
    else:
        article.dislikes.remove(request.user)

    return redirect('articles:post', pk=pk)


def comment_likes(request, pk):
    comment = Comment.objects.get(pk=pk)
    if request.user not in comment.likes.all():
        comment.likes.add(request.user)
        comment.dislikes.remove(request.user)
    else:
        comment.likes.remove(request.user)
    return redirect('articles:post', pk=comment.post.pk)


def comment_dislikes(request, pk):
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
    tags = list(tags.values_list('name', flat=True)) if search else []
    return JsonResponse({'tags': tags, 'count': len(tags)})


def resolve_tags(raw: str) -> list[Tag]:
    names = [name.strip() for name in raw.split(",") if name.strip()]
    names = list(dict.fromkeys(names))  # убрать дубли, сохранив порядок

    tag_objects = []
    for name in names:
        tag = Tag.objects.filter(name__iexact=name).first()
        if not tag:
            tag = Tag.objects.create(name=name)
        tag_objects.append(tag)

    return tag_objects


@login_required(login_url='/users/sign_in')
def favorite(request, pk):
    article = Post.objects.get(pk=pk)
    favorite_post, created = Favorite.objects.get_or_create(user=request.user,
                                                            post=article)
    if not created:
        favorite_post.delete()

    return redirect('articles:post', pk=pk)


@login_required(login_url='/users/sign_in')
def hide_this_author(request, pk, ):
    author = get_object_or_404(User, id=pk)
    if request.user == author:
        return JsonResponse({'error': 'you cannot hide yourself'})
    obj, created = HiddenAuthor.objects.get_or_create(author=author,
                                                      user=request.user)
    if not created:
        obj.delete()
    return redirect('articles:home')


@login_required(login_url='/users/sign_in')
def show_hidden_authors(request):
    hidden_authors = HiddenAuthor.objects.filter(user=request.user)
    return render(request, 'hidden_authors.html',
                  {'hidden_authors': hidden_authors}, )


def is_moderator(user):
    return user.is_authenticated and user.is_staff


def _back(request):
    next_url = request.POST.get('next')
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={
        request.get_host()}):
        return redirect(next_url)
    return redirect('articles:moderation')




@user_passes_test(is_moderator, login_url='users:sign_in')
def moderation(request):
    posts = (Post.objects.pending()
             .select_related('author', 'category')
             .order_by('date_created'))
    return render(request, 'moderation.html', {'posts': posts})


@require_POST
@user_passes_test(is_moderator, login_url='users:sign_in')
def moderation_approve(request, pk):
    post_data = get_object_or_404(Post, pk=pk)
    post_data.status = Post.Status.PUBLISHED
    post_data.moderation_note = ""
    post_data.moderated_by = request.user
    post_data.moderated_at = timezone.now()
    post_data.save(update_fields=['moderation_note', 'moderated_by',
                                  'moderated_at', 'status'])
    # Вызвать функцию оповещения автора по почте,
    messages.success(request, f'{post_data.title} опубликован')
    return _back(request)

@require_POST
@user_passes_test(is_moderator, login_url='users:sign_in')
def moderation_reject(request, pk):
    post_data = get_object_or_404(Post, pk=pk)
    note = request.POST.get('note').strip()
    if not note:
        messages.error(request,'Укажите причину отказа')
        return _back(request)

    post_data.status = Post.Status.REJECTED
    post_data.moderation_note = note
    post_data.moderated_by = request.user
    post_data.moderated_at = timezone.now()
    post_data.save(update_fields=['moderation_note', 'moderated_by',
                                  'moderated_at', 'status'])
    # Вызвать функцию оповещения автора по почте,
    messages.success(request, f'{post_data.title} отклонен')
    return _back(request)