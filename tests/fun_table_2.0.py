import pandas as pd
import xlsxwriter
import os

def create_excel_table(names, date, url):
    """
    Создает или дополняет Excel таблицу с именами, датой и URL,
    окрашивая имена в зависимости от общего URL.

    :param names: Имя или массив имен.
    :param date: Дата.
    :param url: URL ссылка.
    """
    # Если передано одно имя, преобразуем его в список
    if isinstance(names, str):
        names = [names]

    # Создаем DataFrame из имен
    new_data = pd.DataFrame({
        'Имя': names,
        'Дата': date,
        'URL': url
    })

    # Проверяем существует ли файл
    file_name = 'output.xlsx'
    
    if os.path.isfile(file_name):
        # Если файл существует, читаем его
        existing_data = pd.read_excel(file_name)
        # Объединяем старые и новые данные
        combined_data = pd.concat([existing_data, new_data], ignore_index=True)
    else:
        # Если файла нет, используем только новые данные
        combined_data = new_data

    # Определяем количество повторений каждого URL
    url_counts = combined_data['URL'].value_counts()

    # Записываем данные в Excel
    with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
        combined_data.to_excel(writer, index=False, sheet_name='Лист1')

        # Получаем доступ к объекту workbook и worksheet
        workbook  = writer.book
        worksheet = writer.sheets['Лист1']

        # Форматирование заголовков
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D9EAD3',
            'border': 1
        })
        
        # Применяем форматирование к заголовкам
        for col_num, value in enumerate(combined_data.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Форматирование имен по общему URL
        url_colors = {}
        color_index = 0

        for row_num in range(1, len(combined_data) + 1):
            url = combined_data.at[row_num - 1, 'URL']
            name = combined_data.at[row_num - 1, 'Имя']

            if url_counts[url] > 1:  # Если URL встречается более одного раза
                if url not in url_colors:
                    color_index += 1
                    # Генерируем уникальный цвет для нового URL (можно использовать фиксированные цвета)
                    url_colors[url] = workbook.add_format({'bg_color': f'#{color_index * 111111 % 0xFFFFFF:06X}'})
                
                # Устанавливаем цвет для имени в первом столбце
                worksheet.write(row_num, 0, name, url_colors[url])  # Имя с цветом
            else:
                worksheet.write(row_num, 0, name)  # Имя без цвета

            worksheet.write(row_num, 1, combined_data.at[row_num - 1, 'Дата'])  # Дата без цвета
            worksheet.write(row_num, 2, combined_data.at[row_num - 1, 'URL'])   # URL без цвета

# Пример использования функции
create_excel_table(["Иван Иванов", "Петр Петров"], "2024-11-10", "http://example.com/article")
create_excel_table("Вова Вовічкин", "2024-11-09", "http://example.com/article2")
create_excel_table(["Алексей Алексеев", "Мария Мариева"], "2024-11-10", "http://example.com/article")
create_excel_table(["Алексей Алексеев", "Мария Мариева"], "2024-11-10", "http://example.com/article3")
create_excel_table("Чебурашка Чебурашкин", "2024-11-10", "http://example.com/article4")
create_excel_table("Вова Петренко", "2024-11-09", "http://example.com/article2")