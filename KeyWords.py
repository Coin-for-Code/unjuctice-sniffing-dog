import requests
from bs4 import BeautifulSoup

def check_keywords_in_article(url, keywords):
    try:
        # Получаем содержимое страницы
        response = requests.get(url)
        response.raise_for_status()  # Проверка на ошибки HTTP

        # Извлекаем текст статьи
        soup = BeautifulSoup(response.content, 'html.parser')
        article_text = soup.get_text().lower()  # Приводим текст к нижнему регистру

        # Проверяем на совпадение с ключевыми словами
        for keyword in keywords:
            if keyword.lower() in article_text:
                return True
    except Exception as e:
        print(f"Ошибка при обработке {url}: {e}")
    
    return False

def save_matching_articles(urls, keywords, output_file):
    matching_urls = []

    for url in urls:
        if check_keywords_in_article(url, keywords):
            matching_urls.append(url)

    # Сохраняем адреса статей в текстовый файл
    with open(output_file, 'w', encoding='utf-8') as f:
        for url in matching_urls:
            f.write(url + '\n')

# Пример использования
urls = [
    'https://www.epravda.com.ua/news/2023/10/9/705265/',
    # Добавьте другие URL
]

keywords = ['Саламалейкум', 'Биба']  # Замените на ваши ключевые слова
output_file = 'matching_articles.txt'

save_matching_articles(urls, keywords, output_file)
print("Адреса статей, совпадающие с ключевыми словами, сохранены в файле.")