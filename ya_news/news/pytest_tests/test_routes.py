import pytest
from http import HTTPStatus
from django.urls import reverse


@pytest.mark.parametrize(
    'name',
    ('news:home', 'news:detail', 'users:login', 'users:signup', 'users:logout')
)
def test_pages_availability_for_anonymous_user(client, name, news):
    """Тестирование доступности страниц для анонимных пользователей."""
    url = (
        reverse(name, args=(news.id,))
        if name == 'news:detail'
        else reverse(name)
    )
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'client, expected_status',
    [
        ('author_client', HTTPStatus.OK),
        ('reader_client', HTTPStatus.NOT_FOUND),
    ],
    indirect=['client'],
)
def test_comment_edit_delete_availability(client, expected_status, comment):
    """Проверка доступности страниц редактирования и удаления комментария."""
    for name in ('news:edit', 'news:delete'):
        url = reverse(name, args=(comment.id,))
        response = client.get(url)
        assert response.status_code == expected_status


def test_anonymous_user_redirect_to_login(client, comment):
    """Анонимный пользователь перенаправляется на страницу входа."""
    login_url = reverse('users:login')
    for name in ('news:edit', 'news:delete'):
        url = reverse(name, args=(comment.id,))
        expected_redirect = f'{login_url}?next={url}'
        response = client.get(url)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == expected_redirect


def test_auth_pages_availability_for_all_users(client):
    """Страницы входа, регистрации и выхода доступны всем пользователям."""
    for name in ('users:login', 'users:signup', 'users:logout'):
        url = reverse(name)
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK
