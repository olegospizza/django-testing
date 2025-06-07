import pytest
from http import HTTPStatus
from django.urls import reverse


@pytest.mark.parametrize(
    'name',
    ('news:home', 'news:detail', 'users:login', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name, news):
    """Проверка доступности страниц для анонимов."""
    url = reverse(name, args=(news.pk,) if 'detail' in name else None)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'client_fixture, expected_status_edit, expected_status_delete',
    [
        ('author_client', HTTPStatus.OK, HTTPStatus.OK),
        ('reader_client', HTTPStatus.NOT_FOUND, HTTPStatus.NOT_FOUND),
        ('client', HTTPStatus.FOUND, HTTPStatus.FOUND),
    ]
)
def test_comment_edit_delete_availability(
    request,
    client_fixture,
    expected_status_edit,
    expected_status_delete,
    comment
):
    """Проверка доступа к редактированию и удалению комментариев."""
    client = request.getfixturevalue(client_fixture)

    for name, expected_status in (
        ('news:edit', expected_status_edit),
        ('news:delete', expected_status_delete),
    ):
        url = reverse(name, args=(comment.pk,))
        response = client.get(url)
        assert response.status_code == expected_status

        if expected_status == HTTPStatus.FOUND:
            login_url = reverse('users:login')
            assert response.url.startswith(login_url)


def test_anonymous_user_redirect_to_login(client, comment):
    """Анонимный пользователь при попытке редактирования."""
    for name in ('news:edit', 'news:delete'):
        url = reverse(name, args=(comment.pk,))
        expected_redirect = reverse('users:login') + f'?next={url}'
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
def test_auth_pages_availability_for_all_users(
    client, name, method, expected_status, django_user_model
):
    """Проверка доступности login/signup/logout."""
    if name == 'users:logout':
        user = django_user_model.objects.create_user(
            username='logout_user', password='pass'
        )
        assert client.login(username='logout_user', password='pass')

    url = reverse(name)
    response = getattr(client, method)(url)
    assert response.status_code == expected_status