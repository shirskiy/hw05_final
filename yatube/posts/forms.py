from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        labels = {
            'text': ('Текст поста'),
            'group': ('Группа')
        }

        error_messages = {
            'text': {
                'required': ('Текст поста - обязательное поле.'),
            },
        }
        help_texts = {
            'text': ('Напишите Ваш пост.'),
            'group': ('Выберите группу (необязательно).'),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {
            'text': ('Текст комментария')
        }
        error_messages = {
            'text': {
                'required': ('Текст комментария - обязательное поле.')
            }
        }
        help_texts = {
            'text': ('Напишите Ваш комментарий')
        }
        widgets = {'text': forms.Textarea({'rows': 3})}
