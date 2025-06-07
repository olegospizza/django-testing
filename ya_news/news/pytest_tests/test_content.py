import pytest
from django.conf import settings

from .conftest import FORM, NEWS, OBJECT_LIST
from news.forms import CommentForm

pytestmark = [pytest.mark.django_db]


def test_news_context_count(client, url_home, news):
    """Проверяет количество новостей на главной странице."""
    response = client.get(url_home)
    assert OBJECT_LIST in response.context, (
        f'В контекст гланой странице не передаётся ключ "{OBJECT_LIST}".'
    )
    object_list = response.context[OBJECT_LIST]
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE, (
        f'Количество новостей на странице отобразилось {news_count} штук, а '
        f'должно {settings.NEWS_COUNT_ON_HOME_PAGE} штук.'
    )


def test_news_order(object_list):
    """Проверяет порядок отображения новостей на главной странице."""
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates, (
        'Новости на главной стронице должны отображатся от новой к старой.'
    )


def test_comments_order(client, comments, url_detail):
    """Проверяет очередность отображения комментариев."""
    response = client.get(url_detail)
    assert NEWS in response.context, (
        'На страницу отдельной новости в контексте не передался ключ '
        f'"{NEWS}".'
    )
    news = response.context[NEWS]
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps, (
        'Коментарии должны отображатся от старых к новым.'
    )


def test_anonymous_client_has_no_form(client, url_detail):
    """Проверяет передачу формы в словаре контекста."""
    response = client.get(url_detail)
    assert FORM not in response.context, (
        'При запросе анонимного пользователя в контектсе передалась форма.'
    )


def test_authorized_client_has_form(author_client, url_detail):
    """Проверяет передачу формы в словаре контекста."""
    response = author_client.get(url_detail)
    assert FORM in response.context, (
        'При запросе авторизованного пользователя в контектсе не передалась '
        'форма.'
    )
    assert isinstance(response.context[FORM], CommentForm), (
        f'Под ключем "{FORM}" в контекст передалась не та форма.'
    )
