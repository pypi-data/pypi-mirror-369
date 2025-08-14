import os
from typing import Union

PathLike = Union[str, os.PathLike]


class PCDBaseError(Exception): ...


class PCDParseError(PCDBaseError): ...


class PCDHeaderFormatError(PCDParseError): ...


class PCDUnsupportedFormatError(PCDParseError): ...


class PCDDataMismatchError(PCDParseError): ...


class PCDEncodingError(PCDParseError): ...
