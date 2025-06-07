import pytest
from http import HTTPStatus
from django.urls import reverse


@pytest.mark.parametrize(
    'name',
    ('news:home', 'news:detail', 'users:login', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name, news):
    """
    Тестирование доступности страниц для анонимных пользователей.
    Для detail передаём id новости, остальные без аргументов.
    """
    url = (
        reverse(name, args=(news.id,))
        if name == 'news:detail'
        else reverse(name)
    )
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'client, expected_status_edit, expected_status_delete',
    [
        ('author_client', HTTPStatus.OK, HTTPStatus.OK),
        ('reader_client', HTTPStatus.NOT_FOUND, HTTPStatus.NOT_FOUND),
    ],
    indirect=['client'],
)
def test_comment_edit_delete_availability(
    client, expected_status_edit, expected_status_delete, comment
):
    """Проверка доступности страниц редактирования и удаления комментария."""
    edit_url = reverse('news:edit', args=(comment.id,))
    delete_url = reverse('news:delete', args=(comment.id,))

    response_edit = client.get(edit_url)
    assert response_edit.status_code == expected_status_edit

    response_delete = client.get(delete_url)
    assert response_delete.status_code == expected_status_delete


def test_anonymous_user_redirect_to_login(client, comment):
    """Анонимный пользователь перенаправляется на страницу входа."""
    login_url = reverse('users:login')
    for name in ('news:edit', 'news:delete'):
        url = reverse(name, args=(comment.id,))
        expected_redirect = f'{login_url}?next={url}'
        response = client.get(url)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == expected_redirect


@pytest.mark.parametrize(
    'name, method, expected_status',
    [
        ('users:login', 'get', HTTPStatus.OK),
        ('users:signup', 'get', HTTPStatus.OK),
        ('users:logout', 'post', HTTPStatus.FOUND),
    ]
)
def test_auth_pages_availability_for_all_users(client,
                                               name,
                                               method,
                                               expected_status,
                                               django_user_model):
    """Страницы входа, регистрации и выхода доступны всем пользователям."""
    if name == 'users:logout':
        username = 'testuser'
        password = '12345'
        django_user_model.objects.create_user(username=username,
                                              password=password)
        client.login(username=username, password=password)

    url = reverse(name)
    response = getattr(client, method)(url)
    assert response.status_code == expected_status
