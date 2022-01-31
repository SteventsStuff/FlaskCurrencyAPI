import logging
from http import HTTPStatus
from typing import Dict, Any, Tuple

from flask import abort
from marshmallow import ValidationError

from .basic_service import BaseService
from src.models import Currency
from src.enums import CurrencyExternalReprFieldNames as CurrExternalRepr
from src.enums import CurrencyInternalReprFieldNames as CurrInternalRepr
from src.enums import ResponseStatuses, CurrencyStatuesInternal, ResponseFields
from src.schemas.currency_schema import CurrencySchema, CurrencyDetailedSchema
from src.exceptions import UpdateError, DeleteError, CreateError
from werkzeug.datastructures import MultiDict

logger = logging.getLogger(__name__)


class CurrencyService(BaseService):
    _ALLOWED_GET_PARAMS: Tuple[str, ...] = (
        CurrExternalRepr.code.value,
        CurrExternalRepr.name_.value,
    )

    def __init__(self):
        self._currency_schema: CurrencySchema = CurrencySchema()
        self._currencies_schema: CurrencySchema = CurrencySchema(many=True)
        self._currency_details_schema: CurrencyDetailedSchema = CurrencyDetailedSchema()

    def get_currencies(self, request_args: MultiDict) -> Tuple[Dict[str, Any], int]:
        logger.info('Getting all currencies...')
        if len(request_args):
            currencies = self._get_currencies_by_args(request_args)
        else:
            currencies = Currency.get_by(status=CurrencyStatuesInternal.active.value)
        result = self._currencies_schema.dump(currencies) if currencies else []

        response = {
            ResponseFields.next_page_link.value: None,
            **result,
        }
        return response, HTTPStatus.OK

    def get_currency_by_id(self, record_id: int) -> Tuple[Dict[str, Any], int]:
        logger.info(f'Getting currency information by id: {record_id}...')
        currency = Currency.get_by_first_or_404(id=record_id,
                                                status=CurrencyStatuesInternal.active.value)
        response = self._currency_details_schema.dump(currency)
        return response, HTTPStatus.OK

    def create_currency(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        logger.info('Creating a new currency...')
        try:
            dict_currency_repr = self._currency_schema.load(data)
        except ValidationError as e:
            logger.error(f'Invalid request body was provided! Error: {e}')
            abort(HTTPStatus.BAD_REQUEST, e.messages)

        filtering_rules = {
            CurrInternalRepr.code.value: dict_currency_repr[CurrExternalRepr.code.value],
            CurrInternalRepr.status.value: CurrencyStatuesInternal.active.value,
        }
        duplicate = Currency.get_by(**filtering_rules).first()
        if duplicate:
            msg = f'Currency with the same code already exists. Duplicated ID: {duplicate.id}'
            abort(HTTPStatus.CONFLICT, msg)

        try:
            new_currency = Currency.create(**dict_currency_repr)
        except CreateError as e:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, str(e))

        response = {
            ResponseFields.status.value: ResponseStatuses.created.value,
            CurrExternalRepr.id.value: new_currency.id
        }
        return response, HTTPStatus.CREATED

    def update_currency(self, record_id: int, data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        logger.info(f'Updating currency with id: {record_id}...')
        currency_to_update: Currency = Currency.get_by(
            id=record_id,
            status=CurrencyStatuesInternal.active.value
        ).first()
        if not currency_to_update:
            abort(HTTPStatus.NOT_FOUND, f'Currency with id: {record_id} does not exist.')

        duplicate = Currency.get_by(code=data.get(CurrExternalRepr.code.value)).first()
        if duplicate and duplicate.id != record_id:
            msg = f'Currency with the same code already exists. Duplicated ID: {duplicate.id}'
            abort(HTTPStatus.CONFLICT, msg)

        if CurrExternalRepr.id.value in data:
            abort(HTTPStatus.BAD_REQUEST, 'The \'id\' field is not allowed to be updated.')

        try:
            dumped_currency_data = self._currency_schema.load(data)
        except ValidationError as e:
            logger.error(f'Invalid request body was provided! Error: {e}')
            abort(HTTPStatus.BAD_REQUEST, e.messages)

        try:
            currency_to_update.update(dumped_currency_data)
        except UpdateError as e:
            abort(HTTPStatus.BAD_REQUEST, e.reason)

        context = {
            ResponseFields.status.value: ResponseStatuses.updated.value,
            **self._currency_schema.dump(currency_to_update),
        }
        return context, HTTPStatus.OK

    @staticmethod
    def delete_currency(record_id: int) -> Tuple[Dict[str, Any], int]:
        # todo: delete all relevant rates
        logger.info(f'Deleting currency with id: {record_id}...')
        currency = Currency.get_by(id=record_id,
                                   status=CurrencyStatuesInternal.active.value).first_or_404()
        try:
            currency.soft_delete()
        except DeleteError as e:
            abort(HTTPStatus.CONFLICT, e.reason)

        return {}, HTTPStatus.NO_CONTENT

    def _get_currencies_by_args(self, request_args: MultiDict) -> Currency:
        validated_args = self._validate_args(request_args, self._ALLOWED_GET_PARAMS)

        try:
            params = self._currency_schema.dump(validated_args)
        except ValidationError as e:
            logger.error(e)
            abort(HTTPStatus.BAD_REQUEST, f'Invalid request args: {request_args}. Error: {e}')

        params.update({
            CurrExternalRepr.status.value: CurrencyStatuesInternal.active.value
        })
        return Currency.get_by(**params)
