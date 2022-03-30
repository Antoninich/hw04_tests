from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Post, Group, User

AUTHOR = 'auth'
GROUP_DESCRIPTION = 'Тестовое описание'
GROUP_SLUG = 'test-slug'
GROUP_TITLE = 'Тестовая группа'
POST_ID = '1'
POST_TEXT = 'Тестовая пост'
POST_TEXT_EDITED = 'Редактированный Тестовый текст'
REVERSE_POST_CREATE = reverse('posts:post_create')
REVERSE_POST_EDIT = reverse('posts:post_edit', args=(POST_ID,))


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.form = PostForm()
        cls.reverse_profile = reverse('posts:profile', args=(cls.author,))

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_create_edit(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': POST_TEXT,
        }
        response = self.authorized_client.post(
            REVERSE_POST_CREATE,
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            self.reverse_profile
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=POST_TEXT,
            ).latest('pk')
        )

        form_data = {
            'text': POST_TEXT_EDITED,
        }
        post_id = Post.objects.latest('pk').id
        reverse_post_edit = reverse('posts:post_edit', args=(post_id,))
        reverse_post_detail = reverse('posts:post_detail', args=(post_id,))
        response = self.authorized_client.post(
            reverse_post_edit,
            data=form_data,
            follow=True
        )

        self.assertRedirects(
            response,
            reverse_post_detail
        )
