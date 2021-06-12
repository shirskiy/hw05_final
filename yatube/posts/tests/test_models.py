from django.test import TestCase

from ..models import Group, Post, User


class TestModels(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='test grp title',
            slug='test grp slug',
            description='test grp descr'
        )
        cls.post = Post.objects.create(
            text='test_text0123456 пробуем больше 15 символов',
            author=User.objects.create(username='TestUser'),
            group=cls.group
        )

    def test_Post_text(self):
        """правильность отображения __str__ для Post"""
        post = TestModels.post
        text = post.text
        self.assertEqual(str(post), text[:15])

    def test_Group_title(self):
        """правильность отображения __str__ для Group"""
        group = TestModels.group
        title = str(group)
        self.assertEqual(title, group.title)
