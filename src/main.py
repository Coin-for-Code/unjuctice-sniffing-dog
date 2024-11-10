import sys

from src.utils import *
from src.utils.article_analysis import *
from src.utils.site_scrapping import *

if __name__ == '__main__':
    try:
        path_to_save_directory = sys.argv[1]
        if not os.path.exists(path_to_save_directory):
            log.error("The path %s is not a real path", path_to_save_directory)
            sys.exit(2)
    except IndexError:
        log.error("You need to provide a path to a table!")
        sys.exit(2)

    log.info("The table path is correct.")
    log.info("Woof! Ready to sniff for injustice")
    # News sites objects to collect articles from
    sites = SitesPool([ConcreteNewsSite("https://www.epravda.com.ua/sitemap.xml")])
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
                    text = scrap_text_from_article(article_url)
                    found_criminals = identify_criminals_beta(text)
                    date = scrap_date_from_article(article_url)
                    for criminal in found_criminals:
                        # Add columns to the data
                        collected_data.append([criminal, article_url, date])
            except Exception as e:
                log.error("Something went wrong when analysing text on %s. Error: %s", article_url, e)
                continue

        # Finds the path to current executed file, and changes its name to 'gov.csv'.
        #  `"/"+` here is because splitting the file name removes a "/" in front
        # path_to_table = "/"+os.path.join(*(__file__.split("/")[:-1]), "gov.csv")

        log.info("Writing down found bad guys into %s", path_to_save_directory)
        create_table(collected_data, os.path.join(path_to_save_directory, TABLE_NAME))


