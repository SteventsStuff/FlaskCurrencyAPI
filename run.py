import logging

from src.app import Application

logging.basicConfig(level=logging.DEBUG)


def create_app():
    application = Application(__name__)
    application.configure_app()
    return application.flask_app


app = create_app()
