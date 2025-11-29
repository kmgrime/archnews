from archnews.fetcher import NewsFetcher


def test_constructor():
    f = NewsFetcher()
    assert f.source_url == "https://archlinux.org/news/"


def test_get_news_returns_list():
    f = NewsFetcher()
    articles = f.get_articles()
    assert isinstance(articles, list)
    assert len(articles) == 2
