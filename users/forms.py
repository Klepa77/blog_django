from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

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