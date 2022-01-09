import os.path
import spacy
from urllib.parse import urlparse

utils_nlp = spacy.load('en_core_web_md')


def get_product_name_from_url(url: str):
    """
    Extracts the name of the product from the Amazon url.
    :param url: url of the Amazon product page
    :return: the name of the product
    """
    path = urlparse(url).path
    while os.path.dirname(path) != '/':
        path = os.path.dirname(path)
    if path and path[0] == "/":
        path = path[1:]
    return path


def get_rating_from_string(rating: str) -> float:
    """
    Converts product ratings from string to float.
    :param rating: the string with product rating.
    :return: a float number representing the product rating.
    """
    if not rating:
        return 0.0
    rating_list = rating.split()
    rating_str = rating_list[0].strip()
    try:
        return float(rating_str)
    except:
        return 0.0


def clean_pro_con_item(item: str):
    try:
        item = item.strip()
        token = utils_nlp(item)[0]
        if token.is_currency:
            item = "money"
            token = utils_nlp(item)[0]
        if token.pos_ not in ["SYM", "NOUN", "VERB", "PROPN"]:
            return None
        return token.lemma_
    except:
        return None


def clean_pro_con_attr(item: str):
    try:
        item = item.strip()
        token = utils_nlp(item)[0]
        if token.pos_ not in ["ADJ", "NOUN", "VERB"]:
            return None
        return token.lemma_
    except:
        return None


def switch_label_value(label: int):
    if label == 5:
        return 1
    if label == 4:
        return 2
    if label == 2:
        return 4
    if label == 1:
        return 5
    return label
