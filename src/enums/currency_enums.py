from enum import Enum, unique


@unique
class CurrencyExternalReprFieldNames(Enum):
    id = 'id'
    status = 'status'
    name_ = 'name'
    code = 'code'
    created = 'created'
    updated = 'updated'
    links = 'metadata'
    links_self = 'self'
    links_collection = 'collection'


@unique
class CurrencyInternalReprFieldNames(Enum):
    id = 'id'
    status = 'status'
    name_ = 'name'
    code = 'code'
    created = 'created'
    updated = 'updated'
    links = '_links'


@unique
class CurrencyStatuesExternal(Enum):
    active = 'act'.upper()
    deleted = 'del'.upper()


@unique
class CurrencyStatuesInternal(Enum):
    active = 1
    deleted = 0
