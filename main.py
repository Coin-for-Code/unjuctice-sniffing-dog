import logging

from utils.utils import *

log = logging.getLogger(LOGGER_NAME)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


class SitesPool:
    """Holds all the news sites"""
    def __init__(self, news_sites_pool: list):
        """List of news sites"""
        self._news_sites_pool = news_sites_pool

    def __str__(self):
        return ", ".join([str(site) for site in self._news_sites_pool])

    def remove(self, empty_news_site):
        self._news_sites_pool.remove(empty_news_site)

    def is_empty(self):
        return len(self._news_sites_pool) == 0

    def get_url(self):
        if len(self._news_sites_pool) == 0:
            return None
        news_site = choice(self._news_sites_pool)
        try:
            return news_site.get_unique_url()
        except OutOfArticles as signal:
            self._news_sites_pool.remove(signal.empty_site)
            return None


def dilated_page_pick(batch_size: int, site_pool: SitesPool):
    """
    This will create a batch of web urls from different news sites
    :param site_pool: The pool of all sites
    :param batch_size: the amount of urls in one batch
    """
    batch_of_urls = []
    for i in range(0, batch_size):
        # Inside the loop is the logic for picking the site for taking the webpage
        batch_of_urls.append(site_pool.get_url())
    return list(filter(None, batch_of_urls))


if __name__ == '__main__':
    log.info("Woof! Ready to sniff for injustice")
    # News sites objects to collect articles from
    sites = SitesPool([])
    log.info(f"Will sniff in these places: {str(sites)}")
    batch_size_configuration = 1
    log.debug(f"Batch size set to {batch_size_configuration}")
    log.info("Start sniffin'")

    # Start rounds of article analysis
    while not sites.is_empty():
        # Collecting urls for articles
        batch_of_articles = dilated_page_pick(batch_size_configuration, sites)
        for article_url in batch_of_articles:
            try:
                if check_keywords_in_article(article_url):
                    pass
            except requests.exceptions.RequestException:
                log.debug("The article at %s is not available or is corrupted", article_url)
            continue
