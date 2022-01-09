import requests
import time
from service.const import *


def pin_hf_models(pinned_models_map: str):
    api_url = HUGGING_FACE_PINNED_MODELS_URL
    headers = {"Authorization": f"Bearer {HUGGING_FACE_API_TOKEN}"}

    # Put ALL the models to pin at once, this will override the previous values
    response = requests.post(api_url, headers=headers, data=pinned_models_map)
    return response


def hf_query(payload, api_url, headers):
    ctr = 0
    while True:
        response = requests.post(api_url, headers=headers, json=payload)
        status_code = response.status_code
        if status_code == 200:
            return response.json()
        else:
            if ctr > REQUEST_CTR_LIMIT:
                return {}
            ctr += 1
            time.sleep(REQUEST_SLEEP_TIME)


def call_hf_summarizer(text: str):
    api_url = HF_SUM_MODEL_URL
    headers = {"Authorization": f"Bearer {HUGGING_FACE_API_TOKEN}"}
    output = hf_query(
        payload={"inputs": text},
        api_url=api_url,
        headers=headers
    )
    return output


def call_hf_extreme_summarizer(text: str):
    api_url = HF_EXT_SUM_MODEL_URL
    headers = {"Authorization": f"Bearer {HUGGING_FACE_API_TOKEN}"}
    output = hf_query(
        payload={"inputs": text},
        api_url=api_url,
        headers=headers
    )
    return output


def call_hf_text_classification(text: str):
    api_url = HF_SENT_CLASS_MODEL_URL
    headers = {"Authorization": f"Bearer {HUGGING_FACE_API_TOKEN}"}
    output = hf_query(
        payload={"inputs": text},
        api_url=api_url,
        headers=headers
    )
    return output


def call_hf_zero_shot_classification(text: str, labels):
    api_url = HF_ZERO_SHOT_CLASS_MODEL_URL
    headers = {"Authorization": f"Bearer {HUGGING_FACE_API_TOKEN}"}
    output = hf_query(
        payload={"inputs": text, "parameters": {"candidate_labels": labels}},
        api_url=api_url,
        headers=headers
    )
    return output
