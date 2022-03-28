from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Post, Group

User = get_user_model()


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.form = PostForm()

    def setUp(self):
        self.user = User.objects.get(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_edit(self):
        tasks_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=(self.user,))
        )
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
            ).exists()
        )

        form_data = {
            'text': 'Редактированный Тестовый текст',
        }
        post_id = Post.objects.latest("pk").id
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(post_id,)),
            data=form_data,
            follow=True
        )

        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=(post_id,))
        )
