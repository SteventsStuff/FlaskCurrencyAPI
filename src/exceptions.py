class BaseCurrencyAPIException(Exception):
    pass


class CRUDError(BaseCurrencyAPIException):
    def __init__(self, reason: str, entry_type: str, *args):
        super().__init__(*args)
        self.reason: str = reason
        self.entry_type: str = entry_type

    def __str__(self):
        # NOTE: self.__str__ = self.__repr__ in __init__ won't work due to inheritance from Exception
        return self.__repr__()


class CreateError(CRUDError):
    def __init__(self, *args):
        super().__init__(*args)

        self.__dict__['__str__'] = self.__repr__

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}: Failed to create {self.entry_type} due to: {self.reason}'


class UpdateError(CRUDError):
    def __init__(self, *args):
        super().__init__(*args)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}: Failed to updated {self.entry_type} due to: {self.reason}'


class DeleteError(CRUDError):
    def __init__(self, *args):
        super().__init__(*args)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}: Failed to delete {self.entry_type} due to: {self.reason}'
