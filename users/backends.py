from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend


class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None
        field = 'email__iexact' if '@' in username else 'username__iexact'
        user = User.objects.filter(**{field: username}).order_by('id').first()

        if user is None:
            User().set_password(password)
            return None

        if user.check_password(password)and self.user_can_authenticate(user):
            return user
        return None
