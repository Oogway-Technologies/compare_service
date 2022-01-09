import logging
from processor.language_models import pin_hugging_face_models
from server.server_runner import run_server

SERVER_PORT = 8001

# Set logger
root = logging.getLogger()
root.setLevel(logging.INFO)


def procon_service():
    # Prepare the models before running the service
    pin_hugging_face_models()

    # Forward call to the server runner
    run_server(SERVER_PORT)


if __name__ == '__main__':
    procon_service()
