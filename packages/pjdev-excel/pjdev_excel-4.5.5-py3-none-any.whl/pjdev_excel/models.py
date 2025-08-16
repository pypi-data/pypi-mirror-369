from typing import Any, Callable, Generic, TypeVar

from pydantic import BaseModel

DataType = TypeVar("DataType", bound=BaseModel)


class RowDefinition(BaseModel, Generic[DataType]):
    column_name: str
    value_getter: Callable[[DataType], Any]
