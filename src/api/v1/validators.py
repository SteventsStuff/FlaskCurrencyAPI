from typing import List
from abc import ABC, abstractmethod

from flask import request as request_obj
from werkzeug.exceptions import BadRequest


class ValidatorError(Exception):
    pass


class LowLevelValidator(ABC):

    @abstractmethod
    def validate(self, request: request_obj) -> None:
        # todo: "particular aspect" ???
        """Validates request object for particular aspect
        Args:
            request: flask request object
        Raises:
            ValidatorError:
        Returns:
            None
        """
        raise NotImplementedError


class HighLevelValidator(ABC):

    @abstractmethod
    def validate(self, request: request_obj) -> None:
        raise NotImplementedError


class RequestBodyValidator(LowLevelValidator):
    def validate(self, request: request_obj) -> None:
        self._check_is_json(request)

    @staticmethod
    def _check_is_json(request: request_obj) -> None:
        try:
            request.json
        except BadRequest as e:
            raise ValidatorError(e.description) from e


class RequestValidator(HighLevelValidator):

    def __init__(self, additional_validators: List[LowLevelValidator] = None):
        # todo: mb dict instead of list? it might resolve validators duplications issue
        self._validators: List[LowLevelValidator] = [
            RequestBodyValidator(),
        ]
        if isinstance(additional_validators, list):
            self._validators.extend(additional_validators)

    def validate(self, request: request_obj) -> None:
        for validator in self._validators:
            validator.validate(request)
