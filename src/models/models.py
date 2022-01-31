import logging

from .database import db
from src.mixins import CRUDMixin, TimestampMixin
from src.enums import CurrencyStatuesInternal
from src.enums import CurrencyExternalReprFieldNames as CurrExternalRepr

logger = logging.getLogger(__name__)


class Rate(CRUDMixin, TimestampMixin, db.Model):
    __tablename__ = 'Rate'

    id = db.Column(db.Integer, primary_key=True)
    operation_type = db.Column('OperationType', db.CHAR, nullable=False)
    rate = db.Column('Rate', db.DECIMAL(12, 5), nullable=False)
    is_cash = db.Column('IsCash', db.Boolean, nullable=False)

    # Foreign keys
    currency_id = db.Column(
        'CurrencyId', db.Integer, db.ForeignKey('Currency.id', name='CurrencyId'),
        nullable=False
    )
    base_id = db.Column(
        'BaseCurrencyId', db.Integer, db.ForeignKey('Currency.id', name='BaseCurrencyId'),
        nullable=False
    )

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'{self.base_id}, '
            f'{self.currency_id}, '
            f'{self.operation_type}, '
            f'{self.rate}, '
            f'{self.is_cash}'
            f')'
        )


class Currency(CRUDMixin, TimestampMixin, db.Model):
    __tablename__ = 'Currency'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column('Status', db.SMALLINT, nullable=False)
    name = db.Column('Name', db.String(20))
    code = db.Column('Code', db.String(3), nullable=False)

    @classmethod
    def create(cls, **kwargs) -> db.Model:
        kwargs.update({CurrExternalRepr.status.value: CurrencyStatuesInternal.active.value})
        return super().create(**kwargs)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name}, {self.status}, {self.code})'
