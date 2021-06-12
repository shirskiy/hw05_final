from django.test import Client, TestCase
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.names = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html',
        }

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адресов about."""
        for url in self.names.keys():
            response = self.guest_client.get(reverse(url))
            self.assertEqual(response.status_code, 200)

    def test_about_url_uses_correct_template(self):
        """Проверка шаблонов about."""
        for url, template in self.names.items():
            response = self.guest_client.get(reverse(url))
            self.assertTemplateUsed(response, template)
