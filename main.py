from random import choice
from abc import ABC, abstractmethod


class NewsSite(ABC):
    @abstractmethod
    def get_unique_url(self):
        """Gets a new webpage from the website"""
        pass


class PravdaNews(NewsSite):
    def get_unique_url(self):
        pass


def dilated_page_pick(batch_size: int):
    """
    This will create a batch of web urls from different news sites
    :param batch_size: the amount of urls in one batch
    """
    news_sites_pool = []
    batch_of_urls = []
    for i in range(0, batch_size):
        # Inside the loop is the logic for picking the site for taking the webpage
        batch_of_urls.append(choice(news_sites_pool).get_unique_url())
    return batch_of_urls


