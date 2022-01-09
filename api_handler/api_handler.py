import json
from api_handler.base_handler import BaseHandler
from processor.processor import extract_pro_con
from processor.restaurant_processor import extract_pro_con_restaurant
from service.const import AVAILABLE_SERVICE_KEYS_LIST


class ProConHandler(BaseHandler):
    def post(self):

        req_body = json.loads(self.request.body)
        try:
            key = self.get_argument("key", default="", strip=True)
            product_url = req_body["url"]
        except:
            self.reply_client(status_code=400, data={})
            return

        if key not in AVAILABLE_SERVICE_KEYS_LIST:
            self.reply_client(status_code=400, data={})
            return

        # Run pro-con service
        pro_con_data = extract_pro_con(url=product_url)
        if not pro_con_data:
            self.reply_client(status_code=400, data={})
            return

        # Reply back to client
        self.reply_client(status_code=200, data=pro_con_data)


class ProConRestaurantHandler(BaseHandler):
    def post(self):

        req_body = json.loads(self.request.body)
        try:
            key = self.get_argument("key", default="", strip=True)
            restaurant_name = req_body["restaurant_name"]
            city = req_body["city"]
            max_num_reviews = req_body["max_num_reviews"]
        except:
            self.reply_client(status_code=400, data={})
            return

        if key not in AVAILABLE_SERVICE_KEYS_LIST:
            self.reply_client(status_code=400, data={})
            return

        # Run pro-con service for restaurants
        pro_con_data = extract_pro_con_restaurant(name=restaurant_name, city=city, max_num_reviews=max_num_reviews)
        if not pro_con_data:
            self.reply_client(status_code=400, data={})
            return

        # Reply back to client
        self.reply_client(status_code=200, data=pro_con_data)
