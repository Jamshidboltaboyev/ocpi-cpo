from datetime import timezone, datetime
from typing import Union

from pydantic import BaseModel
from py_ocpi.core.data_types import DateTime


class DisplayText(dict):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            examples=[
                {
                    "language": "en",
                    "text": "Standard Tariff"
                }
            ],
        )

    @classmethod
    def validate(cls, v):
        if not isinstance(v, dict):
            raise TypeError(f'excpected dict but received {type(v)}')
        if 'language' not in v:
            raise TypeError('property "language" required')
        if 'text' not in v:
            raise TypeError('property "text" required')
        if len(v['text']) > 512:
            raise TypeError('text too long')
        return cls(v)

    def __repr__(self):
        return f'DateTime({super().__repr__()})'


class OCPIResponse(BaseModel):
    data: Union[list, dict]
    status_code: int
    status_message: str
    timestamp: DateTime = str(datetime.now(timezone.utc))


OCPI_1000_GENERIC_SUCESS_CODE = {
    'status_code': 1000,
    'status_message': 'Generic success code'
}
