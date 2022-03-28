from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.not_author = User.objects.create_user(username='not_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        Post.objects.create(
            author=cls.author,
            text='Тестовая пост',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        self.authorized_not_author_client = Client()
        self.authorized_not_author_client.force_login(self.not_author)

    def test_urls_uses_correct_template(self):
        url_templates_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for url, template in url_templates_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_url_redirect_anonymous(self):
        url_redirects_names = {
            '/posts/1/edit/': '/auth/login/?next=/posts/1/edit/',
            '/create/': '/auth/login/?next=/create/',
        }
        for url, redirect in url_redirects_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, redirect)

    def test_url_redirect_not_author(self):
        url = '/posts/1/edit/'
        redirect = '/posts/1/'
        response = self.authorized_not_author_client.get(url, follow=True)
        self.assertRedirects(response, redirect)

    def test_url_anonymous(self):
        urls = (
            '/',
            '/group/test-slug/',
            '/profile/auth/',
            '/posts/1/'
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_url_authorized(self):
        urls = (
            '/',
            '/group/test-slug/',
            '/profile/auth/',
            '/posts/1/',
            '/posts/1/edit/',
            '/create/',
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_unexisting_page(self):
        url = '/nonexisting_page'
        clients = (self.authorized_client, self.guest_client)
        for client in clients:
            with self.subTest(client=client):
                response = client.get(url)
                self.assertEqual(response.status_code, 404)
