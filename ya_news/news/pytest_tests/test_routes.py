from http import HTTPStatus

import pytest
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from .conftest import (
    URL_HOME,
    URL_DETAIL,
    URL_EDIT,
    URL_DELETE,
    URL_LOGIN,
    URL_LOGOUT,
    URL_SIGNUP,
)

NEW_ID = pytest.lazy_fixture('new_id_for_agrs')
COMMENT_ID = pytest.lazy_fixture('comment_id_for_agrs')
ANONYMOUS_CLIENT = Client()
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
NOT_AUTHOR_CLIENT = pytest.lazy_fixture('not_author_client')

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(
    'name, path, args',
    (
        (URL_HOME, '/', None),
        (URL_DETAIL, '/news/1/', NEW_ID),
        (URL_EDIT, '/edit_comment/1/', COMMENT_ID),
        (URL_DELETE, '/delete_comment/1/', COMMENT_ID),
        (URL_LOGIN, '/auth/login/', None),
        (URL_LOGOUT, '/auth/logout/', None),
        (URL_SIGNUP, '/auth/signup/', None),
    )
)
def test_correct_path_name(name, path, args):
    """Проверяет корректность названий путей."""
    url = reverse(name, args=args)
    assert url == path, (
        f'Путь "{path}" не соответствует namespace "{name}".'
    )


@pytest.mark.parametrize(
    'parametrized_client',
    (ANONYMOUS_CLIENT, AUTHOR_CLIENT)
)
@pytest.mark.parametrize(
    'name, args',
    (
        (URL_HOME, None),
        (URL_DETAIL, NEW_ID),
        (URL_LOGIN, None),
        (URL_LOGOUT, None),
        (URL_SIGNUP, None),
    )
)
def test_pages_availability_for_user(parametrized_client, name, args):
    """Проверяет доступность страниц для разных пользователей."""
    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        f'Пользователь не смог попасть на страницу по namespace "{name}".'
    )


@pytest.mark.parametrize(
    'name, id',
    (
        (URL_EDIT, COMMENT_ID),
        (URL_DELETE, COMMENT_ID),
    )
)
def test_redirect_for_anonymous_client(client, name, id):
    """Проверяет переадресацию неавторизованного пользователя на логин."""
    args = id if id else None
    url = reverse(name, args=args)
    login_url = reverse(URL_LOGIN)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url), (
        f'Неавторизированного пользователя должно перекинуть на страницу '
        f'авторизации при заходе на страницу "{name}".'
    )


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (AUTHOR_CLIENT, HTTPStatus.OK),
        (NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
    )
)
@pytest.mark.parametrize(
    'name',
    (URL_EDIT, URL_DELETE),
)
def test_pages_availability_for_different_users(
    parametrized_client, expected_status, name, comment_id_for_agrs
):
    """Проверяет доступ к редактированию и удалению комментариев."""
    url = reverse(name, args=comment_id_for_agrs)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status, (
        f'При попытке удалить или редактировать чужой комментарий должна '
        f'выходить ошибка 404. URL namespace: "{name}".'
    )
