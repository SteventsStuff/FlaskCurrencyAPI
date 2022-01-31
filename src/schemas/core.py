from typing import Any, Optional

from flask_marshmallow import Marshmallow
from marshmallow import pre_load, post_dump

ma = Marshmallow()


class BaseSchema(ma.Schema):
    # Custom options
    __envelope__ = {'many': None}

    # todo: код выглядит жидко
    def get_envelope_key(self, many: bool) -> Optional[str]:
        """Helper to get the envelope key."""
        if many:
            key = self.__envelope__.get('many')
            assert key is not None, 'Envelope key undefined'
            return key

    # todo: mb refact later
    @pre_load(pass_many=True)
    def unwrap_envelope(self, data: Any, many: bool, **kwargs) -> Any:
        return data[self.get_envelope_key(many)] if many else data

    @post_dump(pass_many=True)
    def wrap_with_envelope(self, data: Any, many: bool, **kwargs) -> Any:
        return {self.__envelope__['many']: data} if many else data

