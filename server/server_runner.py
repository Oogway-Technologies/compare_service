import asyncio
import logging
import tornado.ioloop
from server.server import AIAPIWebApp


def run_server(server_port: int):
    # Create the event loop spawning up the tornado server
    asyncio.set_event_loop(asyncio.new_event_loop())

    server_app = AIAPIWebApp()
    server_app.listen(server_port)

    # Start the server loop
    try:
        logging.info("Start server")
        tornado.ioloop.IOLoop.current().start()
    except Exception as e:
        logging.exception(e)
