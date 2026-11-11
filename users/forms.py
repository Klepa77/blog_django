from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, \
    SetPasswordForm, PasswordResetForm
from django.contrib.auth.models import User
from django import forms

from .models import Profile


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__exact=email).exists():
            raise forms.ValidationError("Пользователь с такой почтой уже "
                                        "зарегистрирован")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        user.is_active = False
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": """
                w-full bg-slate-900/60 border border-white/10
                rounded-xl px-4 py-3 text-slate-100
                placeholder-slate-500
                focus:outline-none focus:border-indigo-500
                """,
            })


class SignInForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ("username", "password",)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            user = (
                    User.objects.filter(email__iexact=username).first()
                    or User.objects.filter(username__iexact=username).first()
            )

            if user and not user.is_active and user.check_password(password):
                self.inactive_user = user
                raise forms.ValidationError('Аккаунт не подтвержден, '
                                            'проверьте почту')
        return super().clean()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": """
                w-full bg-slate-900/60 border border-white/10
                rounded-xl px-4 py-3 text-slate-100
                placeholder-slate-500
                focus:outline-none focus:border-indigo-500
                """,
            })


class ResendActivationForm(forms.Form):
    email = forms.EmailField(label='email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": """
                   w-full bg-slate-900/60 border border-white/10
                   rounded-xl px-4 py-3 text-slate-100
                   placeholder-slate-500
                   focus:outline-none focus:border-indigo-500
                   """,
            })


styles = """w-full bg-slate-900/60 border border-white/10
            rounded-xl px-4 py-3 text-slate-100
            placeholder-slate-500
            focus:outline-none focus:border-indigo-500"""


class MagicLinkForm(forms.Form):
    email = forms.EmailField(
        label='email',
        widget=forms.EmailInput(attrs={
            'autofocus': True,
            'autocomplete': 'email',
            'placeholder': 'you@example.com',
        })
    )

    def clean_email(self):
        return self.cleaned_data.get('email').strip().lower()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                "class": styles,
            })


class ResetPasswordForm(PasswordResetForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = 'Email'
        self.fields['email'].widget.attrs.update({
            'autofocus': True,
            'class': styles,
            'placeholder': 'you@example.com',
        })

    def get_users(self, email):
        return User.objects.filter(email__iexact=email)


class NewPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].label = 'Новый пароль'
        self.fields['new_password2'].label = 'Повторите пароль'
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': styles,
            })

    def save(self, commit=True):
        self.user.is_active = True
        return super().save(commit)


AVATAR_MAX_MB = 2
AVATAR_SIZE = 256


class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',)
        labels = {
            'username': 'Логин',
            'first_name': 'Имя',
            'last_name': 'Фамилия'
        }
        help_texts = {
            'username': 'Буквы,цифры и символы @ . + - _ ',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                "class": styles,
            })

    def clean_username(self):
        username = self.cleaned_data.get('username')
        is_taken = (User.objects.filter(username__iexact=username).exclude(
            pk=self.instance.pk).exists())
        if is_taken:
            raise forms.ValidationError('Этот логин уже занят')
        return username


class ProfileForm(forms.ModelForm):
    remove_avatar = forms.BooleanField(required=False, label='Удалить аватар')

    class Meta:
        model = Profile
        fields = ('avatar', 'bio')
        labels = {
            'avatar': 'Аватар',
            'bio': 'О себе',

        }
        widgets = {
            'avatar': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'hidden',
            }),
            'bio': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Пару слов о себе'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bio'].widget.attrs.update({
            'class': styles,
        })

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and avatar != self.instance.avatar:
            if avatar.size > AVATAR_MAX_MB * 1024 * 1024:
                raise forms.ValidationError(
                    f"Файл больше {AVATAR_MAX_MB} MB"
                )
        return avatar

    def save(self, commit=True):
        profile = super().save(commit=False)
        old = Profile.objects.filter(pk=profile.pk).values_list('avatar',
                                                                flat=True).first()
        if self.cleaned_data.get('remove_avatar'):
            profile.avatar = None
        elif 'avatar' in self.changed_data and profile.avatar:
            profile.avatar = _square_thumbnail(profile.avatar)
        if commit:
            profile.save()
            if old and old != (profile.avatar.name if profile.avatar else ''):
                profile.avatar.storage.delete(old)
        return profile


def _square_thumbnail(uploaded):
    from io import BytesIO
    from django.core.files.uploadedfile import InMemoryUploadedFile
    from PIL import Image, ImageOps

    img = Image.open(uploaded)
    img = ImageOps.exif_transpose(img).convert('RGB')
    img = ImageOps.fit(img, (AVATAR_SIZE, AVATAR_SIZE), Image.LANCZOS)

    buf = BytesIO()
    img.save(buf, format='JPEG', quality=88)
    name = uploaded.name.rsplit('.', 1)[0] + '.jpg'
    return InMemoryUploadedFile(buf, 'avatar', name, 'image/jpeg',
                                buf.getbuffer().nbytes, None)
