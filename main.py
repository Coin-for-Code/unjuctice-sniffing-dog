import os
import requests
import gzip
from io import BytesIO
from random import choice
from abc import ABC, abstractmethod
import xml.etree.ElementTree as ET
import re
import logging

TEMP_PATH = os.path.join(".", "temp")

silly_logger = logging.getLogger("sillybaka")
silly_logger.setLevel(logging.DEBUG)
silly_logger.addHandler(logging.StreamHandler())


def parse_sitemap(url):
    silly_logger.debug("Requesting the articles for %s", url)
    response = requests.get(url)
    if response.status_code != 200:
        silly_logger.debug("Failed to get responce from %s", url)
        raise requests.exceptions.RequestException("The site map is unreachable")

    links = []

    # Check if a file is a gzip or treat
    if url.endswith('.gz') and response.content[:2] == b'\x1f\x8b':  # Проверка gzip по magic number
        try:
            with gzip.GzipFile(fileobj=BytesIO(response.content)) as f:
                xml_content = f.read()
        except gzip.BadGzipFile:
            silly_logger.error(f"Error unpacking gzip archive in a sitemap at {url}. The gzip wasn't correct or corrupted")
            return []
    else:
        xml_content = response.content

    silly_logger.debug("Parsing the content")
    root = ET.fromstring(xml_content)
    # Проверка типа XML (sitemap или urlset)
    if root.tag.endswith('sitemapindex'):
        # Если это индекс сайтмапов, то проходим по каждому дочернему сайтмапу
        for sitemap in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap"):
            sub_sitemap_url = sitemap.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
            try:
                links.extend(parse_sitemap(sub_sitemap_url))  # Рекурсивный вызов
            except requests.exceptions.RequestException as e:
                silly_logger.debug("The subsite map is unreachable or corrupt")
    elif root.tag.endswith('urlset'):
        # Если это сайтмап с ссылками, то собираем ссылки на статьи
        for url_elem in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
            loc = url_elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
            links.append(loc)

    silly_logger.debug("Collected %d links from %s", len(links), url)
    return links


class NewsSite(ABC):
    @abstractmethod
    def get_unique_url(self):
        """Gets a new webpage from the website"""
        pass


class ConcreteNewsSite(NewsSite):
    def __init__(self, url: str):
        silly_logger.debug("Initialising news site")
        self._site_url = url
        silly_logger.debug("Url set to %s", self._site_url)
        self._buffer_file_name = re.search(r"^(?:https?://)?(?:www\.)?([^/]+)", url).group(1)
        silly_logger.debug("The name filename %s", self._buffer_file_name)
        silly_logger.debug("Gathering used articles")
        self._used_articles = self._get_used_articles()
        silly_logger.debug("Gathered %d used articles", len(self._used_articles))
        silly_logger.debug("Scraping for new articles")
        self._scrapped_articles = self._get_scrapped_articles()
        silly_logger.debug("Scrapped %d articles", len(self._scrapped_articles))
        silly_logger.debug("Removing used links")
        intersected_articles = [article for article in self._used_articles if article in self._scrapped_articles]
        for repeated_article in intersected_articles:
            self._scrapped_articles.remove(repeated_article)

    def _get_used_articles(self):
        links = []
        is_file_available = False
        buffer_filename = "used_" + self._buffer_file_name + "_articles.txt"
        for filename in os.listdir(TEMP_PATH):
            if filename == buffer_filename:
                is_file_available = True
                with open(os.path.join(TEMP_PATH, filename), "r") as f:
                    for line in f.readlines():
                        links.append(line)

        if not is_file_available:
            with open(buffer_filename, "w") as f:
                pass
        return links

    def _get_scrapped_articles(self):
        links = []
        is_file_available = False
        buffer_filename = "scrapped_"+self._buffer_file_name+"_articles.txt"

        # Searching for the buffer file
        for filename in os.listdir(TEMP_PATH):
            if filename == buffer_filename:
                is_file_available = True
                silly_logger.debug("Found buffer file for scrapped articles %s", filename)
                with open(os.path.join(TEMP_PATH, filename), "r") as f:
                    for line in f.readlines():
                        links.append(line)

        # Being scrapping for links
        if not is_file_available:
            silly_logger.debug("Didn't find any buffer file for scrapped articles. Beginning to scrap.")
            links = parse_sitemap(self._site_url)

            # Write the links
            with open(buffer:=os.path.join(TEMP_PATH, buffer_filename), 'w', encoding='utf-8') as f:
                silly_logger.debug("Writing scrapped articles into %s file", buffer)
                for link in links:
                    f.write(f'{link}\n')

        return links

    def get_unique_url(self):
        """
        Will take an article from of available articles and return one. It requires that **self.scrapped_articles**
        contains only unused articles
        """
        if len(self._scrapped_articles)==0:
            silly_logger.debug("REMOVE AFTER TESTING: len(scrapped)=%d", len(self._scrapped_articles))
            raise Exception("No articles left")
        article = choice(self._scrapped_articles)
        self._used_articles.append(article)
        # TODO Write used articles to a file
        self._scrapped_articles.remove(article)
        return article


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


if __name__ == '__main__':
    EPravdaSite = ConcreteNewsSite("https://www.epravda.com.ua/sitemap.xml")
    print(EPravdaSite.get_unique_url())
