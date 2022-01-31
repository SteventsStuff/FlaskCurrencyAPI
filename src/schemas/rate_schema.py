from typing import Tuple

from marshmallow import fields, EXCLUDE
from flask_marshmallow import fields as fma_basic

from .core import BaseSchema
from .fields import OperationType, CurrencyRate, CurrencyField
from .currency_schema import CurrencyMinimalSchema
from src.models import Rate
from src.enums import RateOperationTypes
from src.enums import RateExternalReprFieldFieldNames as ExternalRepr
from src.enums import RateInternalReprFieldFieldNames as InternalRepr
from src.constans import DATETIME_FORMAT


class RateSchema(BaseSchema):
    __envelope__ = {'many': 'rates'}
    __model__ = Rate

    _ALLOWED_OPERATION_TYPES: Tuple[str, ...] = (
        RateOperationTypes.buy.value,
        RateOperationTypes.sell.value,
    )

    class Meta:
        unknown = EXCLUDE
        ordered = True
        fields = (
            InternalRepr.id.value,
            InternalRepr.currency.value,
            InternalRepr.base_currency.value,
            InternalRepr.rate.value,
            InternalRepr.operation_type.value,
            InternalRepr.is_cash.value,
        )

    id = fields.Integer()
    currency = CurrencyField(data_key=ExternalRepr.currency.value, required=True)
    base_currency = CurrencyField(data_key=ExternalRepr.base_currency.value, required=True)
    operation_type = OperationType(data_key=ExternalRepr.operation_type.value, required=True,
                                   allow_nan=False)
    rate = CurrencyRate(data_key=ExternalRepr.rate.value, required=True, places=5)
    is_cash = fields.Boolean(data_key=ExternalRepr.is_cash.value, required=True)


class RateDetailsExternalSchema(RateSchema):
    _CURRENCY_CODE_MAX_LENGTH: int = 3

    class Meta:
        unknown = EXCLUDE
        ordered = True
        fields = (
            InternalRepr.id.value,
            InternalRepr.currency.value,
            InternalRepr.base_currency.value,
            InternalRepr.rate.value,
            InternalRepr.operation_type.value,
            InternalRepr.is_cash.value,
            InternalRepr.created.value,
            InternalRepr.updated.value,
            InternalRepr.links.value,
        )

    currency = fields.Nested(CurrencyMinimalSchema(), data_key=ExternalRepr.currency.value)
    base_currency = fields.Nested(CurrencyMinimalSchema(), data_key=ExternalRepr.base_currency.value)
    created = fields.DateTime(data_key=ExternalRepr.created.value, format=DATETIME_FORMAT)
    updated = fields.DateTime(data_key=ExternalRepr.updated.value, format=DATETIME_FORMAT)
    _links = fma_basic.Hyperlinks({
        ExternalRepr.links_self.value: fma_basic.URLFor('rate_api.rate_view',
                                                        values={'record_id': '<id>'}),
        ExternalRepr.links_collection.value: fma_basic.URLFor('rate_api.rates_view'),
    }, data_key=ExternalRepr.links.value)


class CreateRateExternalSchema(RateSchema):
    class Meta:
        unknown = EXCLUDE
        ordered = True
        fields = (
            InternalRepr.operation_type.value,
            InternalRepr.rate.value,
            InternalRepr.is_cash.value,
            InternalRepr.base_currency.value,
            InternalRepr.currency.value,
        )


class CreateRateInternalSchema(RateSchema):
    class Meta:
        unknown = EXCLUDE
        ordered = True
        fields = (
            InternalRepr.operation_type.value,
            InternalRepr.rate.value,
            InternalRepr.is_cash.value,
            InternalRepr.base_id.value,
            InternalRepr.currency_id.value,
        )

    base_id = fields.Integer(required=True)
    currency_id = fields.Integer(required=True)


class UpdateRateExternalSchema(RateSchema):
    class Meta:
        unknown = EXCLUDE
        ordered = True
        fields = (
            InternalRepr.operation_type.value,
            InternalRepr.rate.value,
            InternalRepr.is_cash.value,
        )
