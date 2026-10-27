from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from django import forms


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
        fields = ("username","password",)

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
        return  self.cleaned_data.get('email').strip().lower()

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