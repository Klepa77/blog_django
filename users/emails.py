from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.conf import settings
from django.template.loader import render_to_string


def send_activation_email(request, user):
    try:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        link = request.build_absolute_uri(
            reverse('users:activate', kwargs={'uidb64': uid, 'token': token})
        )
        ctx = {'user': user,
               'link': link,
               'hours': settings.PASSWORD_RESET_TIMEOUT // 3600
               }
        send_mail(
            subject='Подтверждение регистрации ',
            message=render_to_string('emails/activation.txt', ctx),
            html_message=render_to_string('emails/activation.html', ctx),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
    except Exception as e:
        print(e)