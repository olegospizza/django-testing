import pytest
from http import HTTPStatus
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError
from news.forms import BAD_WORDS, WARNING
from news.models import Comment

COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Новый текст комментария'
BAD_WORD_COMMENT = f'Какой-то текст, {BAD_WORDS[0]}, еще текст'


@pytest.mark.parametrize(
    'client, expected_comments_count',
    [
        ('client', 0),
        ('author_client', 1),
    ],
    indirect=['client'],
)
def test_comment_creation_for_different_users(
    client, expected_comments_count, news, author, detail_url
):
    """Проверка создания комментария разными пользователями."""
    initial_count = Comment.objects.count()
    response = client.post(detail_url, data={'text': COMMENT_TEXT})

    if expected_comments_count:
        assertRedirects(response, f'{detail_url}#comments')
        new_comment = Comment.objects.latest('id')
        assert new_comment.text == COMMENT_TEXT
        assert new_comment.news == news
        assert new_comment.author == author
    else:
        login_url = reverse('users:login')
        assertRedirects(response, f'{login_url}?next={detail_url}')

    assert Comment.objects.count() == initial_count + expected_comments_count


def test_bad_words_in_comment(author_client, detail_url):
    """Комментарий с запрещенными словами не публикуется."""
    initial_count = Comment.objects.count()
    response = author_client.post(detail_url, data={'text': BAD_WORD_COMMENT})
    assertFormError(response.context['form'], 'text', errors=WARNING)
    assert Comment.objects.count() == initial_count


@pytest.mark.parametrize(
    'client, expected_status, expected_change',
    [
        ('author_client', HTTPStatus.FOUND, True),
        ('reader_client', HTTPStatus.NOT_FOUND, False),
        ('client', HTTPStatus.FOUND, False),
    ],
    indirect=['client'],
)
def test_comment_edit_for_different_users(
    client, expected_status, expected_change, comment, detail_url
):
    """Проверка редактирования комментария разными пользователями."""
    edit_url = reverse('news:edit', args=(comment.id,))
    old_text = comment.text
    response = client.post(edit_url, data={'text': NEW_COMMENT_TEXT})

    assert response.status_code == expected_status
    comment.refresh_from_db()

    if expected_change:
        assertRedirects(response, f'{detail_url}#comments')
        assert comment.text == NEW_COMMENT_TEXT
    else:
        if expected_status == HTTPStatus.FOUND:
            login_url = reverse('users:login')
            assertRedirects(response, f'{login_url}?next={edit_url}')
        assert comment.text == old_text


@pytest.mark.parametrize(
    'client, expected_status, expected_change',
    [
        ('author_client', HTTPStatus.FOUND, True),
        ('reader_client', HTTPStatus.NOT_FOUND, False),
        ('client', HTTPStatus.FOUND, False),
    ],
    indirect=['client'],
)
def test_comment_delete_for_different_users(
    client, expected_status, expected_change, comment, detail_url
):
    """Проверка удаления комментария разными пользователями."""
    delete_url = reverse('news:delete', args=(comment.id,))
    initial_count = Comment.objects.count()
    response = client.post(delete_url)

    assert response.status_code == expected_status

    if expected_change:
        assertRedirects(response, f'{detail_url}#comments')
        assert Comment.objects.count() == initial_count - 1
    else:
        if expected_status == HTTPStatus.FOUND:
            login_url = reverse('users:login')
            assertRedirects(response, f'{login_url}?next={delete_url}')
        assert Comment.objects.count() == initial_count
