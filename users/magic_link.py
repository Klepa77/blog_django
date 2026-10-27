import re

from django.conf import settings
from django.contrib.auth.models import User
from django.core import signing
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from django.urls import reverse

SALT = 'users.magic-login'


def _last_login_ts(user):
    return int(
        user.last_login.timestamp()) if user and user.last_login else None


def make_token(email):
    user = User.objects.filter(email__iexact=email).order_by('id').first()
    return signing.dumps({'e': email, 'll': _last_login_ts(user)}, salt=SALT)


def send_magic_link(request, email):
    link = request.build_absolute_uri(
        reverse('users:magic_login', kwargs={'token': make_token(email)})
    )
    context = {
        'link': link,
        'minutes': settings.MAGIC_LINK_MAX_AGE // 60,
    }
    send_mail(
        subject='Вход на сайт',
        message=render_to_string('emails/magic_link.txt', context),
        html_message=render_to_string('emails/magic_link.html', context),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )


class MagicLinkError(Exception):
    pass


def _unique_username(email):
    base = re.sub(r'[^\w.+-]', '', email.split('@')[0])[:140] or 'user'
    username, i = base, 1
    while User.objects.filter(username__iexact=username).exists():
        i += 1
        username = f"{base}{i}"
    return username


@transaction.atomic
def user_from_token(token):
    try:
        data = signing.loads(token, salt=SALT,
                             max_age=settings.MAGIC_LINK_MAX_AGE)

    except signing.SignatureExpired:
        raise MagicLinkError('Срок действия ссылки истёк. Запросите новую')

    except signing.BadSignature:
        raise MagicLinkError('Ссылка не действительна')

    email = data['e']
    user = User.objects.select_for_update().filter(
        email__iexact=email).order_by('id').first()
    if _last_login_ts(user) != data['ll']:
        raise MagicLinkError('Ссылка уже использована, Запросите новую')
    if user is None:
        user = User(username=_unique_username(email), email=email)
        user.set_unusable_password()
        user.save()
        return user, True
    if not user.is_active:
        user.is_active = True
        user.save(update_fields=['is_active'])
    return user, False
