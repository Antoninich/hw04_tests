from django.test import Client, TestCase
from http import HTTPStatus

from posts.models import Group, Post, User

AUTHOR = 'auth'
GROUP_DESCRIPTION = 'Тестовое описание'
GROUP_SLUG = 'test-slug'
GROUP_TITLE = 'Тестовая группа'
NOT_AUTHOR = 'not_author'
POST_ID = '1'
POST_TEXT = 'Тестовая пост'
TEMPLATES_INDEX = 'posts/index.html'
TEMPLATES_GROUP = 'posts/group_list.html'
TEMPLATES_POST_CREATE = 'posts/create_post.html'
TEMPLATES_POST_DETAIL = 'posts/post_detail.html'
TEMPLATES_PROFILE = 'posts/profile.html'
URL_INDEX = '/'
URL_GROUP = URL_INDEX + 'group/' + GROUP_SLUG + '/'
URL_NONEXISTENT = URL_INDEX + 'nonexisting_page'
URL_POST_CREATE = URL_INDEX + 'create/'
URL_POST_DETAIL = URL_INDEX + 'posts/' + POST_ID + '/'
URL_POST_EDIT = URL_POST_DETAIL + 'edit/'
URL_PROFILE = URL_INDEX + 'profile/' + AUTHOR + '/'
URL_REDIRECT_TO_LOGIN = URL_INDEX + 'auth/login/?next='


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=AUTHOR)
        cls.not_author = User.objects.create_user(username=NOT_AUTHOR)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        Post.objects.create(
            author=cls.author,
            text=POST_TEXT,
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
            URL_INDEX: TEMPLATES_INDEX,
            URL_GROUP: TEMPLATES_GROUP,
            URL_PROFILE: TEMPLATES_PROFILE,
            URL_POST_DETAIL: TEMPLATES_POST_DETAIL,
            URL_POST_EDIT: TEMPLATES_POST_CREATE,
            URL_POST_CREATE: TEMPLATES_POST_CREATE,
        }
        for url, template in url_templates_names.items():
            with self.subTest(url=url, template=template):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_url_redirect_anonymous(self):
        url_redirects_names = {
            URL_POST_EDIT: URL_REDIRECT_TO_LOGIN + URL_POST_EDIT,
            URL_POST_CREATE: URL_REDIRECT_TO_LOGIN + URL_POST_CREATE,
        }
        for url, redirect in url_redirects_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, redirect)

    def test_url_redirect_not_author(self):
        url = URL_POST_EDIT
        redirect = URL_POST_DETAIL
        response = self.authorized_not_author_client.get(url, follow=True)
        self.assertRedirects(response, redirect)

    def test_url_anonymous(self):
        urls = (
            URL_INDEX,
            URL_GROUP,
            URL_PROFILE,
            URL_POST_DETAIL
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_url_authorized(self):
        urls = (
            URL_INDEX,
            URL_GROUP,
            URL_PROFILE,
            URL_POST_DETAIL,
            URL_POST_EDIT,
            URL_POST_CREATE,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_unexisting_page(self):
        url = URL_NONEXISTENT
        clients = (self.authorized_client, self.guest_client)
        for client in clients:
            with self.subTest(client=client):
                response = client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.NOT_FOUND.value
                )
