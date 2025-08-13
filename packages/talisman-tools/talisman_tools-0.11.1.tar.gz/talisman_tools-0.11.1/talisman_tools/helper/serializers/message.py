import dataclasses
from typing import Type

from pydantic import ConfigDict, Field
from typing_extensions import Self

from tp_interfaces.abstract import ImmutableBaseModel, Message
from tp_interfaces.abstract.processor.message import File
from tp_interfaces.helpers.serialize import AbstractDataModel


class FileModel(ImmutableBaseModel):
    path: str
    filename: str
    checksum: str
    model_config = ConfigDict(extra='allow')


class MessageModel(AbstractDataModel[Message], ImmutableBaseModel):
    id: str = Field(alias="_uuid")
    file: FileModel | None = Field(alias="_file", default=None)
    parent_uuid: str | None = Field(alias="_parent_uuid", default=None)
    timestamp: int | None = Field(alias="_timestamp", default=None)
    model_config = ConfigDict(extra='allow')

    @classmethod
    def serialize(cls, data: Message) -> Self:
        file = FileModel(**data.file.__dict__) if data.file else None
        defined_field_names = {f.name for f in dataclasses.fields(data)}
        extra_fields = {key: value for key, value in data.__dict__.items() if key not in defined_field_names}
        message = cls(_uuid=data.id, _file=file, _parent_uuid=data.parent_uuid, _timestamp=data.timestamp, **extra_fields)
        return message

    def deserialize(self) -> Message:
        file = File(**self.file.model_dump()) if self.file else None
        message = Message(id_=self.id, file=file, parent_uuid=self.parent_uuid, timestamp=self.timestamp, **self.__pydantic_extra__)
        return message

    @classmethod
    def data_type(cls) -> Type[Message]:
        return Message
