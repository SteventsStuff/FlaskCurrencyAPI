from enum import Enum, unique


@unique
class RateExternalReprFieldFieldNames(Enum):
    id = 'id'
    operation_type = 'operationType'
    rate = 'rate'
    is_cash = 'isCash'
    base_currency = 'baseCurrency'
    currency = 'currency'
    created = 'created'
    updated = 'updated'
    links = 'metadata'
    links_self = 'self'
    links_collection = 'collection'


@unique
class RateInternalReprFieldFieldNames(Enum):
    id = 'id'
    operation_type = 'operation_type'
    rate = 'rate'
    is_cash = 'is_cash'
    base_id = 'base_id'
    currency_id = 'currency_id'
    currency = 'currency'
    base_currency = 'base_currency'
    created = 'created'
    updated = 'updated'
    links = '_links'


@unique
class RateOperationTypes(Enum):
    buy = 'buy'.upper()
    sell = 'sell'.upper()
