from typing import BinaryIO

import numpy as np

from .typings import PCDParseError, PCDUnsupportedFormatError
from .utils import (
    get_expected_buffer,
    parse_ascii_data,
    parse_binary_compressed_data,
    parse_pcd_header,
)


class PCDLoader:
    def __init__(self, file: BinaryIO):
        self.file = file
        self.metadata, self.pcd_format, self.data_offset = parse_pcd_header(file)

    def load(self, replace_nan_with_zero: bool) -> np.ndarray:
        self.file.seek(self.data_offset)

        if self.pcd_format == "ascii":
            data = parse_ascii_data(self.file, self.metadata)

        elif self.pcd_format == "binary":
            dtype, expected_bytes = get_expected_buffer(self.metadata)
            buffer = self.file.read(expected_bytes)
            if len(buffer) != expected_bytes:
                raise PCDParseError("Binary data is incomplete.")
            data = np.frombuffer(buffer, dtype=dtype).copy()

        elif self.pcd_format == "binary_compressed":
            data = parse_binary_compressed_data(self.file, self.metadata).copy()

        else:
            raise PCDUnsupportedFormatError(
                f"Unsupported DATA format: {self.pcd_format}"
            )

        if replace_nan_with_zero:
            for name in self.metadata.to_dtype().names:
                if np.issubdtype(data[name].dtype, np.floating):
                    np.nan_to_num(data[name], copy=False, nan=0.0)

        return data
