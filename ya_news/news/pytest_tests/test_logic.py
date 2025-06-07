from http import HTTPStatus

import pytest
from django.contrib.auth import get_user_model
from pytest_django.asserts import assertFormError, assertRedirects

from .conftest import COMMENT_TEXT, NEW_COMMENT_TEXT
from news.forms import BAD_WORDS, WARNING
from news.models import Comment, News


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, form_data, url_detail
):
    """Проверяет, что анонимный клиент не сможет оставить комментарий."""
    expectation_comments_count = Comment.objects.count()
    client.post(url_detail, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == expectation_comments_count, (
        'Проверте, что анонимный клиент не сможет оставить комментарий.'
    )


def test_user_can_create_comment(author_client, form_data, url_detail):
    """Проверяет, что зарегистрированный клиент может оставить комментарий."""
    expectation_comments_count = Comment.objects.count()
    author_client.post(url_detail, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == expectation_comments_count + 1, (
        'Проверте, что зарегистрированный клиент может оставить комментарий.'
    )
    user = get_user_model().objects.get()
    new = News.objects.get()
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT, (
        'Проверте, что при сохранение комментария, корректно заполняется поле '
        '"text".'
    )
    assert comment.news == new, (
        'Проверте, что при сохранение комментария, корректно заполняется поле '
        '"new".'
    )
    assert comment.author == user, (
        'Проверте, что при сохранение комментария, корректно заполняется поле '
        '"author".'
    )


@pytest.mark.parametrize(
    'bad_word',
    BAD_WORDS,
)
def test_user_cant_use_bad_words(author_client, url_detail, bad_word):
    """Проверяет, что нельзя оставить комментарий с запретными словами."""
    bad_words_data = {
        'text': f'Какой-то текст, {bad_word}, еще текст'
    }
    expectation_comments_count = Comment.objects.count()
    response = author_client.post(url_detail, data=bad_words_data)
    msg_prefix = (f'\nЛогика формы на вывод ошибки "{WARNING}" допустила '
                  'ошибку.\n')
    assertFormError(
        response=response,
        form='form',
        field='text',
        errors=WARNING,
        msg_prefix=msg_prefix
    )
    comments_count = Comment.objects.count()
    assert comments_count == expectation_comments_count, (
        'Комментарий сохранился, несмотря на то, что содержал запретные слова.'
    )


def test_author_can_delete_comment(url_delete, url_to_comments, author_client):
    """Проверяет, что пользователь может удалять свои комментарии."""
    expectation_comments_count = Comment.objects.count()
    response = author_client.delete(url_delete)
    msg_prefix = '\nПроверте переадресацию, после удаления комментария.\n'
    assertRedirects(response, url_to_comments, msg_prefix=msg_prefix)
    comments_count = Comment.objects.count()
    assert comments_count == expectation_comments_count - 1, (
        'Комментарий не удалился.'
    )


def test_user_cant_delete_comment_of_another_user(
    url_delete, not_author_client
):
    """Проверяет, что пользователь не может удалять чужие комментарии."""
    expectation_comments_count = Comment.objects.count()
    response = not_author_client.delete(url_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        'При пропытке удалить чужой комментарий, должна выходить ошибка 404.'
    )
    comments_count = Comment.objects.count()
    assert comments_count == expectation_comments_count, (
        'Пользователь смог удалить чужой комментарий.'
    )


def test_author_can_edit_comment(
    url_edit, url_to_comments, author_client, form_data_other
):
    """Проверяет, что пользователь может редактировать свои комментарии."""
    response = author_client.post(url_edit, data=form_data_other)
    msg_prefix = ('\nПроверте переадресацию, после редактирования '
                  'комментария.\n')
    assertRedirects(response, url_to_comments, msg_prefix=msg_prefix)
    comment = Comment.objects.get()
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT, (
        'Комментарий не был изменен.'
    )


def test_user_cant_edit_comment_of_another_user(
    url_edit, not_author_client, form_data_other
):
    """Проверяет, что пользователь не может редактировать чужие комментарии."""
    response = not_author_client.post(url_edit, data=form_data_other)
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        'При пропытке редактировать чужой комментарий, должна выходить '
        'ошибка 404.'
    )
    comment = Comment.objects.get()
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT, (
        'Пользователь смог отредактировать чужой комментарий.'
    )
