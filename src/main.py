from src.article_analysis import is_article_on_topic
from src.helper_stuff import *
from src.site_scrapping import SitesPool

if __name__ == '__main__':
    log.info("Woof! Ready to sniff for injustice")
    # News sites objects to collect articles from
    sites = SitesPool([])
    log.info(f"Will sniff in these places: {str(sites)}")
    batch_size_configuration = 1
    log.debug(f"Batch size set to {batch_size_configuration}")
    log.info("Begin sniffin'")

    # Start rounds of article analysis
    while not sites.is_empty():
        collected_data = None
        # Collecting urls for articles
        batch_of_articles = dilated_page_pick(batch_size_configuration, sites)
        # Analyse each article in the batch
        for article_url in batch_of_articles:
            try:
                # Filter articles unrelated to governors crimes
                if is_article_on_topic(article_url):
                    pass
            except Exception as e:
                log.error("Something went wrong when analysing text on %s. Error: %s", article_url, e)
                continue

        # TODO: Update the table with collected_data
