from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class TestModels(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='test grp title',
            slug='test_grp_slug',
            description='test grp descr'
        )

    def setUp(self):
        self.user = User.objects.create_user(username='TestAuthor')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            text='Тестовый текст который будет редактироваться.',
            author=self.user,
            pub_date='14 Апр 2021',
            group=TestModels.group
        )

    def test_create_post(self):
        """Валидная форма создает пост"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'текст нового поста',
            'group': TestModels.group.id,
        }
        resp = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(resp, reverse('index'))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), post_count + 1)
        # Проверяем что запись создалась
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group_id=form_data['group'],
            ).exists()
        )

    def test_post_edit_changed_post(self):
        new_form_data = {
            'text': 'измененный текст поста'
        }
        resp = self.authorized_client.post(
            reverse('post_edit',
                    kwargs={
                        'username': self.user.username,
                        'post_id': self.post.id
                    }
                    ),
            data=new_form_data,
            follow=True
        )
        # Проверяем redirect
        self.assertRedirects(resp,
                             reverse('post',
                                     kwargs={'username': self.user.username,
                                             'post_id': self.post.id
                                             }
                                     )
                             )
        # Проверяем что, измененный пост есть
        self.assertTrue(
            Post.objects.filter(
                text=new_form_data['text']
            ).exists()
        )
