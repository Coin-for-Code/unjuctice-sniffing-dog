import os
import pandas as pd

def serialize_small_table(data, path_to_table, is_excel=False):
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

# Пример использования
data = [
    ("Иван Ивангов", "2024-11-10", "http://example.com/article3", "Краткое описание 3"),
    ("Петр Бухлов", "2024-11-11", "http://example.com/article4", "Краткое описание 4")
]

serialize_small_table(data, 'articles.xlsx', is_excel=True)