from datetime import datetime
from typing import Annotated, Union

from pydantic import PlainSerializer, PlainValidator
from stollen import StollenObject
from typing_extensions import TypeAlias

from ...utils.base64 import validate_b64_image
from ...utils.date import to_cryptomus_fmt
from ..client import Cryptomus


class CryptomusObject(StollenObject[Cryptomus]):
    pass


class CryptomusUpdate(CryptomusObject):
    sign: str


Image: TypeAlias = Annotated[bytes, PlainValidator(validate_b64_image)]
DateTime: TypeAlias = Annotated[Union[datetime, str], PlainValidator(to_cryptomus_fmt)]
StrFloat: TypeAlias = Annotated[float, PlainSerializer(str)]
