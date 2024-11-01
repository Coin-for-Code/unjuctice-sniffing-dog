import copy
from collections import defaultdict
from src import *
from textblob import TextBlob
import spacy

import requests
from src.site_scrapping import scrap_text_from_article

NLP_MODEL = "uk_core_news_lg"

CRIME_KEY_WORDS = (
    'фінансові махінації', 'розтрата бюджетних коштів', 'підозра на корупційне діяння', 'угода', 'службове підроблення',
    'злочинець', 'відмова у перевірці', 'відмивання активів', 'маніпуляції з податками',
    'незаконне управління активами',
    'незаконні витрати', 'фіктивне планування', 'протизаконна власність', 'незаконне управління коштами',
    'неправомірне використання ресурсів', 'державні змови', 'незадекларовані активи', 'перекваліфікація',
    'незаконний обіг коштів', 'корупційна схема', 'обвинувачення', 'державна зрада', 'підозрюється', 'корупційний',
    'підкуп', 'розтрати', 'маніпуляції бюджетом', 'відчуження майна', 'порушення порядку декларування',
    'порушення процедури закупівель', 'зловживання службовим становищем', 'злочин', 'отримання підозрілих коштів',
    'отримання вигоди', 'незаконна вигода', 'зловживання довірою', 'неправомірне рішення суду',
    'порушення правопорядку',
    'контроль без повноважень', 'недопуск перевірки', 'порушення правил безпеки', 'фінансовий шахрай',
    'корупційна діяльність', 'перевищення службових повноважень', 'привласнення коштів', 'несанкціоновані виплати',
    'неправомірний дохід', 'зловживання владою', 'незаконний дохід', 'хабарництво', 'правопорушення', 'сумнівні активи',
    'порушення закону про бюджет', 'недотримання процедури закупівель', 'махінації', 'неправомірна вигода',
    'порушення закону', 'приховування зарплати', 'незаконне привласнення майна', 'контрабанда', 'порушив',
    'відмивання коштів', 'приватизація', 'маніпуляції з розподілом ресурсів', 'декларування неправдивих даних',
    'звинувачений', 'незаконна діяльність', 'відмивання державних коштів', 'фіктивне декларування доходів',
    'місцева корупція', 'фінансове шахрайство', 'співучасть', 'зловживання іноземною допомогою',
    'незадекларовані кошти',
    'взято під варту', 'декларував', 'незаконна діяльність державних службовців', 'державна змова',
    'незаконне фінансування', 'фіктивні угоди', 'службове перевищення', 'службова халатність',
    'незаконне розподілення коштів', 'фальсифікація', 'розтрата', 'розкрадання ресурсів', 'відмивання грошей',
    'липовий контракт', 'підроблені документи', 'ухилення від податків', 'затриманий', 'зловживання',
    'незаконний вплив',
    'незаконні трансакції', 'маніпуляції з бюджетом', 'розкрадання допомоги', 'приховування боргів', 'службова змова',
    'хабар', 'розкрадання', 'обвинувачена', 'неправомірні перекази', 'підозра на хабар',
    'застосування протиправних дій',
    'недостовірна інформація', 'отримання відкатів', 'придбання активів', 'незаконний продаж майна',
    'корупційні діяння',
    'злочинна діяльність', 'хабародавство', 'незаконний прибуток', 'фіктивне підприємництво', 'приховування доходів',
    'незаконне планування', 'фіктивні звіти', 'хабарник', 'кримінальні дії', 'порушення фінансової звітності',
    'отримання неправомірної вигоди', 'відкат', 'обвинувачений', 'недотримання законодавства', 'підозрюваний',
    'злочинність', 'порушення фінансової дисципліни', 'зловживання повноваженнями', 'відмив активів',
    'розтрати державних коштів', 'неналежне витрачання бюджету', 'внесення недостовірних даних', 'незаконно',
    'корупція',
    'незаконний бізнес', 'протизаконне отримання коштів', 'недобросовісність', 'фіктивне інвестування', 'обхід законів',
    'контрабанда ліків', 'відмивання капіталу', 'контрабанда зброї', 'висунення підозри', 'службова недбалість',
    'неправомірна власність', 'комісійні', 'відмова від декларування', 'приховування активів', 'податкове шахрайство',
    'незаконне збагачення', 'недекларування', 'підробка', 'корупційний скандал', 'державний бюджет',
    'неправомірне рішення',
    'незаконне використання ресурсів', 'маніпуляції з валютними операціями', 'приховування джерел доходів',
    'незаконні дії',
    'шахрайство', 'змова з метою привласнення', 'перевищення державних витрат', 'державні махінації',
    'нерегламентовані кошти', 'декларація', 'розкрадання державного майна', 'прикриття активів', 'політична корупція',
    'незаконні виплати', 'службові злочини', 'обман держави', 'фіктивні контракти', 'співпраця', 'ухилення',
    'розкрадання державних фондів', 'фіктивні працівники', 'таємна змова', 'порушення конкурсу', 'корупціонер',
    'затримано',
    'незаконне розподілення ресурсів', 'недобросовісний', 'фіктивна власність', 'відмивання іноземної валюти', 'змова',
    'посередництво', 'підозрілі контракти', 'фіктивні дані', 'перевищення дозволеного бюджету', 'збагачення',
    'посадовець під підозрою')


def is_same_person(person_a, person_b, nlp_model=None):
    """
    This function will smartly compare the two persons, to decide whatever they are the same or not. **This method is
    prompt to errors** due:

    - The acceptance level derived from experimental data,
    - If they share common names they are considered the same person
    :param person_a: The person to compare
    :param person_b: The person to compare
    :param nlp_model: Natural language processing model, loads default one, if None
    :return: True when the persons are the same, otherwise False
    """
    # 0.75 is the similarity score, and is got from experimental data
    acceptance_level = 0.75
    if nlp_model is None:
        nlp_model = spacy.load(NLP_MODEL)

    similarity_score = nlp_model(person_a.lemma_).similarity(nlp_model(person_b.lemma_))

    # If the lemmatized names are the same, it is the same guy
    if person_a.lemma_ == person_b.lemma_:
        return True
    # If the names contain the same words, very dangerous, as two people with different family names are considered one
    elif not set(person_a.lemma_.split()).isdisjoint(set(person_b.lemma_.split())):
        return True
    # If the level of similarity is acceptable, we consider persons to be the same
    elif similarity_score > acceptance_level:
        return True
    return False


def identify_criminals(text):
    context_depth = 10
    log.debug("Analysing article with context_depth set to %d", context_depth)
    nlp = spacy.load(NLP_MODEL)
    analysed_text = nlp(text)
    persons = [entity for entity in analysed_text.ents if entity.label_ == "PER"]
    # raw_persons = persons.copy()
    log.debug("Found %d named persons", len(persons))

    # TODO: Move this into a separate function, and check the O(?) of this algorithm
    # Will create clean data of entities present and their context
    collected_persons = defaultdict(list)
    for person in persons:
        # Gathering context
        context_window_beginning = max(person.start - round(context_depth / 2), 0)
        context_window_closure = min(person.end + round(context_depth / 2), len(text))
        context = analysed_text[context_window_beginning:context_window_closure]

        # Check if the item is not already in unique_list using the is_equal function

        temp = {}
        for existing_persona in collected_persons.keys():
            temp[existing_persona] = is_same_person(person, existing_persona, nlp)

        if not any(temp.values()):
            # In case the person is not a duplicate
            collected_persons[person].append(context)
        else:
            # IN case the person has a duplicate
            original_person = list(filter(lambda key: temp[key] is True, temp))[0]
            collected_persons[original_person].append(context)

    # Check if persons are crime related
    corrupted_governors = []
    for person, contexts in collected_persons.items():
        for context in contexts:
            if any(word in context.text.lower() for word in CRIME_KEY_WORDS):
                corrupted_governors.append(person.text)
                break

    log.debug("Found following corrupt people: %s", corrupted_governors)

    return corrupted_governors

        # For better times
        #     # Arithmetic average
        #     context_arith_likelihood_score = 0
        #     for evaluate_word in CRIME_KEY_WORDS:
        #         context_arith_likelihood_score += context.similarity(nlp(evaluate_word))
        #     context_arith_likelihood_score /= len(CRIME_KEY_WORDS)
        #
        #     # Geometric average
        #     context_geo_likelihood_score = 1
        #     for evaluate_word in CRIME_KEY_WORDS:
        #         context_geo_likelihood_score *= context.similarity(nlp(evaluate_word))
        #     context_geo_likelihood_score **= 1 / len(CRIME_KEY_WORDS)
        #
        #     arith_likelihood_score += context_arith_likelihood_score
        #     geo_likelihood_score += context_geo_likelihood_score
        # arith_likelihood_score /= len(contexts)
        # geo_likelihood_score **= 1/len(contexts)

        # More verbose log output
        # log.debug("Evaluated arithmetic likelihood score: %d and geometric likelihood score: %d",
        #           arith_likelihood_score, geo_likelihood_score)
        # log.debug("Evaluated arith/geo scores for %s: %f/%f", person, arith_likelihood_score, geo_likelihood_score)


def is_article_on_topic(url):
    """
    Will search for keywords to filter needed articles from unrelated. Keep it stupid, but simple
    :param url: The url of an article to check
    :return: True if article contains the keywords, otherwise False
    :raise requests.exceptions.RequestException`: if the ``qhttp`` request is bad
    """
    try:
        log.debug("Filtering (%s) on governors crime topics", url)
        article_text = scrap_text_from_article(url)

        # Проверяем на совпадение с ключевыми словами
        for keyword in TOPIC_KEYWORDS:
            if keyword.lower() in article_text:
                log.debug("Article (%s) have right topic", url)
                return True
    except requests.exceptions.RequestException as bad_req:
        log.debug("Article (%s) is unreachable", url)
        return False

    log.debug("Article (%s) doesn't have the right topic", url)
    return False
