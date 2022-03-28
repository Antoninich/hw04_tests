from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
            group=cls.group,
        )

    def test_models_have_correct_object_names(self):
        model_object = {
            self.post: self.post.text[:15],
            self.group: self.group.title,
        }
        for model, object in model_object.items():
            with self.subTest(model=model):
                self.assertEqual(object, str(model))
