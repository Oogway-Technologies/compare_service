import tornado.web
from api_handler.api_handler import (ProConHandler, ProConRestaurantHandler)


class AIAPIWebApp(tornado.web.Application):
    def __init__(self):
        # Define the handlers answering requests from clients
        self.handlers = [
            (r"/pro_con", ProConHandler),
            (r"/pro_con_restaurant", ProConRestaurantHandler),
        ]
        super(AIAPIWebApp, self).__init__(self.handlers)
