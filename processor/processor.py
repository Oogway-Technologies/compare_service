import string
from operator import itemgetter
from processor.pro_con_extractor import (apply_extraction, get_compound_pairs, pro_con_gpt3_extractor)
from processor.language_models import (classify_pro_con_category_and_sentiment, classify_pro_con,
                                       extreme_summarize_text, get_title_and_summary_sentiment, summarize_text)
from processor.scraper import spider_scrape
from processor.utils import (clean_pro_con_attr, clean_pro_con_item, get_product_name_from_url, get_rating_from_string,
                             switch_label_value)
from pymongo import MongoClient
from service.const import *


def get_pro_con_from_mongodb(url: str, pc_collection):
    """
    Fetches data from MongoDB if exists.
    :param url: the url of the product to fetch.
    :param pc_collection: the MongoDB collection to query.
    :return: fetched data
    """
    product_name = get_product_name_from_url(url)

    query = {
        'prod': product_name
    }
    prod_data = pc_collection.find_one(query)
    return prod_data


def run_basic_pro_con_analysis(review_info: dict, use_title_in_summary: bool = False) -> dict:
    """
    Runs pro-con analysis given review MetaData.
    Some of the analysis include sentiment, pro-con classification, etc.
    :param review_info: the dictionary of review MetaData.
    :param use_title_in_summary: whether or not to use the title when summarizing reviews.
    :return: a dictionary containing the pro-con analysis
    """
    # Collect all the text for all reviews and summarize them
    merged_titles = ""
    merged_titles_list = list()
    merged_reviews = ""
    merged_review_list = list()
    best_review = {"rating": 0.0, "review": list()}
    worst_review = {"rating": 5.0, "review": list()}
    for review in review_info['reviews']:
        # For each review, get the corresponding text and extract the review
        title_text = review['title'].strip()
        review_text = review['review'].strip()

        # Capture best/worst review
        rating_text = review['rating']
        rating = get_rating_from_string(rating_text)
        if rating >= best_review['rating']:
            best_review['rating'] = rating
            best_review['review'].append([rating, title_text])
        if rating <= worst_review['rating']:
            worst_review['rating'] = rating
            worst_review['review'].append([rating, title_text])

        # Merge titles for summary
        if title_text:
            if title_text[-1] not in string.punctuation:
                title_text += '.'
            merged_titles += title_text + " "
            merged_titles_list.append(title_text)

        # Merge reviews for summary
        if review_text:
            if review_text[-1] not in string.punctuation:
                review_text += '.'
            if use_title_in_summary:
                merged_reviews += title_text + ' ' + review_text + ' '
            else:
                merged_reviews += review_text + ' '
            merged_review_list.append(review_text)

    # Get titles summary and simplify it
    title_summary = summarize_text(merged_titles)
    title_summary_simplified = extreme_summarize_text(title_summary)

    # Get reviews summary
    review_summary = summarize_text(merged_reviews, num_sentences=20)

    # Sort reviews
    pos_ratings = best_review['review']
    pos_ratings = sorted(pos_ratings, key=itemgetter(0))
    neg_ratings = worst_review['review']
    neg_ratings = sorted(neg_ratings, key=itemgetter(0))

    # Return review summarization
    review_data = dict()
    review_data['title'] = title_summary_simplified
    review_data['title_sum'] = title_summary
    review_data['all_titles'] = merged_titles_list
    review_data['summary'] = review_summary
    review_data['reviews'] = merged_review_list
    review_data['best_review'] = pos_ratings[-1]
    review_data['worst_review'] = neg_ratings[-1]

    # Return the review data
    return review_data


def get_pro_con_map(review_data, use_generative_model: bool = True):
    """
    Extract pros and cons from reviews.
    By default, this function calls GPT-3 to extract
    pros and cons from a given review.
    Note: currently extracts pros and cons from review titles.
    This still works reasonably well and it is cheaper.
    :param review_data: review MetaData
    :param use_generative_model: if True, use GPT-3 to extract pros-cons.
    If False, runs regex analysis to extract attributes for nouns and use
    those as pros-cons.
    :return: the list of pros and cons
    """
    if use_generative_model:
        pro_con_list = list()
        for title in review_data['all_titles']:
            pro_con_list += pro_con_gpt3_extractor(title)
        return pro_con_list

    title_sum = review_data['title_sum']
    review_sum = ' '.join(review_data['all_titles'])
    pro_con_list = apply_extraction(text=title_sum)
    pro_con_list += get_compound_pairs(text=title_sum)
    pro_con_list += apply_extraction(text=review_sum)
    pro_con_list += get_compound_pairs(text=review_sum)

    # Store procon in map
    pro_con_map = dict()
    for pro_con in pro_con_list:
        pc = pro_con[0]
        pc = clean_pro_con_item(pc)
        if pc is None:
            continue
        if pc not in pro_con_map:
            pro_con_map[pc] = set()
        attr = clean_pro_con_attr(pro_con[1])
        if attr is None:
            continue
        pro_con_map[pc].add(attr)
    return pro_con_map


def get_sentiment_map(review_data) -> dict:
    """
    Runs sentiment analysis on reviews to determine the overall
    sentiment towards the given product.
    :param review_data: the review data.
    :return: a map of sentiments towards the product
    """
    title_sum = review_data['title_sum']
    review_sum = review_data['summary']

    sentiment_map = dict()
    sentiment_title_prediction, sentiment_sum_prediction = get_title_and_summary_sentiment(title_sum=title_sum,
                                                                                           review_sum=review_sum)
    for sentiment in sentiment_title_prediction[0] + sentiment_sum_prediction[0]:
        if sentiment["score"] > 0.1:
            sentiment_label = sentiment["label"]
            if sentiment_label not in sentiment_map:
                sentiment_map[sentiment_label] = list()
            sentiment_map[sentiment_label].append(sentiment["score"])
    return sentiment_map


def analyze_gen_pro_con(pro_con_list: list):
    pos_label = 'pos'
    neg_label = 'neg'
    category_pro_con_map = dict()
    category_pro_con_map[pos_label] = list()
    category_pro_con_map[neg_label] = list()
    for pro_con in pro_con_list:
        label = classify_pro_con(pro_con, pos_label, neg_label)
        if label:
            category_pro_con_map[label].append(pro_con)
    return category_pro_con_map


def analyze_pro_con(pro_con_map):
    """
    Analyze and classify pros and cons according to their product review topic.
    :param pro_con_map: pros and cons map.
    :return: two maps: (1) category counter map, and category pros-cons map
    """
    category_ctr_map = dict()
    category_pro_con_map = dict()
    attr_score = dict()

    pos_label = 'pos'
    neg_label = 'neg'
    category_pro_con_map[pos_label] = dict()
    category_pro_con_map[neg_label] = dict()
    for cat in CANDIDATE_PROD_LABELS:
        category_ctr_map[cat] = {'ctr': 0, 'num_entries': 0}
    for key, val in pro_con_map.items():
        for text in val:
            attr = text + ' ' + key

            # Find the category of the pro-con
            score, label, categories_list = classify_pro_con_category_and_sentiment(attr)

            # Store the score
            attr_score[text] = score
            label_value = int(label.split()[0].strip())

            # Modify incorrect sentiments for price
            if key in PRICE_CAT and text in PRICE_RANGE:
                label_value = switch_label_value(label_value)

            # Add voting counter to the category
            for cat in categories_list:
                category_ctr_map[cat]['ctr'] += label_value
                category_ctr_map[cat]['num_entries'] += 1
            if label_value != 3:
                if label_value > 3:
                    label = pos_label
                else:
                    label = neg_label
                if key not in category_pro_con_map[label]:
                    category_pro_con_map[label][key] = list()
                category_pro_con_map[label][key].append([text, attr_score[text]])

    # Calculate percentage for scores in categories
    for key, value in category_ctr_map.items():
        num_entries = value['num_entries']
        ctr_value = value['ctr']
        value['perc'] = 0
        if num_entries == 0:
            continue
        min_val = 1 * num_entries
        max_val = 5 * num_entries

        # Scale values
        ctr_value -= min_val
        max_val -= min_val

        # Calculate percentage
        value['perc'] = (ctr_value / max_val) * 100.0

    # Return values
    return category_ctr_map, category_pro_con_map


def extract_pro_con(url: str) -> dict:
    """
    Given the url of an Amazon product page, extracts pro-con
    data for that product.
    This function acts as "fetch or create", meaning that
    it firsts tries to retrieve the data from MongoDB.
    If the data is not present, it scrapes it from the web,
    caches the results, and returns the data.
    :param url: a url of an Amazon product.
    :return: the dictionary of pro-con MetaData
    """
    # Connect to MongoDB
    mongo_db_client = MongoClient(MONGO_DB_URL)
    pc_db = mongo_db_client.comparison_engine
    pc_metadata = pc_db.review_metadata

    # Step 0: check if the object has been scraped already
    stored_review_data = get_pro_con_from_mongodb(url, pc_metadata)
    if stored_review_data is not None:
        # Drop MongoDB _id
        del stored_review_data["_id"]
        return stored_review_data

    # Step 1: scrape the web page to get reviews
    review_info = spider_scrape(url=url, num_review_pages=NUM_REVIEW_PAGES_TO_SCRAPE)

    # Step 2: extract review summary
    review_data = run_basic_pro_con_analysis(review_info)

    # Step 3: create a pro-con map
    gen_model = False
    pro_con_map = get_pro_con_map(review_data, use_generative_model=gen_model)

    # Step 3.b: create a pro-con list using a generative model
    gen_model = True
    pro_con_list = get_pro_con_map(review_data, use_generative_model=gen_model)

    # Ste 4: get overall sentiment
    sentiment_map = get_sentiment_map(review_data)

    # Step 5: process pro-con for product analysis
    category_ctr_map, category_pro_con_map = analyze_pro_con(pro_con_map)

    # Step 5.b: process generated pro-con for product analysis
    category_gen_pro_con_map = analyze_gen_pro_con(pro_con_list)

    # Add sentiment and pro-con analysis to the review data map
    review_data["meta"] = review_info["meta"]
    review_data["sentiment_map"] = sentiment_map
    review_data["category_map"] = category_ctr_map
    review_data["pro_con_map"] = category_pro_con_map
    review_data["gen_pro_con_map"] = category_gen_pro_con_map
    review_data["url"] = url

    # Before returning, store the data to MongoDB
    product_name = get_product_name_from_url(url)
    review_data['prod'] = product_name
    pc_metadata.insert_one(review_data)

    # Return the full analysis
    if "_id" in review_data:
        del review_data["_id"]

    return review_data
