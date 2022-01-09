from pathlib import Path
import yaml
import warnings

# Keys/passwords
CREDENTIALS_STR = 'credentials.yml'
CREDENTIALS_PATH = Path(CREDENTIALS_STR).resolve()

SCRAPINGBEE_KEY_STR = 'scrapingbee_key'
MONGODB_CREDENTIAL_STR = 'mongodb_credential_url'
HUGGING_FACE_KEY_STR = 'hugging_face_key'
OPEN_AI_KEY_STR = 'open_ai_key'

if CREDENTIALS_PATH.exists():
    with CREDENTIALS_PATH.open() as f:
        credentials = yaml.safe_load(f)
        if (MONGODB_CREDENTIAL_STR in credentials) and \
                (SCRAPINGBEE_KEY_STR in credentials) and \
                (HUGGING_FACE_KEY_STR in credentials) and \
                (OPEN_AI_KEY_STR in credentials):
            MONGO_DB_URL = credentials[MONGODB_CREDENTIAL_STR]
            SCRAPINGBEE_KEY = credentials[SCRAPINGBEE_KEY_STR]
            OPEN_AI_KEY = credentials[OPEN_AI_KEY_STR]
            HUGGING_FACE_API_TOKEN = credentials[HUGGING_FACE_KEY_STR]
            if (MONGO_DB_URL is None) or (SCRAPINGBEE_KEY is None) or (HUGGING_FACE_KEY_STR is None) or \
                    (OPEN_AI_KEY_STR is None):
                warnings.warn(f'Missing values in {CREDENTIALS_STR}. '
                              f'Please add yours or get the Oogway one from Brady or Federico.')
        else:
            warnings.warn(f'Missing keys in {CREDENTIALS_STR}')
else:
    raise RuntimeError(f'Missing {CREDENTIALS_STR}. Make one with the keys for the service '
                       f'and corresponding values or get the Oogway one from '
                       f'Brady or Federico.')

# Service
AMAZON_BASE_URL = 'https://www.amazon.com'
AVAILABLE_SERVICE_KEYS_LIST = ["oogway_test"]

# Scrapingbee url and key
SCRAPINGBEE_URL = 'https://app.scrapingbee.com/api/v1/'

# Processor
# Number of review pages to scrape.
# By default scrape only 1 page of reviews for any given product
NUM_REVIEW_PAGES_TO_SCRAPE = 1
# Limit on number of tokens for Bert summarizer.
# If greater than the limit, run extractive summarization before
# running abstract summarization
BERT_NUM_TOKEN_LIMIT = 800
# Candidate topic labels for product reviews
CANDIDATE_PROD_LABELS = ['customization', 'quality', 'price', 'features', 'look and feel', 'durability', 'efficiency',
                         'reliability', 'safety']
# Candidate topic labels for restaurant reviews
CANDIDATE_RESTAURANT_LABELS = ['atmosphere', 'food', 'service', 'price', 'other']
# Price category and range-price category used to revet sentiments
# for price topics
PRICE_CAT = ["cost", "payment", "price"]
PRICE_RANGE = ["high", "low", "little", "big"]

# OpenAI
# The GPT-3 prompt used to extract pros and cons from a review title
OPEN_AI_PROMPT = "I am a highly intelligent bot that extracts pros and cons from product reviews.\n\nReview: Dont " \
                 "last very long. Lightweight and comfy.\nPros and cons:\n1 - don't last long\n2 - lightweight and " \
                 "comfy\n\nReview: Love them! Great shoes if your going to be on your feet a lot!\nPros and " \
                 "cons:\n1 - great shoes\n\nReview: Support not there. Dont last very long.\nPros and cons:\n1 - " \
                 "don't have support\n2 - don't last long\n\nReview: Even better than I expected!\nPros and " \
                 "cons:\n1 - better than expected\n\nReview: Fit well and comfortable.\nPros and cons:\n1 - " \
                 "fit well\n2 - comfortable\n\nReview: Great shoe for the price!\nPros and cons:\n1 - " \
                 "great shoe\n\nReview: Support not there.\nPros and cons:\n1 - doesn't have support\n\nReview: " \
                 "terrible running shoe! Utter Trash.\nPros and cons:\n1 - terrible running shoe\n\nReview: " \
                 "Minimally adequate for astronomy - here's why\nPros and cons:\n1 - minimally adequate\n\nReview: " \
                 "My Favorite Binoculars. Not a toy! Real  binoculars! Good optics.\nPros and cons:\n1 - " \
                 "real binoculars\n2 - good optics\n\nReview: BUY THESE, YOU WON'T REGRET IT!!" \
                 "\nPros and cons:\n1 - good deal" \
                 "\n\nReview: Poorly made, no support, don’t breathe." \
                 "\nPros and cons:\n1 - poorly made\n2 - no support\n\nReview: Great binoculars for the " \
                 "backyard astronomer\nPros and cons:\n1 - great binoculars\n\nReview: "
# Restaurant prompt
OPEN_AI_RESTAURANT_PROMPT = "I am a highly intelligent bot that extracts pros and cons from restaurant reviews." \
                            "\n\nReview: There are so many options it was hard to decide on what to order. " \
                            "The portions are perfect for sharing. The pan con con tomate is so simple but so " \
                            "delicious. The atmosphere is clean, modern and bright. We've been several times and " \
                            "we will return again soon!\nPros and Cons:\n1 - many options\n" \
                            "2 - portions perfect for sharing\n3 - delicious food\n4 - clean, modern and " \
                            "bright atmosphere\n\nReview: Jamòn Iberico is a small plate that has a listed " \
                            "price of $24 for a small. The elote dish came with 4 halves of corn on the cob and " \
                            "bone marrow was very yummy. The mango lime soda mock-cocktail was just okay ." \
                            "\nPros and Cons:\n1 - small plates\n2 - yummy food\n3 - okay cocktails\n\nReview: " \
                            "The place comes off as a good neighborhood restaurant and bar with a casual vibe. " \
                            "It's a bit noisy indoors but no worse than most other casual dining places these days. " \
                            "The only knock on the place for me is the wine list. Food this good should be offered " \
                            "with wine that can complement it well .\nPros and Cons:\n1 - good neighborhood restaurant " \
                            "and bar\n2 - casual vibe\n3 - a bit noisy indoors\n4 - good food\n\nReview: " \
                            "Annette was an amazingly gracious server...so friendly and helpful. " \
                            "The eggplant rollini app was phenomenal. The ricotta was as light as a cloud. " \
                            "The salad was fresh and tasty... not a limp afterthought like at many other places. " \
                            "MAMMA MIA, THAT WAS BUONISSIMO!!\nPros and Cons:\n1 - friendly and helpful waiters " \
                            "\n2 - fresh and tasty food\n\nReview: I'm a regular at this go-to-to spot on " \
                            "Chambridge st. Couldent ask for a better option with convenient hours. The kicker? " \
                            "They have refried beans! 10/10. The kicker is that they have a refried bean! 10-10." \
                            "\nPros and Cons:\n1 - convenient hours\n2 - good refried beans\n\nReview: " \
                            "phenomenal food and service. phenomenal food & service. Nothing more needs to be said. " \
                            "5 stars. 5-star service. 5 star service. Food & Service. No need to say more than that. " \
                            "Nothing else needs to said. It's a great place to eat at the restaurant.\n" \
                            "Pros and Cons:\n1 - phenomenal food and service\n2 - 5 start service\n" \
                            "3 - great place to eat at the restaurant\n\nReview: "
# Suffix to append to the prompt to send to OpenAI
OPEN_AI_SUFFIX = '\nPros and cons:'
# Engine to use
OPEN_AI_ENGINE = "curie"

# HuggingFace
# Whether or not to call HuggingFace APIs
USE_HF_API = True
# How many times re-trying calling HuggingFace API
REQUEST_CTR_LIMIT = 4
# Sleep time (in sec.) between HuggingFace calls
REQUEST_SLEEP_TIME = 45

# HuggingFace pinned models usage
HUGGING_FACE_PINNED_MODELS_URL = "https://api-inference.huggingface.co/usage/pinned_models"
# Summarizer model
HF_SUM_MODEL_URL = "https://api-inference.huggingface.co/models/sshleifer/distilbart-cnn-12-6"
# Extreme summarizer model
HF_EXT_SUM_MODEL_URL = "https://api-inference.huggingface.co/models/google/pegasus-xsum"
# Sentiment classification model
HF_SENT_CLASS_MODEL_URL = "https://api-inference.huggingface.co/models/nlptown/bert-base-multilingual-uncased-sentiment"
# Zero-shot classification model
HF_ZERO_SHOT_CLASS_MODEL_URL = "https://api-inference.huggingface.co/models/typeform/distilbert-base-uncased-mnli"
