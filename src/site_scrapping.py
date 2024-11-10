from src import log
from src.helper_stuff import OutOfArticles

import os
import requests

from random import choice
from abc import ABC, abstractmethod
from io import BytesIO
import re
import gzip
from bs4 import BeautifulSoup
from xml.etree import ElementTree


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
            log.error("Error unpacking gzip archive in a sitemap at %s. The gzip wasn't correct or corrupted", url)
            return []
    else:
        xml_content = response.content

    log.debug("Parsing the content")
    root = ElementTree.fromstring(xml_content)
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


def scrap_text_from_article(url):
    """
    Gets text from an article
    :param url: The articles url
    :return: Text inside the url
    :raise requests.exceptions.RequestException: If http request was bad
    """
    log.debug("Requesting the contents at %s", url)
    response = requests.get(url)
    response.raise_for_status()
    log.debug("Response is OK")
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(separator="", strip=True).lower()
    log.debug("Extracted text %d characters long", len(text))
    return text


def scrap_date_from_article(url):
    """
    Извлекает дату написания статьи с указанного URL.
    
    :param url: URL статьи.
    :return: Дата написания статьи или None, если дата не найдена.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка на успешный ответ
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Поиск даты в тегах <time>
        date = soup.find("time")
        if date and date.has_attr("datetime"):
            return date["datetime"]

        # 2. Поиск даты в мета-тегах
        meta_tags = [
            {"property": "article:published_time"},
            {"property": "datePublished"},
            {"name": "pubdate"},
            {"name": "date"}
        ]

        for meta in meta_tags:
            meta_date = soup.find("meta", attrs=meta)
            if meta_date and meta_date.has_attr("content"):
                return meta_date["content"]

        # 3. Дополнительные проверки для других возможных форматов
        possible_dates = [
            soup.find("span", class_="date"),  # Пример класса для даты
            soup.find("div", class_="publish-date"),  # Пример класса для даты
            soup.find("p", class_="date")  # Пример класса для даты
        ]

        for possible_date in possible_dates:
            if possible_date:
                return possible_date.get_text(strip=True)

        # 4. Поиск даты в тексте статьи с помощью регулярных выражений
        article_text = soup.get_text()
        
        # Регулярное выражение для поиска форматов даты (например, "10 ноября 2024" или "2024-11-10")
        date_pattern = r'(\d{1,2}\s+[а-яА-ЯёЁ]+\s+\d{4}|\d{4}-\d{1,2}-\d{1,2})'
        found_dates = re.findall(date_pattern, article_text)

        if found_dates:
            return found_dates[0]  # Возвращаем первую найденную дату

    except requests.RequestException as e:
        print(f"Ошибка при запросе к {url}: {e}")
    
    return None



class NewsSite(ABC):
    @abstractmethod
    def get_unique_url(self):
        """Gets a new webpage from the website"""
        pass

    @abstractmethod
    def __str__(self):
        pass


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
        # TODO: Ignoring save mechanisms, needs to get back it
        # for filename in os.listdir(TEMP_PATH):
        #     if filename == buffer_filename:
        #         is_file_available = True
        #         with open(os.path.join(TEMP_PATH, filename), "r") as f:
        #             for line in f.readlines():
        #                 links.append(line)

        if not is_file_available:
            with open(os.path.join("..", buffer_filename), "w") as f:
                pass
        return links

    def _get_scrapped_articles(self):
        links = []
        is_file_available = False
        buffer_filename = "scrapped_" + self._site_domain + "_articles.txt"

        # TODO: Ignoring save mechanisms, needs to get back it
        # Searching for the buffer file
        # for filename in os.listdir(".."):
        #     if filename == buffer_filename:
        #         is_file_available = True
        #         log.debug("Found buffer file for scrapped articles %s", filename)
        #         with open(os.path.join(TEMP_PATH, filename), "r") as f:
        #             for line in f.readlines():
        #                 links.append(line)

        # Being scrapping for links
        if not is_file_available:
            log.debug("Didn't find any buffer file for scrapped articles. Beginning to scrap.")
            links = parse_sitemap(self._site_url)

            # Write the links
            with open(buffer := os.path.join("..", buffer_filename), 'w', encoding='utf-8') as f:
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
