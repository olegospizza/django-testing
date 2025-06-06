from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note


User = get_user_model()


class TestNoteCreation(TestCase):
    """Тестирование создания заметок."""

    @classmethod
    def setUpTestData(cls):
        """Создание тестовых данных."""
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note_data = {
            'title': 'Тестовая заметка',
            'text': 'Текст тестовой заметки',
            'slug': 'test-note'
        }
        cls.note = Note.objects.create(author=cls.author, **cls.note_data)
        cls.add_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')

    def test_authorized_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        self.client.force_login(self.author)
        notes_count_before = Note.objects.count()
        response = self.client.post(self.add_url, data=self.note_data)
        self.assertRedirects(response, self.success_url)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before + 1)

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        notes_count_before = Note.objects.count()
        response = self.client.post(self.add_url, data=self.note_data)
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={self.add_url}'
        self.assertRedirects(response, redirect_url)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)

    def test_cant_create_duplicate_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        self.client.force_login(self.author)
        notes_count_before = Note.objects.count()
        response = self.client.post(self.add_url, data=self.note_data)
        self.assertFormError(
            response,
            'form',
            'slug',
            'Такой slug уже существует, придумайте уникальное значение!'
        )
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)

    def test_auto_slug_generation(self):
        """Если slug не указан, он генерируется автоматически."""
        self.client.force_login(self.author)
        notes_count_before = Note.objects.count()
        note_data = {
            'title': 'Новая заметка без slug',
            'text': 'Текст новой заметки',
            'slug': ''  # Пустой slug
        }
        response = self.client.post(self.add_url, data=note_data)
        self.assertRedirects(response, self.success_url)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before + 1)
        new_note = Note.objects.latest('id')
        expected_slug = slugify(note_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(TestCase):
    """Тестирование редактирования и удаления заметок."""

    @classmethod
    def setUpTestData(cls):
        """Создание тестовых данных."""
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            slug='test-note',
            author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')
        cls.new_data = {
            'title': 'Обновленный заголовок',
            'text': 'Обновленный текст',
            'slug': 'updated-note'
        }

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        self.client.force_login(self.author)
        response = self.client.post(self.edit_url, data=self.new_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.new_data['title'])
        self.assertEqual(self.note.text, self.new_data['text'])
        self.assertEqual(self.note.slug, self.new_data['slug'])

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        self.client.force_login(self.author)
        notes_count_before = Note.objects.count()
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, self.success_url)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before - 1)

    def test_reader_cant_edit_note(self):
        """Не-автор не может редактировать заметку."""
        self.client.force_login(self.reader)
        response = self.client.post(self.edit_url, data=self.new_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertNotEqual(self.note.title, self.new_data['title'])
        self.assertNotEqual(self.note.text, self.new_data['text'])

    def test_reader_cant_delete_note(self):
        """Не-автор не может удалить заметку."""
        self.client.force_login(self.reader)
        notes_count_before = Note.objects.count()
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)
