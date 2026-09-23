from django.db.models import F
from .models import  Post


def increment_views(request,post):
    viewed_key = f'viewed_post_{post.pk}'
    if not request.session.get(viewed_key, False):
        Post.objects.filter(pk=post.pk).update(views=F('views') + 1)
        request.session[viewed_key] = True
