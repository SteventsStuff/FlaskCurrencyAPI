from http import HTTPStatus

from flask import request as request_obj
from flask.views import MethodView
from flask import abort

from src.api.v1.validators import RequestValidator, ValidatorError


class BasicView(MethodView):
    def __init__(self):
        self._request_validator: RequestValidator = RequestValidator()

    def validate_request(self, request: request_obj) -> None:
        try:
            self._request_validator.validate(request)
        except ValidatorError as e:
            error_message = e.args[0]
            abort(HTTPStatus.BAD_REQUEST, error_message)
