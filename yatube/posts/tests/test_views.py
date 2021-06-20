from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Group, Post, User


class TestViewsContext(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='test grp title123',
            slug='test_grp_slug',
            description='test grp descr'
        )
        cls.author = User.objects.create_user(username='Author')
        cls.user = User.objects.create_user(username='Random_user')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Some text to test',
            author=TestViewsContext.author,
            group=TestViewsContext.group,
            image=uploaded,
        )
        cls.wrong_group = Group.objects.create(
            title='wrong grp title123',
            slug='wrong_grp_slug',
            description='wrong grp descr'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)  # логинемся как юзер
        self.reverse_list_with_no_pagese = [
            reverse('post', kwargs={'username': TestViewsContext.author,
                                    'post_id': TestViewsContext.post.id})
        ]
        self.reverse_list_with_pages = [
            reverse('index'),
            reverse('group', kwargs={'slug': TestViewsContext.group.slug}),
            reverse('profile', kwargs={'username': TestViewsContext.author}),
            reverse('follow_index')
        ]
        # фолловим юзером автора
        Follow.objects.create(user=TestViewsContext.user,
                              author=TestViewsContext.author)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'index.html': reverse('index'),
            'group.html': reverse(
                'group', kwargs={'slug': TestViewsContext.group.slug}
            ),
            'new.html': reverse('new_post')

        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_and_group_shows_correct_context(self):
        """На главной на странице, группы, пользователя, follow
        выводится правильный context"""
        for url in self.reverse_list_with_pages:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                response_post = response.context['page'][0]
                self.assertEqual(TestViewsContext.post, response_post)

    def test_post_page_shows_correct_context(self):
        """На странице поста выводится правильный context"""
        response = self.guest_client.get(self.reverse_list_with_no_pagese[0])
        response_post = response.context['post']
        self.assertEqual(TestViewsContext.post, response_post)

    def test_new_group_post_dont_append_at_wrong_group(self):
        """Групповой пост не отоброжается в другой группе"""
        response = self.authorized_client.get(
            reverse('group',
                    kwargs={'slug': TestViewsContext.wrong_group.slug}))
        self.assertNotContains(response, TestViewsContext.post.text)

    def test_new_post_for_followers(self):
        """Новая запись пользователя появляется
        в ленте тех, кто на него подписан."""
        Post.objects.create(
            text='Текст нового поста',
            author=TestViewsContext.author,
        )
        response = self.authorized_client.get(reverse('follow_index'))
        response_post_text = response.context['page'][0].text
        self.assertEqual(response_post_text, 'Текст нового поста')

    def test_unfollow_cant_see_post(self):
        """Записи не появляются у тех, кто не подписан"""
        Follow.objects.filter(user=TestViewsContext.user,
                              author=TestViewsContext.author).delete()
        response = self.authorized_client.get(reverse('follow_index'))
        self.assertNotContains(response, TestViewsContext.post.text)

    def test_edit_page_context(self):
        """Проверка контекста на странице редактирования"""
        self.authorized_client.force_login(self.author)  # логинемся как автор
        response = self.authorized_client.get(
            reverse(
                'post_edit',
                kwargs={
                    'username': TestViewsContext.author,
                    'post_id': TestViewsContext.post.id
                }
            )
        )
        form = response.context['form']
        post_text = form['text'].value()
        self.assertEqual(TestViewsContext.post.text, post_text)


class TestPaginator(TestCase):
    @ classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='TestUser')
        i = 1
        while i < 14:
            cls.post = Post.objects.create(
                text=f'test text №{i}',
                author=TestPaginator.user,
            )
            i += 1

    def setUp(self):
        self.client = Client()

    def test_first_page_contains_10_records(self):
        """На главной странице отоброжается 10 записей"""
        response = self.client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_contains_3_records(self):
        """На второй странице отоброжается 3 записи"""
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)


class TestCashe(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Author')
        cls.post = Post.objects.create(
            text='test text 1',
            author=TestCashe.author
        )
        cls.guest_client = Client()

    def test_cache_guest(self):
        """Проверка работы кэша"""
        response = TestCashe.guest_client.get(reverse('index'))
        cached_response_content = response.content
        Post.objects.create(text='test text 2', author=TestCashe.author)
        response = TestCashe.guest_client.get(reverse('index'))
        cache.clear()
        self.assertNotEqual(cached_response_content, response.content)


class TestFollow(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Author')
        cls.user = User.objects.create_user(username='User')
        cls.post = Post.objects.create(
            text='To followers',
            author=TestFollow.author
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(TestFollow.user)

    def test_follow(self):
        followers_count = Follow.objects.filter(
            author=TestFollow.author
        ).count()
        following_count = Follow.objects.filter(
            user=TestFollow.user).count()
        self.authorized_client.get(
            reverse('profile_follow',
                    kwargs={'username': TestFollow.author})
        )
        # Проверяем, что число фолловеров увеличилось на 1
        self.assertEqual(followers_count + 1,
                         Follow.objects.filter(
                             author=TestFollow.author).count()
                         )
        # Проверяем, что число подписок увеличилось на 1
        self.assertEqual(following_count + 1,
                         Follow.objects.filter(
                             user=TestFollow.user).count()
                         )
        # Проверяем, что подписка создалась
        self.assertTrue(Follow.objects.filter(
            user=TestFollow.user, author=TestFollow.author).exists()
        )

    def test_unfollow(self):
        Follow.objects.create(user=TestFollow.user,
                              author=TestFollow.author)
        followers_count = Follow.objects.filter(
            author=TestFollow.author
        ).count()
        following_count = Follow.objects.filter(
            user=TestFollow.user
        ).count()
        self.authorized_client.get(
            reverse('profile_unfollow',
                    kwargs={'username': TestFollow.author})
        )
        # Проверяем, что число фолловеров уменьшилось
        self.assertEqual(followers_count - 1,
                         Follow.objects.filter(
                             author=TestFollow.author).count()
                         )
        # Проверяем, что чилсо подписок уменьшилось
        self.assertEqual(following_count - 1,
                         Follow.objects.filter(user=TestFollow.user).count()
                         )
        self.assertFalse(Follow.objects.filter(
            user=TestFollow.user, author=TestFollow.author).exists()
        )

    def test_cant_follow_yorself(self):
        self.authorized_client.force_login(TestFollow.author)
        followers_count = Follow.objects.filter(
            author=TestFollow.author
        ).count()
        self.authorized_client.get(
            reverse('profile_follow',
                    kwargs={'username': TestFollow.author}
                    )
        )
        # Проверяем, что число подписок не изменилось
        self.assertEqual(followers_count,
                         Follow.objects.filter(
                             author=TestFollow.author).count()
                         )
        self.assertFalse(Follow.objects.filter(
            user=TestFollow.author, author=TestFollow.author).exists()
        )
