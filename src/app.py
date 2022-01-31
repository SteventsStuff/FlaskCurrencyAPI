from http import HTTPStatus

from flask import Flask

# NOTE: it is IMPORTANT to all models here to create all tables
from .api.v1 import rate_api, currency_api
# todo: mb refact v1.views -> just v1 (__init__)
from .api.v1.views import errors_view as err
from .models import db
from .schemas.core import ma
from .constans import DB_URI
from config import Config


class Application:
    def __init__(self, name: str):
        self._app: Flask = Flask(name)

    def configure_app(self, config_object: Config = Config) -> None:
        # self._app.config.from_object(config_object)
        self._app.config['DEBUG'] = 'true'
        self._app.config['SERVER_NAME'] = 'vm-currency.com:5000'
        self._app.config['ENV'] = 'development'
        # NOTE: I do not remember why I did that, fuck...
        self._app.config['JSON_SORT_KEYS'] = False
        # db configs
        self._app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_URI}'
        self._app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # init_stuff
        self._init_db()
        self._init_marshmallow()

        # add routes
        self._register_blueprints()
        self._register_error_handlers()

    @property
    def flask_app(self) -> Flask:
        return self._app

    def _register_blueprints(self, ) -> None:
        self._app.register_blueprint(rate_api)
        self._app.register_blueprint(currency_api)

    def _register_error_handlers(self) -> None:
        self._app.register_error_handler(HTTPStatus.BAD_REQUEST, err.bad_request)
        self._app.register_error_handler(HTTPStatus.NOT_FOUND, err.page_not_found)
        self._app.register_error_handler(HTTPStatus.METHOD_NOT_ALLOWED, err.method_not_allowed)
        self._app.register_error_handler(HTTPStatus.CONFLICT, err.conflict)
        self._app.register_error_handler(HTTPStatus.UNPROCESSABLE_ENTITY, err.unprocessed_entity)
        self._app.register_error_handler(HTTPStatus.INTERNAL_SERVER_ERROR, err.internal_server_error)

    def _init_db(self) -> None:
        db.init_app(self._app)
        db.create_all(app=self._app)

    def _init_marshmallow(self) -> None:
        ma.init_app(self._app)
