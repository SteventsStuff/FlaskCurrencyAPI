from decimal import Decimal, InvalidOperation
from typing import Dict, Any

from marshmallow import fields
from marshmallow import ValidationError

from src.enums import CurrencyStatuesExternal, RateOperationTypes
from src.models import Currency, Rate


class Status(fields.Field):
    _serialize_map: Dict[int, str] = {
        0: CurrencyStatuesExternal.deleted.value,
        1: CurrencyStatuesExternal.active.value,
    }
    _deserialize_map: Dict[str, int] = {
        CurrencyStatuesExternal.deleted.value: 0,
        CurrencyStatuesExternal.active.value: 1,
    }

    def _serialize(self, value: Any, attr: str, obj: Currency, **kwargs) -> str:
        try:
            return self._serialize_map[value]
        except KeyError as e:
            raise ValidationError(f'Invalid status value {e}. '
                                  f'Allowed values: {list(self._serialize_map)}') from e

    def _deserialize(self, value: Any, attr: str, data: Any, **kwargs) -> int:
        try:
            return self._deserialize_map[value]
        except KeyError as e:
            raise ValidationError(f'Invalid status value {e}. '
                                  f'Allowed values: {list(self._deserialize_map)}') from e


class OperationType(fields.Field):
    _serialize_map: Dict[int, str] = {
        'b': RateOperationTypes.buy.value,
        's': RateOperationTypes.sell.value,
    }
    _deserialize_map: Dict[str, int] = {
        RateOperationTypes.buy.value: 'b',
        RateOperationTypes.sell.value: 's',
    }

    def _serialize(self, value: Any, attr: str, obj: Rate, **kwargs) -> str:
        """ORM object -> JSON"""
        try:
            return self._serialize_map[value]
        except KeyError as e:
            raise ValidationError(f'Invalid operation type {e}. '
                                  f'Allowed operation types: {list(self._serialize_map)}') from e

    def _deserialize(self, value: Any, attr: str, data: Any, **kwargs) -> int:
        """JSON -> ORM object"""
        try:
            return self._deserialize_map[value]
        except KeyError as e:
            raise ValidationError(f'Invalid operation type {e}. '
                                  f'Allowed operation types: {list(self._deserialize_map)}') from e


class CurrencyRate(fields.Decimal):

    def _serialize(self, value: Any, attr: str, obj: Rate, **kwargs) -> float:
        """ORM object -> JSON"""
        try:
            return float(value)
        except Exception as e:
            raise ValidationError(f'Can not deserialize value: {value}. Error: {e}') from e

    def _deserialize(self, value: Any, attr: str, data: Any, **kwargs) -> Decimal:
        """JSON -> ORM object"""
        try:
            return Decimal(value).quantize(Decimal('1.00000'))
        except InvalidOperation as e:
            raise ValidationError(f'Invalid decimal value: {value}. Error: {e}') from e


class CurrencyField(fields.Field):
    _MAX_CURRENCY_CODE_LENGTH: int = 3

    def _validate_deserialization_data(self, value: Any) -> None:
        if not isinstance(value, str):
            raise ValidationError('Value must be a string.')
        if len(value) != self._MAX_CURRENCY_CODE_LENGTH:
            raise ValidationError(f'Value must be {self._MAX_CURRENCY_CODE_LENGTH} characters long.')
        if not value.isupper():
            raise ValidationError('Value must be in an upper case.')

    @staticmethod
    def _validate_serialization_data(value: Any) -> None:
        if not isinstance(value, str):
            raise ValidationError(f'Value "{value}" must be a String.')

    def _serialize(self, value: Any, attr: str, obj: Rate, **kwargs) -> int:
        """ORM object -> JSON"""
        self._validate_serialization_data(value)
        return value

    def _deserialize(self, value: Any, attr: str, data: Any, **kwargs) -> str:
        """JSON -> ORM object"""
        self._validate_deserialization_data(value)
        return value
