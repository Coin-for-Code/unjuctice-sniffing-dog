import requests
import gzip
import xml.etree.ElementTree as ET
from io import BytesIO

def parse_sitemap(url):
    response = requests.get(url)
    
    # Проверяем, gzip ли это файл (по первым двум байтам)
    if url.endswith('.gz') and response.content[:2] == b'\x1f\x8b':  # Проверка gzip по magic number
        try:
            # Если это gzip, пытаемся распаковать его
            with gzip.GzipFile(fileobj=BytesIO(response.content)) as f:
                xml_content = f.read()
        except gzip.BadGzipFile:
            print(f"Ошибка: {url} не является правильным gzip-файлом.")
            return []  # Возвращаем пустой список если файл не может быть распакован
    else:
        # Иначе обрабатываем как обычный XML
        xml_content = response.content
    
    root = ET.fromstring(xml_content)
    links = []

    # Проверка типа XML (sitemap или urlset)
    if root.tag.endswith('sitemapindex'):
        # Если это индекс сайтмапов, то проходим по каждому дочернему сайтмапу
        for sitemap in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap"):
            sub_sitemap_url = sitemap.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
            links.extend(parse_sitemap(sub_sitemap_url))  # Рекурсивный вызов
    elif root.tag.endswith('urlset'):
        # Если это сайтмап с ссылками, то собираем ссылки на статьи
        for url_elem in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
            loc = url_elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
            links.append(loc)
    
    return links

# Пример использования
sitemap_url = 'https://lb.ua/sitemap.xml'
article_links = parse_sitemap(sitemap_url)

# Выводим количество найденных ссылок и первые 10 ссылок
print(f'Найдено {len(article_links)} статей.')
print(article_links[:10])

# Сохранение ссылок в файл
with open('article_links.txt', 'w', encoding='utf-8') as f:
    for link in article_links:
        f.write(f'{link}\n')