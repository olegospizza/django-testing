import pytest
from django.test.client import Client
from news.models import News, Comment
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news(author):
    return News.objects.create(
        title='Тестовая новость',
        text='Текст новости',
    )


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Test comment'
    )


@pytest.fixture
def id_for_args(comment):
    return comment.id


@pytest.fixture
def news_batch(author):
    return News.objects.bulk_create(
        News(
            title=f'Новость {i}',
            text='Текст новости',
        )
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def detail_url(news):
    """Фикстура возвращающая URL детальной страницы новости."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def comments(news, author):
    """Фикстура создающая 10 комментариев с разными датами."""
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст{index}'
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return Comment.objects.all()


@pytest.fixture
def edit_url():
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass
