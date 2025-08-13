__all__ = [
    'TalismanDocumentDataModel',
    'MessageModel',
    'get_serializers'
]

from typing import Iterable, Type

from tp_interfaces.helpers.serialize import AbstractDataModel
from .document import TalismanDocumentDataModel
from .message import MessageModel


def get_serializers() -> Iterable[Type[AbstractDataModel]]:
    return [TalismanDocumentDataModel, MessageModel]
