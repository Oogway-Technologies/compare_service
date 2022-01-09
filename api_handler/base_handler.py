import logging
import tornado.web


class BaseHandler(tornado.web.RequestHandler):
    def data_received(self, chunk: bytes):
        pass

    def set_default_headers(self):
        # TODO limit origin to load balancer IP
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', '*')

    def reply_client(self, status_code: int, data: dict):
        if status_code != 200:
            logging.error(f"BaseHandler::reply_client - error {status_code}")
            self.send_error(status_code)
        else:
            self.write(data)
