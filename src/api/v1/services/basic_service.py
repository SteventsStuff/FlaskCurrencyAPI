import logging
from typing import Tuple

from werkzeug.datastructures import MultiDict

logger = logging.getLogger(__name__)


class BaseService:

    @staticmethod
    def _validate_args(reqeust_args: MultiDict, allowed_param_names: Tuple[str, ...]) -> MultiDict:
        return MultiDict({k: v for k, v in reqeust_args.items() if k in allowed_param_names})
