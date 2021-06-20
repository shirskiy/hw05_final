from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class UrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Author')
        cls.group = Group.objects.create(
            title='test grp title',
            slug='test_grp_slug',
            description='test grp descr'
        )
        cls.post = Post.objects.create(
            text='test urls',
            pub_date='14 Мая 2021',
            author=cls.author,
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(UrlTests.author)
        self.not_author = User.objects.create_user(username='Not_Author')
        self.not_author_client = Client()
        self.not_author_client.force_login(self.not_author)
        self.reverse_list_for_guest = [
            # Главная страница
            reverse('index'),
            # Страница группы test_grp_slug
            reverse('group', kwargs={'slug': UrlTests.group.slug}),
            # Страница пользователя TestUser
            reverse('profile', kwargs={'username': UrlTests.author}),
            # Страница поста
            reverse('post', kwargs={
                    'username': UrlTests.author, 'post_id': UrlTests.post.id})
        ]
        self.reverse_list_for_user = [
            # Страница создания поста
            reverse('new_post'),
        ]
        self.reverse_list_for_author = [
            # Страница редактирования поста
            reverse('post_edit',
                    kwargs={
                        'username': UrlTests.author,
                        'post_id': UrlTests.post.id
                    }
                    )
        ]

    def test_guest(self):
        """Проверьте доступность страниц проекта Yatube гостем."""
        for url in self.reverse_list_for_guest:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code, 200,
                    f'У гостя нет доступа к {url}'
                )

    def test_no_access_guest(self):
        """У гостя нет доступа к новому посту, редактированию поста,
        комментированию поста"""
        for url in (self.reverse_list_for_user + self.reverse_list_for_author):
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code, 302,
                    f'У гостя есть доступ к {url}'
                )

    def test_not_author(self):
        """Проверьте доступность страниц проекта Yatube юзером."""
        for url in self.reverse_list_for_user:
            with self.subTest(url=url):
                response = self.not_author_client.get(url)
                self.assertEqual(
                    response.status_code, 200,
                    f'У авторизованного пользователя — '
                    f'не автора поста нет доступа к {url}'
                )

    def test_no_access_user(self):
        """У не автора нет доступа к редактированию поста"""
        for url in (self.reverse_list_for_author):
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code, 302,
                    f'У юзера есть доступ к {url}'
                )

    def test_author(self):
        """Проверьте доступность страниц проекта Yatube автором поста."""
        for url in self.reverse_list_for_author:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(
                    response.status_code, 200,
                    f'У автора поста нет доступа к {url}'
                )

    def test_guest_redirects_to_loggin(self):
        """Страница по адресу /new перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/new/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/new/',
            msg_prefix='Редирект не сработал'
        )

    def test_urls_uses_correct_template(self):
        """проверка шаблонов"""
        templates_url_names = {
            'index.html': reverse('index'),
            'group.html': reverse(
                'group', kwargs={'slug': UrlTests.group.slug}
            ),
            'new.html': reverse(
                'post_edit', kwargs={
                    'username': UrlTests.author,
                    'post_id': UrlTests.post.id
                }
            )
        }
        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.author_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_not_author_edit_redirects_to_post(self):
        """Страница /<username>/<post_id>/edit/
        редиректит не автора на просмотр поста"""
        response = self.not_author_client.get(
            f'/{UrlTests.author}/{UrlTests.post.id}/edit/',
            follow=True
        )
        self.assertRedirects(
            response, f'/{UrlTests.author}/{UrlTests.post.id}/',
            msg_prefix='Редирект не сработал'
        )
