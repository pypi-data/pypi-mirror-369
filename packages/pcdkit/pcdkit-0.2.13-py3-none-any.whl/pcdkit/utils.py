from typing import BinaryIO, List, Tuple, Union

import lzf
import numba
import numpy as np

from .pcd_metadata import PCDMetadata
from .typings import (
    PCDDataMismatchError,
    PCDEncodingError,
    PCDHeaderFormatError,
    PCDParseError,
    PCDUnsupportedFormatError,
)


def get_expected_buffer(metadata: PCDMetadata) -> Tuple[np.dtype, int]:
    dtype = metadata.to_dtype()
    expected_bytes = metadata.points * dtype.itemsize
    return dtype, expected_bytes


def parse_pcd_header(file: BinaryIO) -> Tuple[PCDMetadata, str, int]:
    lines = []
    offset = 0

    for raw_line in file:
        try:
            line = raw_line.decode("ascii").strip()
        except UnicodeDecodeError:
            raise PCDEncodingError("PCD header must be ASCII encoded.")

        lines.append(line)
        offset += len(raw_line)

        if line.lower().startswith("data"):
            break
    else:
        raise PCDHeaderFormatError("Header missing required DATA line.")
    pcd_metadata, pcd_format = parse_pcd_header_from_lines(lines)
    return pcd_metadata, pcd_format, offset


def parse_pcd_header_from_lines(lines: List[str]) -> Tuple[PCDMetadata, str]:
    metadata = {}
    pcd_format = ""

    def ints(values):
        return list(map(int, values))

    def floats(values):
        return tuple(map(float, values))

    for line in lines:
        if not line or line.startswith("#"):
            continue

        parts = line.split()
        key, values = parts[0].lower(), parts[1:]

        if key == "version":
            metadata["version"] = values[0]
        elif key == "fields":
            metadata["fields"] = values
        elif key == "size":
            metadata["size"] = ints(values)
        elif key == "type":
            metadata["type"] = values
        elif key == "count":
            metadata["count"] = ints(values)
        elif key == "width":
            metadata["width"] = int(values[0])
        elif key == "height":
            metadata["height"] = int(values[0])
        elif key == "viewpoint":
            if len(values) != 7:
                raise PCDHeaderFormatError("VIEWPOINT must have 7 values.")
            metadata["viewpoint"] = floats(values)
        elif key == "points":
            metadata["points"] = int(values[0])
        elif key == "data":
            pcd_format = values[0].lower()

    required = {
        "version",
        "fields",
        "size",
        "type",
        "count",
        "width",
        "height",
        "viewpoint",
        "points",
    }
    missing = required - metadata.keys()
    if missing:
        raise PCDHeaderFormatError(f"Missing fields: {missing}")

    if metadata["points"] != metadata["width"] * metadata["height"]:
        raise PCDDataMismatchError("POINTS must equal WIDTH × HEIGHT.")

    if pcd_format not in {"ascii", "binary", "binary_compressed"}:
        raise PCDUnsupportedFormatError(
            f"Unsupported DATA pcd_format: {metadata['data']}"
        )

    return PCDMetadata(**metadata), pcd_format


def parse_ascii_data(file: BinaryIO, metadata: PCDMetadata) -> np.ndarray:
    dtype = metadata.to_dtype()

    try:
        data = np.genfromtxt(file, dtype=dtype, delimiter=" ")
    except Exception as e:
        raise PCDParseError("Failed to parse ASCII point data.") from e

    if data.shape[0] != metadata.points:
        raise PCDParseError(f"Expected {metadata.points} points, got {data.shape[0]}.")

    return data


def parse_binary_compressed_data(file: BinaryIO, metadata: PCDMetadata) -> np.ndarray:
    dtype, expected_bytes = get_expected_buffer(metadata)

    header = file.read(8)
    if len(header) < 8:
        raise PCDParseError("Incomplete compressed header.")

    compressed_size, uncompressed_size = np.frombuffer(header, dtype=np.uint32)

    compressed_data = file.read(compressed_size)
    if len(compressed_data) != compressed_size:
        raise PCDParseError("Compressed data is incomplete.")

    try:
        decompressed = lzf.decompress(compressed_data, uncompressed_size)
    except Exception as e:
        raise PCDParseError("LZF decompression failed.") from e

    if len(decompressed) != expected_bytes:
        raise PCDParseError(
            f"Decompressed data length mismatch: expected {expected_bytes}, got {len(decompressed)}"
        )

    return reconstruct_structured_array_from_columnwise_bytes(decompressed, dtype)


def reconstruct_structured_array_from_columnwise_bytes(
    data: Union[bytes, memoryview],
    dtype: np.dtype,
) -> np.ndarray:
    """
    Reconstruct a structured NumPy array from column-wise byte data.

    Assumes the data contains all field values stored sequentially,
    field by field, for a structured dtype. Automatically infers the number
    of records based on total byte length.

    Parameters:
        data (bytes or memoryview): Field-wise byte layout for all records.
        dtype (np.dtype): Target structured dtype.

    Returns:
        np.ndarray: Structured array with shape (num_records,).

    Raises:
        ValueError: If dtype is not structured or data size is invalid.
    """
    if dtype.fields is None:
        raise ValueError("Provided dtype is not structured.")

    total_bytes = len(data)
    field_names = dtype.names
    field_dtypes = [dtype.fields[name][0] for name in field_names]
    field_itemsizes = [np.dtype(ft).itemsize for ft in field_dtypes]
    total_per_point = sum(field_itemsizes)

    if total_bytes % total_per_point != 0:
        raise ValueError("Byte size mismatch with dtype layout.")

    num_points = total_bytes // total_per_point

    offset = 0
    values = []
    for name, field_dtype, itemsize in zip(field_names, field_dtypes, field_itemsizes):
        nbytes = itemsize * num_points
        field_data = np.frombuffer(
            data, dtype=field_dtype, count=num_points, offset=offset
        )
        values.append((name, field_data))
        offset += nbytes

    structured = np.empty(num_points, dtype=dtype)
    for name, val in values:
        structured[name] = val

    return structured


def insert_field(
    old_array: np.ndarray,
    name: str,
    dtype: Union[str, type, np.dtype],
    default: float = 0,
) -> np.ndarray:
    dtype = np.dtype(dtype)

    if name in old_array.dtype.names:
        raise ValueError(f"Field '{name}' already exists")

    new_dtype = old_array.dtype.descr + [(name, dtype.str)]
    new_array = np.empty(old_array.shape, dtype=new_dtype)

    for field in old_array.dtype.names:
        new_array[field] = old_array[field]

    new_array[name] = default
    return new_array


def remove_field(array: np.ndarray, name: str) -> np.ndarray:
    if name not in array.dtype.names:
        raise ValueError(f"Field '{name}' not in array")

    keep_fields = [f for f in array.dtype.names if f != name]
    new_dtype = [(f, array.dtype.fields[f][0]) for f in keep_fields]
    new_array = np.empty(array.shape, dtype=new_dtype)

    for f in keep_fields:
        new_array[f] = array[f]

    return new_array


@numba.njit(cache=True)
def apply_transform_xyz(xyz: np.ndarray, r: np.ndarray, t: np.ndarray):
    for i in range(xyz.shape[0]):
        xi, yi, zi = xyz[i, 0], xyz[i, 1], xyz[i, 2]
        xyz[i, 0] = r[0, 0] * xi + r[0, 1] * yi + r[0, 2] * zi + t[0]
        xyz[i, 1] = r[1, 0] * xi + r[1, 1] * yi + r[1, 2] * zi + t[1]
        xyz[i, 2] = r[2, 0] * xi + r[2, 1] * yi + r[2, 2] * zi + t[2]


@numba.njit(cache=True, parallel=True)
def apply_transform_xyz_parallel(xyz: np.ndarray, r: np.ndarray, t: np.ndarray):
    for i in numba.prange(xyz.shape[0]):
        xi, yi, zi = xyz[i, 0], xyz[i, 1], xyz[i, 2]
        xyz[i, 0] = r[0, 0] * xi + r[0, 1] * yi + r[0, 2] * zi + t[0]
        xyz[i, 1] = r[1, 0] * xi + r[1, 1] * yi + r[1, 2] * zi + t[1]
        xyz[i, 2] = r[2, 0] * xi + r[2, 1] * yi + r[2, 2] * zi + t[2]
