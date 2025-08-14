from dataclasses import dataclass
from typing import List, Tuple, Union

import numpy as np

from .typings import PCDParseError, PCDUnsupportedFormatError


@dataclass
class PCDMetadata:
    version: str
    fields: List[str]
    size: List[int]
    type: List[str]
    count: List[int]
    width: int
    height: int
    viewpoint: Tuple[float, float, float, float, float, float, float]
    points: int

    @property
    def is_organized(self) -> bool:
        return self.height > 1

    @property
    def shape(self) -> Tuple[int, int]:
        return self.height, self.width

    @classmethod
    def from_array(cls, array: np.ndarray) -> "PCDMetadata":
        if not array.dtype.names:
            raise ValueError("Array must be structured with named fields")

        fields = list(array.dtype.names)
        count = [1] * len(fields)
        field_types = []

        for name in fields:
            dtype = array.dtype.fields[name][0]
            kind = dtype.kind
            item_size = dtype.itemsize

            if kind == "f":
                if item_size not in {4, 8}:
                    raise PCDParseError(
                        f"Unsupported float size of {kind}: {item_size}"
                    )
                field_types.append("F")
            elif kind == "u":
                if item_size not in {1, 2, 4}:
                    raise PCDParseError(
                        f"Unsupported float size of {kind}: {item_size}"
                    )
                field_types.append("U")
            elif kind == "i":
                if item_size not in {1, 2, 4}:
                    raise PCDParseError(
                        f"Unsupported float size of {kind}: {item_size}"
                    )
                field_types.append("I")
            else:
                raise PCDParseError(f"Unsupported dtype kind: {kind}")

        return cls(
            version="0.7",
            fields=fields,
            size=[array.dtype.fields[name][0].itemsize for name in fields],
            type=field_types,
            count=count,
            width=array.shape[0],
            height=1,
            viewpoint=(0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0),
            points=array.shape[0],
        )

    def to_dtype(self) -> np.dtype:
        type_map = {
            ("F", 4): "f4",
            ("F", 8): "f8",
            ("U", 1): "u1",
            ("U", 2): "u2",
            ("U", 4): "u4",
            ("I", 1): "i1",
            ("I", 2): "i2",
            ("I", 4): "i4",
        }

        fields = []
        for name, t, sz, cnt in zip(self.fields, self.type, self.size, self.count):
            try:
                dtype = type_map[(t, sz)]
            except KeyError:
                raise PCDUnsupportedFormatError(f"Unsupported type/size: ({t}, {sz})")
            if cnt == 1:
                fields.append((name, dtype))
            else:
                fields.extend((f"{name}_{i}", dtype) for i in range(cnt))

        return np.dtype(fields)

    def to_pcd_header(self, data_format: str) -> str:
        lines = [
            # I mean, it's kinda shit the official example is "v.7", but people are using "v0.7", so we have to follow this convention.
            f"# .PCD v{self.version} - Point Cloud Data file format",
            f"VERSION {self.version}",
            f"FIELDS {' '.join(self.fields)}",
            f"SIZE {' '.join(map(str, self.size))}",
            f"TYPE {' '.join(self.type)}",
            f"COUNT {' '.join(map(str, self.count))}",
            f"WIDTH {self.width}",
            f"HEIGHT {self.height}",
            f"VIEWPOINT {' '.join(map(str, self.viewpoint))}",
            f"POINTS {self.points}",
            f"DATA {data_format.lower()}",
            "",  # ends with newline
        ]
        return "\n".join(lines)

    def add_field(self, name: str, dtype: Union[str, np.dtype], count: int = 1):
        np_dtype = np.dtype(dtype)

        self.fields.append(name)
        self.count.append(count)
        self.size.append(np_dtype.itemsize)
        self.type.append(infer_pcd_type(np_dtype))

    def remove_field(self, name: str):
        idx = self.fields.index(name)
        self.fields.pop(idx)
        self.size.pop(idx)
        self.type.pop(idx)
        self.count.pop(idx)


def infer_pcd_type(np_dtype: np.dtype) -> str:
    kind = np_dtype.kind
    if kind == "f":
        return "F"
    elif kind == "i":
        return "I"
    elif kind == "u":
        return "U"
    else:
        raise ValueError(f"Unsupported dtype for PCD: {np_dtype}")
