from marshmallow import ValidationError
from marshmallow import fields, validates, EXCLUDE
from flask_marshmallow import fields as fma_fields

from .core import BaseSchema
from .fields import Status
from src.enums import CurrencyExternalReprFieldNames as ExternalRepr
from src.enums import CurrencyInternalReprFieldNames as InternalRepr
from src.models import Currency
from src.constans import DATETIME_FORMAT


class CurrencyDetailedSchema(BaseSchema):
    __envelope__ = {'many': 'currencies'}
    __model__ = Currency

    _MAX_CURRENCY_NAME_LENGTH: int = 20
    _MIN_CURRENCY_NAME_LENGTH: int = 1
    _CURRENCY_CODE_LENGTH: int = 3

    class Meta:
        model = Currency
        unknown = EXCLUDE
        ordered = True
        fields = (
            InternalRepr.id.value,
            InternalRepr.status.value,
            InternalRepr.name_.value,
            InternalRepr.code.value,
            InternalRepr.created.value,
            InternalRepr.updated.value,
            InternalRepr.links.value,
        )

    id = fields.Integer()
    status = Status(data_key=ExternalRepr.status.value)
    name = fields.Str(data_key=ExternalRepr.name_.value, required=True)
    code = fields.Str(data_key=ExternalRepr.code.value, required=True, allow_none=False)
    created = fields.DateTime(data_key=ExternalRepr.created.value, format=DATETIME_FORMAT)
    updated = fields.DateTime(data_key=ExternalRepr.updated.value, format=DATETIME_FORMAT)
    _links = fma_fields.Hyperlinks({
        ExternalRepr.links_self.value: fma_fields.URLFor('currency_api.currency_view',
                                                         values={'record_id': '<id>'}),
        ExternalRepr.links_collection.value: fma_fields.URLFor('currency_api.currencies_view')
    }, data_key=ExternalRepr.links.value)

    @validates(InternalRepr.name_.value)
    def _validate_currency_name(self, value: str) -> None:
        if len(value) > self._MAX_CURRENCY_NAME_LENGTH:
            raise ValidationError('Currency name length must be up to 20 characters.')
        if len(value) == self._MIN_CURRENCY_NAME_LENGTH:
            raise ValidationError('Currency name length must be at least 1 character.')

    @validates(InternalRepr.code.value)
    def _validate_code(self, value: str) -> None:
        if not value.isupper():
            raise ValidationError('Currency code must be in UPPER case!')

        if len(value) != self._CURRENCY_CODE_LENGTH:
            raise ValidationError('Currency code length must be 3 characters long!')


class CurrencySchema(CurrencyDetailedSchema):
    class Meta:
        fields = (
            InternalRepr.id.value,
            InternalRepr.status.value,
            InternalRepr.code.value,
            InternalRepr.name_.value,
        )


class CurrencyMinimalSchema(CurrencyDetailedSchema):
    class Meta:
        fields = (
            InternalRepr.id.value,
            InternalRepr.code.value,
        )
