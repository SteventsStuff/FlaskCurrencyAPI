import logging
from typing import Tuple

from flask import jsonify, Response
from flask import request as request_obj

from .basic_view import BasicView
from src.api.v1.services.rate_service import RateService

logger = logging.getLogger(__name__)


class BasicRateView(BasicView):

    def __init__(self):
        super().__init__()
        self._rate_service: RateService = RateService()


class RateView(BasicRateView):

    def get(self, record_id: int) -> Tuple[Response, int]:
        context, status = self._rate_service.get_rate_by_id(record_id)
        return jsonify(context), status

    def patch(self, record_id: int) -> Tuple[Response, int]:
        self.validate_request(request_obj)
        context, status = self._rate_service.update_rate(record_id, request_obj.json)
        return jsonify(context), status

    def delete(self, record_id: int) -> Tuple[Response, int]:
        context, status = self._rate_service.delete_rate(record_id)
        return jsonify(context), status


class RatesView(BasicRateView):

    def get(self) -> Tuple[Response, int]:
        context, status = self._rate_service.get_rates(request_obj.args)
        return jsonify(context), status

    def post(self) -> Tuple[Response, int]:
        self.validate_request(request_obj)
        context, status = self._rate_service.create_rate(request_obj.json)
        return jsonify(context), status
