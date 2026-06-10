from django import forms
from .models import *

class PostForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-slate-800 text-slate-100 border border-white/10 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-indigo-500 transition-colors',
            'placeholder': 'Заголовок статьи'
        }),
        label='Заголовок'
    )
    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full bg-slate-800 text-slate-100 border border-white/10 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-indigo-500 transition-colors resize-none',
            'rows': '10',
            'placeholder': 'Текст статьи...'
        }),
        label='Текст поста'
    )

    image = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'w-full bg-slate-800 text-slate-100 border border-white/10 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-indigo-500 transition-colors file:mr-4 file:py-1 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-500'
        }),
        label='Изображение',
        required=False # Сделайте True, если картинка обязательна
    )

    class Meta:
        model = Post
        fields = ['title', 'text', 'image']
