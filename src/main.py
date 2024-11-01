import os.path

from src.article_analysis import *
from src.helper_stuff import *
from src.site_scrapping import *

if __name__ == '__main__':
    log.info("Woof! Ready to sniff for injustice")
    # News sites objects to collect articles from
    sites = SitesPool([ConcreteNewsSite("https://www.epravda.com.ua/sitemap.xml"),
                       ConcreteNewsSite("https://ua.korrespondent.net/sitemap/ua/sitemap.xml")])
    log.info(f"Will sniff in these places: {str(sites)}")
    batch_size_configuration = 10
    log.debug(f"Batch size set to {batch_size_configuration}")
    log.info("Begin sniffin'")

    # Start rounds of article analysis
    while not sites.is_empty():
        collected_data = []
        # Collecting urls for articles
        batch_of_articles = dilated_page_pick(batch_size_configuration, sites)
        # Analyse each article in the batch
        for article_url in batch_of_articles:
            try:
                # Filter articles unrelated to governors crimes
                if is_article_on_topic(article_url):
                    found_criminals = identify_criminals(scrap_text_from_article(article_url))
                    for criminal in found_criminals:
                        collected_data.append(criminal)
            except Exception as e:
                log.error("Something went wrong when analysing text on %s. Error: %s", article_url, e)
                continue

        # TODO: Update the table with collected_data
        path_to_table = "/".join(__file__.split("/")[:-1])+"/gov.csv"
        log.info("Writing down found bad guys into %s", path_to_table)
        serialize_small_table(collected_data, path_to_table)
