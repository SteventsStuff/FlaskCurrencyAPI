import copy
import logging
from http import HTTPStatus
from typing import Dict, Any, Tuple, List, Optional

from flask import abort
from marshmallow import ValidationError
from sqlalchemy.engine.row import Row

from .basic_service import BaseService
from src.models import db, Rate, Currency
from src.enums import RateExternalReprFieldFieldNames as RateExternalRepr
from src.enums import RateInternalReprFieldFieldNames as RateInternalRepr
from src.enums import ResponseStatuses, ResponseFields, CurrencyStatuesInternal
from src.exceptions import UpdateError, DeleteError, CreateError
from werkzeug.datastructures import MultiDict
from src.schemas.rate_schema import (
    RateSchema, RateDetailsExternalSchema, CreateRateExternalSchema, CreateRateInternalSchema,
    UpdateRateExternalSchema
)

logger = logging.getLogger(__name__)


class RateService(BaseService):
    _RATE_NOT_FOUND_MSG: str = 'Rate with id: {} not found'
    _CURRENCY_NOT_FOUND_MSG: str = 'Currency with id: {} not found'
    _ALLOWED_GET_PARAMS: Tuple[str, ...] = (
        RateExternalRepr.currency.value,
        RateExternalRepr.base_currency.value,
        RateExternalRepr.rate.value,
        RateExternalRepr.is_cash.value,
        RateExternalRepr.operation_type.value,
    )

    def __init__(self):
        self._rate_schema: RateSchema = RateSchema()
        self._rates_schema: RateSchema = RateSchema(many=True)
        self._rate_detailed_external_schema: RateDetailsExternalSchema = RateDetailsExternalSchema()
        self._create_rate_external_schema: CreateRateExternalSchema = CreateRateExternalSchema()
        self._create_rate_internal_schema: CreateRateInternalSchema = CreateRateInternalSchema()
        self._update_rate_external_schema: UpdateRateExternalSchema = UpdateRateExternalSchema()

    def get_rates(self, request_args: MultiDict) -> Tuple[Dict[str, Any], int]:
        logger.info('Getting rates...')
        rates = self._get_rates_by_args(request_args) if len(request_args) else self._get_all_rates()

        response = {
            ResponseFields.next_page_link.value: None,
            **rates
        }
        return response, HTTPStatus.OK

    def get_rate_by_id(self, record_id: int) -> Tuple[Dict[str, Any], int]:
        logger.info(f'Getting rate information by id: {record_id}...')

        record_info = self._get_joined_rate_and_currencies_by_rate_id(record_id)
        if not record_info:
            abort(HTTPStatus.NOT_FOUND, self._RATE_NOT_FOUND_MSG.format(record_id))

        rate, currency_code, base_currency_code = record_info
        # NOTE: "updated" not used
        rate_data = {
            RateInternalRepr.currency.value: currency_code,
            RateInternalRepr.base_currency.value: base_currency_code,
            RateInternalRepr.id.value: rate.id,
            RateInternalRepr.rate.value: rate.rate,
            RateInternalRepr.operation_type.value: rate.operation_type,
            RateInternalRepr.is_cash.value: rate.is_cash,
            RateInternalRepr.created.value: rate.created,
        }
        response = self._rate_detailed_external_schema.dump(rate_data)

        return response, HTTPStatus.OK

    def create_rate(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        logger.info('Creating a new rate...')
        try:
            self._create_rate_external_schema.load(data)
        except ValidationError as e:
            logger.error(f'Invalid request body was provided! Error: {e}')
            abort(HTTPStatus.BAD_REQUEST, e.messages)
        data_copy = copy.deepcopy(data)
        base_currency_id, currency_id = self._get_rate_currency_info(data)
        if not base_currency_id:
            abort(HTTPStatus.BAD_REQUEST,
                  self._CURRENCY_NOT_FOUND_MSG.format(data[RateExternalRepr.base_currency.value]))
        if not currency_id:
            abort(HTTPStatus.BAD_REQUEST,
                  self._CURRENCY_NOT_FOUND_MSG.format(data[RateExternalRepr.currency.value]))

        data_copy.update({
            RateInternalRepr.base_id.value: base_currency_id,
            RateInternalRepr.currency_id.value: currency_id,
        })
        try:
            new_rate = Rate.create(**self._create_rate_internal_schema.load(data_copy))
        except CreateError as e:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, str(e))

        response = {
            ResponseFields.status.value: ResponseStatuses.created.value,
            ResponseFields.id.value: new_rate.id
        }
        return response, HTTPStatus.CREATED

    def update_rate(self, record_id: int, data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        # тут жидкий момент в том, что я не проверяю валюту рейта на то что у нее активный статус
        logger.info('Updating currency...')
        rate_to_update: Rate = Rate.get_by(id=record_id).first()
        if not rate_to_update:
            abort(HTTPStatus.NOT_FOUND, f'Rate with id: {record_id} does not exist.')

        if RateExternalRepr.id.value in data:
            abort(HTTPStatus.BAD_REQUEST, 'The \'id\' field is not allowed to be updated.')

        try:
            loaded_data = self._update_rate_external_schema.load(data)
        except ValidationError as e:
            logger.error(f'Invalid request body was provided! Error: {e}')
            abort(HTTPStatus.BAD_REQUEST, e.messages)

        try:
            rate_to_update.update(loaded_data)
        except UpdateError as e:
            abort(HTTPStatus.BAD_REQUEST, e.reason)

        context = {
            ResponseFields.status.value: ResponseStatuses.updated.value,
            ResponseFields.record.value: self._rate_schema.dump(rate_to_update),
        }
        return context, HTTPStatus.OK

    @staticmethod
    def delete_rate(record_id: int) -> Tuple[Dict[str, Any], int]:
        logger.info(f'Deleting rate with Id: {record_id}...')
        rate = Rate.get_by(id=record_id).first_or_404()
        try:
            rate.hard_delete()
        except DeleteError as e:
            abort(HTTPStatus.CONFLICT, e.reason)

        return {}, HTTPStatus.NO_CONTENT

    def _get_all_rates(self) -> List[Dict[str, Any]]:
        rates_info = self._get_joined_rate_and_currencies()
        if not rates_info:
            return []

        rates = []
        for rate_info in rates_info:
            rate, currency_code, base_currency_code = rate_info
            rate = {
                RateInternalRepr.id.value: rate.id,
                RateInternalRepr.currency.value: currency_code.code,
                RateInternalRepr.base_currency.value: base_currency_code.code,
                RateInternalRepr.rate.value: rate.rate,
                RateInternalRepr.is_cash.value: rate.is_cash,
                RateInternalRepr.operation_type.value: rate.operation_type,
            }
            rates.append(rate)

        return self._rates_schema.dump(rates)

    def _get_rates_by_args(self, request_args: MultiDict) -> List[Dict[str, Any]]:
        validated_args = self._validate_args(request_args, self._ALLOWED_GET_PARAMS)
        if not validated_args:
            return self._get_all_rates()

        parsed_args = self._parser_args(validated_args)

        rates_info = Rate.query.filter_by(**parsed_args).all()
        if not rates_info:
            return []

        rates = []
        for rate_info in rates_info:
            rate, currency_code, base_currency_code = rate_info
            rate = {
                RateInternalRepr.id.value: rate.id,
                RateInternalRepr.currency.value: currency_code.code,
                RateInternalRepr.base_currency.value: base_currency_code.code,
                RateInternalRepr.rate.value: rate.rate,
                RateInternalRepr.is_cash.value: rate.is_cash,
                RateInternalRepr.operation_type.value: rate.operation_type,
            }
            rates.append(rate)

        return self._rates_schema.dump(rates)

    def _parser_args(self, args: MultiDict) -> Dict[str, Any]:
        # todo: finish later
        parsed_args = dict(args)

        if RateExternalRepr.base_currency.value in args:
            currency = Currency.get_by(
                code=args[RateExternalRepr.base_currency.value],
                status=CurrencyStatuesInternal.active.value
            ).first()
            parsed_args[RateInternalRepr.base_currency.value] = currency.id
        if RateExternalRepr.currency.value in args:
            currency = Currency.get_by(
                code=args[RateExternalRepr.currency.value],
                status=CurrencyStatuesInternal.active.value
            ).first()
            parsed_args[RateInternalRepr.currency.value] = currency.id
        if RateExternalRepr.operation_type.value in args:
            parsed_args[RateInternalRepr.operation_type] = args[RateExternalRepr.operation_type.value]

        return self._rate_schema.dump(parsed_args)

    @staticmethod
    def _get_rate_currency_info(data: Dict[str, Any]) -> Tuple[Optional[int], Optional[int]]:
        base_curr_code = data[RateExternalRepr.base_currency.value]
        curr_code = data[RateExternalRepr.currency.value]
        query_filter = db.and_(Currency.status == CurrencyStatuesInternal.active.value,
                               Currency.code.in_([base_curr_code, curr_code]))
        currencies_info = db.session.query(Currency.id, Currency.code) \
            .filter(query_filter) \
            .all()

        base_curr_id, curr_id = None, None
        for currency_id, currency_code in currencies_info:
            if currency_code == base_curr_code:
                base_curr_id = currency_id
            else:
                curr_id = currency_id

        return base_curr_id, curr_id

    @staticmethod
    def _get_joined_rate_and_currencies_by_rate_id(rate_id: int) -> Optional[Row]:
        base_currency = db.aliased(Currency, name='base_currency')
        query_filter = db.and_(
            Rate.id == rate_id,
            db.and_(
                Currency.status == CurrencyStatuesInternal.active.value,
                base_currency.status == CurrencyStatuesInternal.active.value
            )
        )

        query_result = db.session.query(Rate, Currency, base_currency) \
            .join(Currency, Rate.currency_id == Currency.id) \
            .join(base_currency, Rate.base_id == base_currency.id) \
            .filter(query_filter) \
            .first()
        return query_result

    @staticmethod
    def _get_joined_rate_and_currencies() -> Optional[List[Row]]:
        base_currency = db.aliased(Currency, name='base_currency')
        query_filter = db.and_(
            Currency.status == CurrencyStatuesInternal.active.value,
            base_currency.status == CurrencyStatuesInternal.active.value
        )

        query_result = db.session.query(Rate, Currency, base_currency) \
            .join(Currency, Rate.currency_id == Currency.id) \
            .join(base_currency, Rate.base_id == base_currency.id) \
            .filter(query_filter) \
            .all()
        return query_result
