import re

from django.contrib.auth.models import User
from django.db import models
from django.utils.html import strip_tags


class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=Post.Status.PUBLISHED)

    def pending(self):
        return self.filter(status=Post.Status.PENDING)


class Post(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'На модерации'
        PUBLISHED = 'published', 'Опубликовано'
        REJECTED = 'rejected', 'Отклонен'

    title = models.CharField(max_length=255)
    text = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to="posts",
                              blank=True)
    likes = models.ManyToManyField(User, related_name='likes', blank=True)
    dislikes = models.ManyToManyField(User, related_name='dislikes',
                                      blank=True)
    category = models.ForeignKey('articles.Category', null=True,
                                 on_delete=models.CASCADE)
    tags = models.ManyToManyField('articles.Tag', related_name='tags',
                                  blank=True)
    views = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=Status.choices,
                              default=Status.PENDING, db_index=True)
    moderation_note = models.TextField(blank=True)
    moderated_by = models.ForeignKey(User, on_delete=models.CASCADE,
                                     related_name="posts")
    moderated_at = models.DateTimeField(auto_now_add=True)
    objects = PostQuerySet.as_manager()

    @property
    def reading_time(self):
        words_per_minute = 200
        text = strip_tags(self.text)
        words_count = len(re.findall(r'\w+', text))
        return max(1, round(words_count / words_per_minute))

    @property
    def is_published(self):
        return self.status == Post.Status.PUBLISHED

    def can_view(self, user):
        return (self.is_published or user.is_staff or (user.is_authenticated
                                                       and
                                                       user.pk == self.author_id))

    def __str__(self):
        return self.title

    def snippet(self):
        return self.text[:20] + "... read more"


class Person(models.Model):
    name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    age = models.IntegerField()

    def __str__(self):
        return f"{self.name} {self.last_name}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='comment_likes')
    dislikes = models.ManyToManyField(User, related_name='comment_islikes')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True,
                               blank=True, related_name='reply')
    first_comment = models.ForeignKey('self', on_delete=models.CASCADE,
                                      null=True, related_name='main_comment')

    def __str__(self):
        return f"{self.post}-{self.body[:5]}"


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}-{self.post}"

    class Meta:
        unique_together = ('user', 'post')


class HiddenAuthor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='hidden_authors')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='hidden_by')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'author'],
                                               name='unique_author'),
                       models.CheckConstraint(check=~models.Q(user=models.F(
                           'author')), name='cannot_hide_self')]

    def __str__(self):
        return self.name
