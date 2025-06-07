import pytest
from http import HTTPStatus
from django.urls import reverse
from pytest_django.asserts import assertRedirects


pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(
    'name, expected_path, args',
    [
        ('news:home', '/', None),
        ('news:detail', '/news/1/', [1]),
        ('news:edit', '/edit_comment/1/', [1]),
        ('news:delete', '/delete_comment/1/', [1]),
        ('users:login', '/auth/login/', None),
        ('users:logout', '/auth/logout/', None),
        ('users:signup', '/auth/signup/', None),
    ]
)
def test_reverse_names(name, expected_path, args):
    """Проверяет соответствие namespace и путей."""
    url = reverse(name, args=args)
    assert url == expected_path, (
        f'Ожидался путь {expected_path} для namespace {name}, '
        f'но получен {url}.'
    )


@pytest.mark.parametrize(
    'client_fixture',
    ['client', 'author_client']
)
@pytest.mark.parametrize(
    'name, args',
    [
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('new_id_for_agrs')),
        ('users:login', None),
        ('users:signup', None),
    ]
)
def test_pages_availability(client_fixture, name, args, request):
    """Проверка доступности страниц для разных пользователей."""
    client = request.getfixturevalue(client_fixture)
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        f'Пользователь не смог попасть на страницу по namespace "{name}".'
    )


@pytest.mark.parametrize(
    'name',
    ['news:edit', 'news:delete']
)
def test_redirect_for_anonymous_user(client, name, comment_id_for_agrs):
    """Проверка редиректа неавторизованного пользователя на логин."""
    url = reverse(name, args=comment_id_for_agrs)
    expected_url = reverse('users:login') + f'?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'client_fixture, expected_status',
    [
        ('author_client', HTTPStatus.OK),
        ('not_author_client', HTTPStatus.NOT_FOUND),
    ]
)
@pytest.mark.parametrize(
    'name',
    ['news:edit', 'news:delete']
)
def test_edit_delete_availability_by_user_type(
    client_fixture, expected_status, name, request, comment_id_for_agrs
):
    """Проверка доступа к редактированию и удалению для автора и не-автора."""
    client = request.getfixturevalue(client_fixture)
    url = reverse(name, args=comment_id_for_agrs)
    response = client.get(url)
    assert response.status_code == expected_status, (
        f'Неверный код ответа при попытке доступа к "{name}".'
    )


def test_logout_redirects_authenticated_user(client, django_user_model):
    """Проверка выхода (logout) авторизованного пользователя."""
    django_user_model.objects.create_user(
        username='testuser', password='pass'
    )
    client.login(username='testuser', password='pass')
    url = reverse('users:logout')
    response = client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse('news:home')
