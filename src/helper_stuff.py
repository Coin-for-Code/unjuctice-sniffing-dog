from src import log, KEY_WORDS

import pandas as pd


def update_table(data, path_to_table, is_excel=False):
    """

    :param data: The data to add to the table
    :param path_to_table: Path to the table file
    :param is_excel: If true would load and save an Excel file
    :return:
    """
    table_data = pd.DataFrame([[], [], []], columns=["Governor", "Captured source", "Released source"])

    # Add the data from the file
    if is_excel:
        table_data = pd.concat([table_data, pd.read_excel(path_to_table)])
    else:
        table_data = pd.concat([table_data, pd.read_csv(path_to_table)])

    df = pd.DataFrame(data, columns=["Governor", "Captured source", "Released source"])
    if is_excel:
        df.to_excel(path_to_table, index=False)
    else:
        df.to_csv(path_to_table, index=False)


def dilated_page_pick(batch_size: int, site_pool):
    """
    This will create a batch of web urls from different news sites
    :param site_pool: The pool of all sites
    :param batch_size: the amount of urls in one batch
    """
    log.debug("Picking %d urls for analysis", batch_size)
    batch_of_urls = []
    for i in range(0, batch_size):
        # Inside the loop is the logic for picking the site for taking the webpage
        batch_of_urls.append(site_pool.get_url())
    links = list(filter(None, batch_of_urls))
    log.debug("Successfully picked %d urls. Batch completeness rate %d", len(links), len(links) / batch_size)
    return links


class EndOfProcess(Exception):
    pass


class OutOfArticles(Exception):
    """
    An exception to be raised when a news site runs out of articles.
    Has a reference to the emptied news site
    """

    def __init__(self, empty_site):
        """
        :param empty_site: The news site object that has run out of articles
        """
        self.empty_site = empty_site
        super().__init__()
