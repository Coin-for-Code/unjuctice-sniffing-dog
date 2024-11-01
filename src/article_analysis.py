from src import *
from textblob import TextBlob
import spacy

import requests
from src.site_scrapping import scrap_text_from_article


def is_article_on_topic(url):
    """
    Will search for keywords to filter needed articles from unrelated. Keep it stupid, but simple
    :param url: The url of an article to check
    :return: True if article contains the keywords, otherwise False
    :raise requests.exceptions.RequestException`: if the ``qhttp`` request is bad
    """
    try:
        log.debug("Filtering (%s) on governors crime topics", url)
        article_text = scrap_text_from_article(url)

        # Проверяем на совпадение с ключевыми словами
        for keyword in KEY_WORDS:
            if keyword.lower() in article_text:
                log.debug("Article (%s) have right topic", url)
                return True
    except requests.exceptions.RequestException as bad_req:
        log.debug("Article (%s) is unreachable", url)
        return False

    log.debug("Article (%s) doesn't have the right topic", url)
    return False