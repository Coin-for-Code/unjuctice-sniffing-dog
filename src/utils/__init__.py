import logging
import os

import pandas as pd

LOGGER_NAME = "sillybaka"
TABLE_NAME = "gov.csv"

# TODO: The path for the temp folder shouldn't be hardcoded. For now changing the location of helper_stuff.py file needs
#  special attention to change the location of the root folder
# TEMP_PATH = "/".join(__file__.split("/")[:-1])
# os.makedirs(TEMP_PATH+"/temp", exist_ok=True)
# For topic filtering
# TOPIC_KEYWORDS = (
#     'розтрата бюджетних коштів', 'кумівство', 'привласнення', 'прозорість діяльності', 'недостовірні дані',
#     'захист інтересів', 'злочинець', "родинні зв'язки", 'економічні правопорушення', 'внутрішні розслідування',
#     'спонсорство', 'громадська безпека', 'зловживання правом', 'зловживання активами', 'корупційні дії',
#     'незаконні прибутки', 'розкриття інформації', 'приватні активи', 'офіційний контроль', 'правова відповідальність',
#     'порушення прав', 'державні фінанси', 'інсайдер', 'таємні платежі', 'антикорупційний аудит', 'державні органи',
#     'корупційна схема', 'корупційні схеми', 'підкуп', 'державна зрада', 'відшкодування', 'антикорупційна політика',
#     'позовна діяльність', 'спеціальні витрати', 'підробка документів', 'секретна інформація',
#     'зловживання службовим становищем', 'конфлікт інтересів', 'непрозорі договори', 'службові зловживання',
#     'розкрадання активів', 'нецільове використання коштів', 'незаконна вигода', 'службовий злочин', 'розслідування',
#     'розтратники', 'захист прав', 'антикорупційний захист', 'підозра', 'економічна злочинність',
#     'корупційна діяльність',
#     'державне регулювання', 'державний апарат', 'корупційні угоди', 'відмивання', 'розкрадання фондів',
#     'фінансова відповідальність', 'секретні рахунки', 'зловживання владою', 'державні інститути', 'хабарництво',
#     'незаконне привласнення', 'незаконне використання', 'правопорушення', 'громадські активи', 'хабарники',
#     'неправомірна вигода', 'злочини проти держави', 'незалежний аудит', 'бенефіціар', 'контрабанда', 'державна служба',
#     'приватизація', 'кримінальний елемент', 'благодійні фонди', 'офшорна діяльність', 'державні послуги',
#     'економічні злочини', 'прямий вплив', 'комерційні угоди', 'посадова особа', 'незаконні угоди',
#     'незаконна діяльність',
#     'офшорні рахунки', 'тіньовий ринок', 'таємний фонд', 'лобіювання', 'державні ресурси', 'незаконні дотації',
#     'посадовці',
#     'кримінальні схеми', 'незаконне фінансування', 'розкрадання фінансів', 'антикорупційні дії', 'корупційні ризики',
#     'антикорупційна діяльність', 'дотримання вимог', 'фальсифікація', 'розтрата', 'розкрадання ресурсів',
#     'відмивання грошей', 'обман', 'державні інтереси', 'зловживання', 'незаконний вплив', 'дискримінація',
#     'фінансові порушення', 'провокація злочину', 'державні структури', 'хабар', 'недобросовісні дії',
#     'державне управління',
#     'надання послуг', 'маніпуляції з документами', 'справи про корупцію', 'зловживання повноваженнями',
#     'державне фінансування', 'безпека активів', 'тіньова економіка', 'бюрократичні злочини', 'корупція',
#     'державна підтримка', 'таємні угоди', 'антикорупційні заходи', 'недержавні фінанси', 'недбалість',
#     'службова недбалість', 'державний борг', 'комісійні', 'державні установи', 'правове регулювання',
#     'корупційні злочини',
#     'незаконне збагачення', 'захоплення ресурсів', 'корупційний скандал', 'державний бюджет', 'громадські інтереси',
#     'влада', 'незаконні дії', 'посадовий злочин', 'недотримання етики', 'шахрайство', 'недекларовані активи',
#     'секретні операції', 'корупційна змова', 'прозорість витрат', 'порушення законодавства', 'розслідування справ',
#     'державне правопорушення', 'державний аудит', 'декларування', 'корупційна політика', 'іноземні активи',
#     'професійна етика', 'державні фонди', 'корупціонер', 'державна політика', 'фінансовий контроль', 'офіційні особи',
#     'офшорні угоди', 'управління активами', 'незаконні схеми', 'декларування активів', 'антикорупційний комітет',
#     'прозорість', 'таємні операції', 'захист громадян', 'недостатній контроль', 'недоцільні витрати',
#     'кримінальна відповідальність', 'таємні рахунки', 'антикорупційна служба')

TOPIC_KEYWORDS = ['фінансові махінації', 'розтрата бюджетних коштів', 'підозра на корупційне діяння', 'угода', 'службове підроблення',
    'злочинець', 'відмова у перевірці', 'відмивання активів', 'маніпуляції з податками',
    'незаконне управління активами',
    'незаконні витрати', 'фіктивне планування', 'протизаконна власність', 'незаконне управління коштами',
    'неправомірне використання ресурсів', 'державні змови', 'незадекларовані активи', 'перекваліфікація',
    'незаконний обіг коштів', 'корупційна схема', 'обвинувачення', 'державна зрада', 'підозрюється', 'корупційний',
    'підкуп', 'розтрати', 'маніпуляції бюджетом', 'відчуження майна', 'порушення порядку декларування',
    'порушення процедури закупівель', 'зловживання службовим становищем', 'злочин', 'отримання підозрілих коштів',
    'отримання вигоди', 'незаконна вигода', 'зловживання довірою', 'неправомірне рішення суду',
    'порушення правопорядку']

log = logging.getLogger(LOGGER_NAME)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


def create_table(data, path_to_table, is_excel=False):
    """
    Создает или обновляет таблицу в формате CSV или Excel на основе переданных данных.

    :param data: Список кортежей с данными для добавления в таблицу.
                 Каждый кортеж должен содержать (имя, дата, ссылка на статью, краткое описание).
    :param path_to_table: Путь к файлу таблицы.
    :param is_excel: Если True, будет загружен и сохранен файл Excel.
    """

    # Заголовки столбцов
    headers = ["Имя", "Ссылка на статью", "Дата"]

    # Проверка на наличие файла и загрузка данных
    table_data = None
    if os.path.isfile(path_to_table):
        if is_excel:
            table_data = pd.read_excel(path_to_table)
        else:
            table_data = pd.read_csv(path_to_table)
    else:
        with open(path_to_table, "w") as table:
            pass

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


def create_excel_table(path_to_table,names, date, url):
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
    file_name = path_to_table

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
        workbook = writer.book
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
            worksheet.write(row_num, 2, combined_data.at[row_num - 1, 'URL'])  # URL без цвета


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
