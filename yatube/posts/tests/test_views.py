from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Group, Post, User

AUTHOR = 'auth'
CONTEXT = 'page_obj'
FORM_FIELDS = {
    'text': forms.fields.CharField,
    'group': forms.models.ModelChoiceField,
}
GROUP_DESCRIPTION = 'Тестовое описание'
GROUP_SLUG = 'test-slug'
GROUP_TITLE = 'Тестовая группа'
GROUP_ANOTHER_DESCRIPTION = 'Другое тестовое описание'
GROUP_ANOTHER_SLUG = 'another-slug'
GROUP_ANOTHER_TITLE = 'Другая группа'
POST_TEXT = 'Тестовая пост'
POST_TEXT_FIRST = 'Тестовый пост другой группы'
REVERSE_INDEX = reverse('posts:index')
REVERSE_POST_CREATE = reverse('posts:post_create')
TEMPLATES_INDEX = 'posts/index.html'
TEMPLATES_GROUP = 'posts/group_list.html'
TEMPLATES_POST_CREATE = 'posts/create_post.html'
TEMPLATES_POST_DETAIL = 'posts/post_detail.html'
TEMPLATES_PROFILE = 'posts/profile.html'


class ViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.another_group = Group.objects.create(
            title=GROUP_ANOTHER_TITLE,
            slug=GROUP_ANOTHER_SLUG,
            description=GROUP_ANOTHER_DESCRIPTION,
        )
        cls.first_post = Post.objects.create(
            author=cls.author,
            text=POST_TEXT_FIRST,
            group=cls.another_group,
        )
        for i in range(13):
            cls.last_post = Post.objects.create(
                author=cls.author,
                text=f'{POST_TEXT} {i}',
                group=cls.group,
            )
        cls.reverse_profile = reverse('posts:profile', args=(cls.author,))
        cls.reverse_group = reverse(
            'posts:group_list',
            kwargs={'slug': cls.group.slug}
        )
        cls.reverse_anouther_group = reverse(
            'posts:group_list',
            kwargs={'slug': cls.another_group.slug}
        )
        cls.post_detail = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.last_post.id}
        )
        cls.post_edit = reverse(
            'posts:post_edit',
            kwargs={'post_id': cls.last_post.id}
        )
        cls.pages_with_paginator = {
            REVERSE_INDEX: TEMPLATES_INDEX,
            cls.reverse_group: TEMPLATES_GROUP,
            cls.reverse_profile: TEMPLATES_PROFILE,
        }
        cls.page_post_detail = {
            cls.post_detail: TEMPLATES_POST_DETAIL,
        }
        cls.pages_without_paginator = {
            cls.post_edit: TEMPLATES_POST_CREATE,
            REVERSE_POST_CREATE: TEMPLATES_POST_CREATE,
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

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
                    first_object = response.context[CONTEXT][0]
                except TypeError:
                    first_object = response.context[CONTEXT]
                post_author_0 = first_object.author
                post_text_0 = first_object.text
                post_group_0 = first_object.group
                self.assertEqual(post_author_0, self.author)
                self.assertEqual(post_text_0, self.last_post.text)
                self.assertEqual(post_group_0, self.group)

    def test_paginator(self):
        for reverse_name in self.pages_with_paginator.keys():
            with self.subTest(page=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(response.context[CONTEXT]), 10)
                response = self.client.get((reverse_name) + '?page=2')
                if reverse_name == self.reverse_group:
                    last_objects = 3
                else:
                    last_objects = 4

                self.assertEqual(
                    len(response.context[CONTEXT]),
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

            for value, expected in FORM_FIELDS.items():
                with self.subTest(value=value, page=reverse_name):
                    form_field = first_context.fields[value]
                    self.assertIsInstance(form_field, expected)
                    self.assertEqual(second_context, True)

    def test_post_with_another_group(self):
        reverse_name = self.reverse_anouther_group
        response = self.authorized_client.get(reverse_name)
        first_object = response.context[CONTEXT][0]
        post_group_0 = first_object.group
        self.assertNotEqual(post_group_0, self.group)
