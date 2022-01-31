from enum import Enum, unique


@unique
class ResponseStatuses(Enum):
    failed = 'failed'.upper()
    updated = 'updated'.upper()
    created = 'created'.upper()
    # todo: review later
    # deleted = 'deleted'.upper()


@unique
class ResponseFields(Enum):
    status = 'status'
    id = 'id'
    result_collection = 'records'
    next_page_link = 'next'
    record = 'record'
