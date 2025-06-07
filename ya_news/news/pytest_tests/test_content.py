from django.urls import reverse
from django.conf import settings
from news.forms import CommentForm

NEWS_COUNT_ON_HOME_PAGE = 10


def test_news_count_on_home_page(author_client, news_batch):
    """Количество новостей на главной странице не превышает лимит."""
    url = reverse('news:home')
    response = author_client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) == NEWS_COUNT_ON_HOME_PAGE


def test_news_order_on_home_page(author_client, news_batch):
    """Новости на главной отсортированы от новых к старым."""
    url = reverse('news:home')
    response = author_client.get(url)
    object_list = response.context['object_list']
    dates = [news.date for news in object_list]
    assert dates == sorted(dates, reverse=True)


def test_comments_order_on_news_page(author_client,
                                     news,
                                     comments,
                                     detail_url):
    """Комментарии на странице новости отсортированы от старых к новым."""
    response = author_client.get(detail_url)
    comment_list = list(response.context['news'].comment_set.all())
    sorted_list = sorted(comment_list, key=lambda c: c.created)
    assert comment_list == sorted_list


def test_comment_form_available_for_authorized_user(author_client, detail_url):
    """Авторизованному пользователю доступна форма комментария."""
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


def test_comment_form_unavailable_for_anonymous_user(client, detail_url):
    """Анонимному пользователю форма комментария недоступна."""
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_single_news_in_list(author_client, news):
    """Проверка, что новость отображается на главной."""
    url = reverse('news:home')
    response = author_client.get(url)
    object_list = response.context['object_list']
    assert news in object_list
