import logging
import datetime
from http import HTTPStatus
from typing import Any, Dict, Optional

from flask import abort
from sqlalchemy.exc import InvalidRequestError, SQLAlchemyError, IntegrityError

from .models.database import db
from src.exceptions import CreateError, UpdateError, DeleteError

logger = logging.getLogger(__name__)


# todo: mb this whole DB session handling done incorrectly here... it suppose to be in
# todo: consider SQLAlchemy .one() method here. it raises an NoResultFound / MultipleResultsFound.
#  that might be used instead if "if"

class CRUDMixin:
    @classmethod
    def get(cls, record_id: int) -> Optional[db.Model]:
        return cls.query.get(record_id)

    @classmethod
    def get_or_404(cls, record_id: int) -> db.Model:
        obj = cls.get(record_id)
        if not obj:
            abort(HTTPStatus.NOT_FOUND, f'Can not {cls.__name__.lower()} record with ID: {record_id}')
        return obj

    @classmethod
    def get_by(cls, **kwargs) -> Optional[db.Model]:
        return cls.query.filter_by(**kwargs)

    @classmethod
    def get_by_first_or_404(cls, **kwargs) -> db.Model:
        return cls.query.filter_by(**kwargs).first_or_404()

    @classmethod
    def create(cls, **kwargs) -> db.Model:
        try:
            obj = cls(**kwargs)
            db.session.add(obj)
            db.session.commit()
        except IntegrityError as e:
            logger.error(e)
            db.session.rollback()
            raise CreateError("Integrity error", cls.__name__.lower()) from e
        return obj

    def update(self, data: Dict[str, Any]) -> None:
        # todo: тут так-то стейт меняется и новый объект не возвращается... Жидковато выходит
        for attr, value in data.items():
            setattr(self, attr, value)
        try:
            db.session.commit()
        except InvalidRequestError as e:
            logger.error(e)
            db.session.rollback()
            raise UpdateError(str(e), self.__class__.__name__.lower()) from e

    def hard_delete(self) -> None:
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            raise DeleteError(str(e), self.__class__.__name__.lower()) from e

    def soft_delete(self) -> None:
        try:
            self.update({'status': 0})
        except UpdateError as e:
            logger.error(e)
            raise DeleteError(str(e), self.__class__.__name__.lower()) from e


class TimestampMixin:
    created = db.Column('Created', db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated = db.Column('Updated', db.DateTime, onupdate=datetime.datetime.utcnow)
