from typing import Type

from tdm import TalismanDocument, TalismanDocumentModel
from typing_extensions import Self

from tp_interfaces.helpers.serialize import AbstractDataModel


class TalismanDocumentDataModel(AbstractDataModel[TalismanDocument], TalismanDocumentModel):

    @classmethod
    def serialize(cls, data: TalismanDocument) -> Self:
        return TalismanDocumentModel.serialize(data)

    def deserialize(self) -> TalismanDocument:
        return TalismanDocumentModel.deserialize(self)

    @classmethod
    def data_type(cls) -> Type[TalismanDocument]:
        return TalismanDocument
