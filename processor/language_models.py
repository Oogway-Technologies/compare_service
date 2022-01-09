import json
import logging
from processor.hf_api import (call_hf_summarizer, call_hf_extreme_summarizer, call_hf_text_classification,
                              call_hf_zero_shot_classification, pin_hf_models)
from service.const import *
from summarizer import Summarizer
from transformers import pipeline


# Load the models all at once
glb_extract_summarizer = Summarizer()
glb_summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
glb_extreme_summarizer = pipeline("summarization", model="google/pegasus-xsum")
glb_classifier = pipeline("text-classification", model="nlptown/bert-base-multilingual-uncased-sentiment",
                          return_all_scores=True)
glb_zero_shot = pipeline("zero-shot-classification", model="typeform/distilbert-base-uncased-mnli")

# Note: another classifier that works fairly well is:
# glb_classifier = pipeline("text-classification", model='bhadresh-savani/distilbert-base-uncased-emotion',
#                           return_all_scores=True)

# Note: a better and more expensive tokenizer (instead of space tokenizer) is directly
# using the bert tokenizer
# glb_tokenizer = AutoTokenizer.from_pretrained("sshleifer/distilbart-cnn-12-6")
# res = glb_tokenizer.tokenize(review_text)


def pin_hugging_face_models():
    data = json.dumps({
        "pinned_models": [
            {"model_id": "sshleifer/distilbart-cnn-12-6", "compute_type": "cpu"},
            {"model_id": "google/pegasus-xsum", "compute_type": "cpu"},
            {"model_id": "nlptown/bert-base-multilingual-uncased-sentiment", "compute_type": "cpu"},
            {"model_id": "typeform/distilbert-base-uncased-mnli", "compute_type": "cpu"},

        ]
    })
    res = pin_hf_models(pinned_models_map=data)
    logging.info(json.dumps(res.json()))


def summarize_extractive_abstractive(text: str, num_sentences: int = 10):
    text = text.strip()
    text = glb_extract_summarizer(text, num_sentences=num_sentences)
    if USE_HF_API:
        text = call_hf_summarizer(text.strip())
    else:
        text = glb_summarizer(text.strip())
    summary = text[0]["summary_text"].strip()
    summary = summary.replace(' . ', '. ')
    return summary.strip()


def summarize_text(text: str, num_sentences: int = 10):
    if len(text.split()) > BERT_NUM_TOKEN_LIMIT:
        return summarize_extractive_abstractive(text, num_sentences)
    else:
        text = text.strip()
        try:
            if USE_HF_API:
                text_sum = call_hf_summarizer(text.strip())
            else:
                text_sum = glb_summarizer(text.strip())

            summary = text_sum[0]["summary_text"].strip()
            summary = summary.replace(' . ', '. ').strip()
        except:
            summary = ""

        # Try again on error
        if not summary:
            return summarize_extractive_abstractive(text, num_sentences)

        return summary


def extreme_summarize_text(text: str, num_sentences: int = 10):
    text = text.strip()
    if len(text.split()) > BERT_NUM_TOKEN_LIMIT:
        text = glb_extract_summarizer(text, num_sentences=num_sentences)
        if USE_HF_API:
            text = call_hf_extreme_summarizer(text.strip())
        else:
            text = glb_extreme_summarizer(text.strip())
    else:
        if USE_HF_API:
            text = call_hf_extreme_summarizer(text.strip())
        else:
            text = glb_extreme_summarizer(text.strip())

    summary = text[0]["summary_text"].strip()
    summary = summary.replace(' . ', '. ')
    return summary.strip()


def get_title_and_summary_sentiment(title_sum: str, review_sum: str):
    sentiment_title_prediction = [list()]
    sentiment_sum_prediction = [list()]
    if title_sum:
        if USE_HF_API:
            sentiment_title_prediction = call_hf_text_classification(title_sum)
        else:
            sentiment_title_prediction = glb_classifier(title_sum)

    if review_sum:
        if USE_HF_API:
            sentiment_sum_prediction = call_hf_text_classification(review_sum)
        else:
            sentiment_sum_prediction = glb_classifier(review_sum)

    return sentiment_title_prediction, sentiment_sum_prediction


def classify_pro_con(pro_con: str, pos_label: str, neg_label: str, threshold: int = 3) -> str:
    """
    Classifies the given pro-con as positive or negative according to
    its sentiment and given threshold.
    :param pro_con: the pro-con string
    :param pos_label: label to produce if the sentiment is positive.
    :param neg_label: label to produce if the sentiment is negative.
    :param threshold: value in [1-5] above which the sentiment is considered positive.
    :return: either pos_label or neg_label. If it cannot decide, return empty string
    """
    if USE_HF_API:
        res_sent = call_hf_text_classification(pro_con)
    else:
        res_sent = glb_classifier(pro_con)

    label = ''
    score = -1.0
    for sent in res_sent[0]:
        if sent['score'] > score:
            score = sent['score']
            label = sent['label']

    # Store the score
    label_value = int(label.split()[0].strip())
    if label_value != threshold:
        if label_value > threshold:
            label = pos_label
        else:
            label = neg_label

        # Return the label
        return label

    # Return the label
    return ""


def classify_pro_con_category_and_sentiment(attr: str, labels: list = CANDIDATE_PROD_LABELS):
    # Find the category of the pro-con
    if USE_HF_API:
        res_cat = call_hf_zero_shot_classification(attr, labels)
    else:
        res_cat = glb_zero_shot(attr, labels, multi_label=True)

    # Store the first category and the second if the delta score is less than 10%
    categories_list = [res_cat['labels'][0]]
    if res_cat['scores'][0] - res_cat['scores'][1] < 0.1:
        categories_list.append(res_cat['labels'][1])

    # Find vote and pro-con
    if USE_HF_API:
        res_sent = call_hf_text_classification(attr)
    else:
        res_sent = glb_classifier(attr)

    # Store the score given by the attribute
    label = ''
    score = -1.0
    for sent in res_sent[0]:
        if sent['score'] > score:
            score = sent['score']
            label = sent['label']

    return score, label, categories_list
