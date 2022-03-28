from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Group, Post

User = get_user_model()


class ViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
        )
        cls.another_group = Group.objects.create(
            title='Другая группа',
            slug='another-slug',
        )
        cls.first_post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост другой группы',
            group=cls.another_group,
        )
        for i in range(13):
            cls.last_post = Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост {i}',
                group=cls.group,
            )
        cls.pages_with_paginator = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': cls.user}
            ): 'posts/profile.html',
        }
        cls.page_post_detail = {
            reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.last_post.id}
            ): 'posts/post_detail.html',
        }
        cls.pages_without_paginator = {
            reverse(
                'posts:post_edit',
                kwargs={'post_id': cls.last_post.id}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        cls.context = 'page_obj'
        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }

    def setUp(self):
        self.user = User.objects.get(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_templates(self):
        pages_templates = {
            **self.pages_with_paginator,
            **self.page_post_detail,
            **self.pages_without_paginator
        }
        for reverse_name, template in pages_templates.items():
            with self.subTest(page=reverse_name, template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_context_with_paginator(self):
        pages = (
            *self.pages_with_paginator.keys(),
            *self.page_post_detail.keys(),
        )
        for reverse_name in pages:
            with self.subTest(page=reverse_name):
                response = self.client.get(reverse_name)
                try:
                    first_object = response.context[self.context][0]
                except TypeError:
                    first_object = response.context[self.context]
                task_author_0 = first_object.author
                task_text_0 = first_object.text
                task_group_0 = first_object.group
                self.assertEqual(task_author_0, self.user)
                self.assertEqual(task_text_0, self.last_post.text)
                self.assertEqual(task_group_0, self.group)

    def test_paginator(self):
        for reverse_name in self.pages_with_paginator.keys():
            with self.subTest(page=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(response.context[self.context]), 10)
                response = self.client.get((reverse_name) + '?page=2')
                if reverse_name == reverse(
                    'posts:group_list',
                    kwargs={'slug': self.group.slug}
                ):
                    last_objects = 3
                else:
                    last_objects = 4

                self.assertEqual(
                    len(response.context[self.context]),
                    last_objects
                )

    def test_context_without_paginator(self):
        for reverse_name in self.pages_without_paginator.keys():
            response = self.authorized_client.get(reverse_name)
            first_context = response.context['form']
            try:
                second_context = response.context['is_edit']
            except KeyError:
                second_context = True

            for value, expected in self.form_fields.items():
                with self.subTest(value=value, page=reverse_name):
                    form_field = first_context.fields[value]
                    self.assertIsInstance(form_field, expected)
                    self.assertEqual(second_context, True)

    def test_post_with_another_group(self):
        reverse_name = reverse(
            'posts:group_list',
            kwargs={'slug': self.another_group.slug}
        )
        response = self.authorized_client.get(reverse_name)
        first_object = response.context[self.context][0]
        task_group_0 = first_object.group
        self.assertNotEqual(task_group_0, self.group)
