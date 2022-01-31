import logging
from typing import Tuple

from flask import jsonify, Response
from flask import request as request_obj

from .basic_view import BasicView
from src.api.v1.services.currency_service import CurrencyService

logger = logging.getLogger(__name__)


class BasicCurrencyView(BasicView):

    def __init__(self):
        super().__init__()
        # todo: cache problem
        self._currency_service: CurrencyService = CurrencyService()


class CurrencyView(BasicCurrencyView):

    def get(self, record_id: int) -> Tuple[Response, int]:
        context, status = self._currency_service.get_currency_by_id(record_id)
        return jsonify(context), status

    def patch(self, record_id: int) -> Tuple[Response, int]:
        self.validate_request(request_obj)
        context, status = self._currency_service.update_currency(record_id, request_obj.json)
        return jsonify(context), status

    def delete(self, record_id: int) -> Tuple[Response, int]:
        context, status = self._currency_service.delete_currency(record_id)
        return jsonify(context), status


class CurrenciesView(BasicCurrencyView):

    def get(self) -> Tuple[Response, int]:
        context, status = self._currency_service.get_currencies(request_obj.args)
        return jsonify(context), status

    def post(self) -> Tuple[Response, int]:
        self.validate_request(request_obj)
        context, status = self._currency_service.create_currency(request_obj.json)
        return jsonify(context), status
