from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class BaseTestNote(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Создание тестовых данных один раз для всех тестов класса."""
        cls.auth_client = Client()
        cls.author = User.objects.create(username='note_author')
        cls.reader = User.objects.create(username='regular_user')
        cls.note = Note.objects.create(
            title='Тест заметка',
            text='Тестовый текст заметки',
            author=cls.author,
            slug='test-zametka'
        )


class TestRoutes(BaseTestNote):
    """Тестирование доступности маршрутов приложения для заметок."""

    def test_homepage_availability_for_anonymous(self):
        """Главная страница доступна анонимному пользователю."""
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authenticated_user_pages_availability(self):
        """Аутентифицированному пользователю доступны страницы заметок."""
        self.client.force_login(self.reader)
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_pages_availability_for_author(self):
        """Страницы заметки доступны только автору."""
        self.client.force_login(self.author)
        urls = (
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_pages_unavailability_for_another_user(self):
        """Страницы заметки недоступны для не автора (404)."""
        self.client.force_login(self.reader)
        urls = (
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect_for_anonymous_on_protected_pages(self):
        """
        Аноним перенаправляется на логин
        при доступе к защищенным страницам.
        """
        login_url = reverse('users:login')
        protected_urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for name, args in protected_urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_auth_pages_availability_for_all_users(self):
        """Страницы аутентификации доступны всем пользователям."""
        urls = (
            ('users:login', None),
            ('users:signup', None),
            ('users:logout', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
