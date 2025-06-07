from datetime import timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

URL_HOME = 'news:home'
URL_DETAIL = 'news:detail'
URL_EDIT = 'news:edit'
URL_DELETE = 'news:delete'
URL_LOGIN = 'users:login'
URL_LOGOUT = 'users:logout'
URL_SIGNUP = 'users:signup'
OBJECT_LIST = 'object_list'
NEWS = 'news'
FORM = 'form'
COMMENT_TEXT = 'Первоночальный текст'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


def client_authorization(auth_client):
    client = Client()
    client.force_login(auth_client)
    return client


@pytest.fixture
def author_client(author):
    return client_authorization(author)


@pytest.fixture
def not_author_client(not_author):
    return client_authorization(not_author)


@pytest.fixture
def new():
    new = News.objects.create(
        title='Заголовок Новости',
        text='Текст Новости',
    )
    return new


@pytest.fixture
def news():
    today = timezone.now()
    News.objects.bulk_create(
        News(
            title='Заголовок Новости',
            text='Текст Новости',
            date=today - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def new_id_for_agrs(new):
    return (new.pk,)


@pytest.fixture
def comment(author, new):
    comment = Comment.objects.create(
        news=new,
        author=author,
        text=COMMENT_TEXT,
    )
    return comment


@pytest.fixture
def comments(author, new):
    today = timezone.now()
    Comment.objects.bulk_create([
        Comment(
            news=new,
            author=author,
            text=f'Текст коменнтария {index}',
            created=today + timedelta(days=index),
        ) for index in range(2)
    ])


@pytest.fixture
def comment_id_for_agrs(comment):
    return (comment.pk,)


@pytest.fixture
def object_list(client):
    url = reverse(URL_HOME)
    response = client.get(url)
    object_list = response.context[OBJECT_LIST]
    return object_list


@pytest.fixture
def form_data():
    return {
        'text': COMMENT_TEXT,
    }


@pytest.fixture
def form_data_other():
    return {
        'text': NEW_COMMENT_TEXT,
    }


@pytest.fixture
def url_home():
    return reverse(URL_HOME)


@pytest.fixture
def url_detail(new_id_for_agrs):
    url_detail = reverse(URL_DETAIL, args=new_id_for_agrs)
    return url_detail


@pytest.fixture
def url_delete(comment_id_for_agrs):
    url_delete = reverse(URL_DELETE, args=comment_id_for_agrs)
    return url_delete


@pytest.fixture
def url_edit(comment_id_for_agrs):
    url_edit = reverse(URL_EDIT, args=comment_id_for_agrs)
    return url_edit


@pytest.fixture
def url_to_comments(new_id_for_agrs):
    news_url = reverse('news:detail', args=new_id_for_agrs)
    url_to_comments = news_url + '#comments'
    return url_to_comments
