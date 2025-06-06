from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestContent(TestCase):
    """Тестирование контента страниц приложения для заметок."""

    @classmethod
    def setUpTestData(cls):
        """Создание тестовых данных."""
        cls.author = User.objects.create(username='Автор заметки')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст тестовой заметки',
            slug='test-note',
            author=cls.author
        )

    def test_note_in_list_for_author(self):
        """Отдельная заметка передаётся на страницу со списком заметок."""
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:list'))
        self.assertIn('object_list', response.context)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_notes_separation_between_users(self):
        """В список заметок одного пользователя не попадают заметки другого."""
        Note.objects.create(
            title='Чужая заметка',
            text='Текст чужой заметки',
            slug='foreign-note',
            author=self.reader
        )
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        self.assertTrue(
            all(note.author == self.author for note in object_list)
        )
        self.assertEqual(len(object_list), 1)
        self.assertEqual(object_list[0], self.note)

    def test_create_page_contains_form(self):
        """На страницу создания заметки передаётся форма."""
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:add'))
        self.assertIn('form', response.context)

    def test_edit_page_contains_form(self):
        """На страницу редактирования заметки передаётся форма."""
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.get(url)
        self.assertIn('form', response.context)

    def test_note_link_visible_for_authorized(self):
        """Ссылка на список заметок видна авторизованному пользователю."""
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:home'))
        notes_url = reverse('notes:list')
        self.assertContains(response, notes_url)

    def test_note_link_invisible_for_anonymous(self):
        """Ссылка на список заметок не видна анонимному пользователю."""
        response = self.client.get(reverse('notes:home'))
        notes_url = reverse('notes:list')
        self.assertNotContains(response, notes_url)
