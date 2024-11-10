import os

from src import log

import pandas as pd

def create_table(data, path_to_table, is_excel=False):
    """
    Создает или обновляет таблицу в формате CSV или Excel на основе переданных данных.

    :param data: Список кортежей с данными для добавления в таблицу.
                 Каждый кортеж должен содержать (имя, дата, ссылка на статью, краткое описание).
    :param path_to_table: Путь к файлу таблицы.
    :param is_excel: Если True, будет загружен и сохранен файл Excel.
    """
    
    # Заголовки столбцов
    headers = ["Имя", "Дата", "Ссылка на статью", "Краткое описание"]

    # Проверка на наличие файла и загрузка данных
    table_data = None
    if os.path.isfile(path_to_table):
        if is_excel:
            table_data = pd.read_excel(path_to_table)
        else:
            table_data = pd.read_csv(path_to_table)

    # Создание DataFrame из переданных данных
    df = pd.DataFrame(data, columns=headers)

    # Объединение с существующими данными, если они есть
    if table_data is not None:
        df = pd.concat([table_data, df], ignore_index=True)

    # Сохранение данных в файл
    if is_excel:
        df.to_excel(path_to_table, index=False)
    else:
        df.to_csv(path_to_table, index=False)

def serialize_small_table(data, path_to_table, is_excel=False):
    """

    :param data: The data to add to the table
    :param path_to_table: Path to the table file
    :param is_excel: If true would load and save an Excel file
    :return:
    """
    headers = ["Governors"]

    table_data = None
    # Add the data from the file
    if os.path.isfile(path_to_table):
        if is_excel:
            table_data = pd.read_excel(path_to_table)
        else:
            table_data = pd.read_csv(path_to_table)

    df = pd.DataFrame(data, columns=headers)
    if table_data is not None:
        df = pd.concat([table_data, df])
    if is_excel:
        df.to_excel(path_to_table, index=False)
    else:
        df.to_csv(path_to_table, index=False)


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
