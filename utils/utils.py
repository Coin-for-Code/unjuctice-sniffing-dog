import os
import requests
import gzip
from io import BytesIO
from random import choice
from abc import ABC, abstractmethod
import xml.etree.ElementTree as ET
import re
import logging
from bs4 import BeautifulSoup

TEMP_PATH = os.path.join(".", "temp")
LOGGER_NAME = "sillybaka"
KEY_WORDS = []

log = logging.getLogger(LOGGER_NAME)


def parse_sitemap(url):
    log.debug("Requesting the articles for %s", url)
    response = requests.get(url)
    if response.status_code != 200:
        log.debug("Failed to get responce from %s", url)
        raise requests.exceptions.RequestException("The site map is unreachable")

    links = []

    # Check if a file is a gzip or treat
    if url.endswith('.gz') and response.content[:2] == b'\x1f\x8b':  # Проверка gzip по magic number
        try:
            with gzip.GzipFile(fileobj=BytesIO(response.content)) as f:
                xml_content = f.read()
        except gzip.BadGzipFile:
            log.error(f"Error unpacking gzip archive in a sitemap at {url}. The gzip wasn't correct or corrupted")
            return []
    else:
        xml_content = response.content

    log.debug("Parsing the content")
    root = ET.fromstring(xml_content)
    # Проверка типа XML (sitemap или urlset)
    if root.tag.endswith('sitemapindex'):
        # Если это индекс сайтмапов, то проходим по каждому дочернему сайтмапу
        for sitemap in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap"):
            sub_sitemap_url = sitemap.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
            try:
                links.extend(parse_sitemap(sub_sitemap_url))  # Рекурсивный вызов
            except requests.exceptions.RequestException as e:
                log.debug("The subsite map is unreachable or corrupt")
    elif root.tag.endswith('urlset'):
        # Если это сайтмап с ссылками, то собираем ссылки на статьи
        for url_elem in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
            loc = url_elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
            links.append(loc)

    log.debug("Collected %d links from %s", len(links), url)
    return links


def check_keywords_in_article(url):
    """
    Will search for keywords to filter needed articles from unrelated. Keep it stupid, but simple
    :param url: The url of an article to check
    :return: True if article contains the keywords, otherwise False
    :raise RequestException: if the ``qhttp`` request is bad
    """
    try:
        # Получаем содержимое страницы
        log.debug("Requesting the contents at %s", url)
        response = requests.get(url)
        response.raise_for_status()  # Проверка на ошибки HTTP

        # Извлекаем текст статьи
        soup = BeautifulSoup(response.content, 'html.parser')
        article_text = soup.get_text().lower()  # Приводим текст к нижнему регистру

        # Проверяем на совпадение с ключевыми словами
        for keyword in KEY_WORDS:
            if keyword.lower() in article_text:
                return True
    except Exception as e:
        print(f"Ошибка при обработке {url}: {e}")

    return False


class NewsSite(ABC):
    @abstractmethod
    def get_unique_url(self):
        """Gets a new webpage from the website"""
        pass

    @abstractmethod
    def __str__(self):
        pass


class EndOfProcess(Exception):
    pass


class OutOfArticles(Exception):
    """
    An exception to be raised when a news site runs out of articles.
    Has a reference to the emptied news site
    """
    def __init__(self, empty_site: NewsSite):
        """
        :param empty_site: The news site object that has run out of articles
        """
        self.empty_site = empty_site
        super().__init__()


class ConcreteNewsSite(NewsSite):
    def __init__(self, url: str):
        log.debug("Initialising news site")
        self._site_url = url
        log.debug("Url set to %s", self._site_url)
        self._site_domain = re.search(r"^(?:https?://)?(?:www\.)?([^/]+)", url).group(1)
        log.debug("The name filename %s", self._site_domain)
        log.debug("Gathering used articles")
        self._used_articles = self._get_used_articles()
        log.debug("Gathered %d used articles", len(self._used_articles))
        log.debug("Scraping for new articles")
        self._scrapped_articles = self._get_scrapped_articles()
        log.debug("Scrapped %d articles", len(self._scrapped_articles))
        log.debug("Removing used links")
        intersected_articles = [article for article in self._used_articles if article in self._scrapped_articles]
        for repeated_article in intersected_articles:
            self._scrapped_articles.remove(repeated_article)

    def __str__(self):
        """String for of a news site is its domain name"""
        return self._site_domain

    def _get_used_articles(self):
        links = []
        is_file_available = False
        buffer_filename = "used_" + self._site_domain + "_articles.txt"
        for filename in os.listdir(TEMP_PATH):
            if filename == buffer_filename:
                is_file_available = True
                with open(os.path.join(TEMP_PATH, filename), "r") as f:
                    for line in f.readlines():
                        links.append(line)

        if not is_file_available:
            with open(os.path.join(buffer_filename, ), "w") as f:
                pass
        return links

    def _get_scrapped_articles(self):
        links = []
        is_file_available = False
        buffer_filename = "scrapped_" + self._site_domain + "_articles.txt"

        # Searching for the buffer file
        for filename in os.listdir(TEMP_PATH):
            if filename == buffer_filename:
                is_file_available = True
                log.debug("Found buffer file for scrapped articles %s", filename)
                with open(os.path.join(TEMP_PATH, filename), "r") as f:
                    for line in f.readlines():
                        links.append(line)

        # Being scrapping for links
        if not is_file_available:
            log.debug("Didn't find any buffer file for scrapped articles. Beginning to scrap.")
            links = parse_sitemap(self._site_url)

            # Write the links
            with open(buffer := os.path.join(TEMP_PATH, buffer_filename), 'w', encoding='utf-8') as f:
                log.debug("Writing scrapped articles into %s file", buffer)
                for link in links:
                    f.write(f'{link}\n')

        return links

    def get_unique_url(self):
        """
        Will take an article from of available articles and return one. It requires that **self.scrapped_articles**
        contains only unused articles
        :raise OutOfArticles: when the site has no articles
        """
        if len(self._scrapped_articles) == 0:
            raise OutOfArticles(self)
        article = choice(self._scrapped_articles)
        self._used_articles.append(article)
        # TODO Write used articles to a file
        self._scrapped_articles.remove(article)
        return article
