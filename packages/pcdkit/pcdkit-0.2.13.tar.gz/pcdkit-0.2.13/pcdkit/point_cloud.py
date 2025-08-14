import os
import struct
from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO, Union

import lzf
import numpy as np
from typing_extensions import Literal, Self

from .pcd_metadata import PCDMetadata
from .typings import PathLike, PCDUnsupportedFormatError
from .utils import apply_transform_xyz, apply_transform_xyz_parallel


class PointCloud(ABC):
    """
    Abstract base class representing a 3D point cloud.

    Attributes:
        metadata (PCDMetadata): Metadata describing the structure and properties of the point cloud.
        pc_data (np.ndarray or np.memmap): The structured NumPy array containing point cloud data.
    """

    metadata: PCDMetadata
    pc_data: Union[np.ndarray, np.memmap]

    def __repr__(self) -> str:
        """Return a concise string representation for debugging."""
        return f"<{self.__class__.__name__} shape={self.pc_data.shape}, dtype={self.pc_data.dtype}, fields={self.pc_data.dtype.names}>"

    def __str__(self) -> str:
        """Return a human-readable summary of the point cloud."""
        return f"PointCloud with {self.metadata.points} points ({len(self.metadata.fields)} fields): {self.metadata.fields}"

    @abstractmethod
    def add_field(
        self,
        name: str,
        dtype: Union[str, type, np.dtype],
        default: float = 0,
    ) -> Self:
        """
        Add a new field (column) to the point cloud.

        Args:
            name (str): The name of the new field.
            dtype (str or np.dtype): The data type of the field.
            default (float): The default value to initialize the field with.

        Returns:
            Self: The updated point cloud instance.

        Raises:
            ValueError: If the field already exists.
        """
        pass

    @abstractmethod
    def drop_field(self, name: str) -> Self:
        """
        Remove a field (column) from the point cloud.

        Args:
            name (str): The name of the field to remove.

        Returns:
            Self: The updated point cloud instance.

        Raises:
            ValueError: If the field does not exist.
        """
        pass

    def save(
        self,
        path: PathLike,
        format: Union[Literal["ascii", "binary", "binary_compressed"], str] = "binary",
    ) -> None:
        """
        Save the point cloud to a PCD file.

        Args:
            path (PathLike): The file path to save to.
            format (str): The PCD format: 'ascii', 'binary', or 'binary_compressed'.

        Raises:
            PCDUnsupportedFormatError: If an unsupported format is specified.
            Exception: If the file write fails.
        """
        path = Path(path)
        temp_path = path.with_suffix(path.suffix + ".tmp")
        try:
            with temp_path.open("wb") as f:
                f.write(self.metadata.to_pcd_header(format).encode("ascii"))
                self._write_data(f, format)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, path)
        except Exception:
            if temp_path.exists():
                temp_path.unlink()
            raise

    def _write_data(self, f: BinaryIO, format: str) -> None:
        """
        Write the point data to an open binary file in the specified format.

        Args:
            f (BinaryIO): Open file handle.
            format (str): Format: 'ascii', 'binary', or 'binary_compressed'.

        Raises:
            PCDUnsupportedFormatError: If the format is invalid.
        """
        if format == "ascii":
            for row in self.pc_data:
                f.write((" ".join(str(x) for x in row) + "\n").encode("ascii"))
        elif format == "binary":
            f.write(self.pc_data.tobytes())
        elif format == "binary_compressed":
            raw = self.pc_data.tobytes()
            compressed = lzf.compress(raw, len(raw) + len(raw) // 4)
            f.write(struct.pack("II", len(compressed), len(raw)))
            f.write(compressed)
        else:
            raise PCDUnsupportedFormatError(f"Unsupported format: {format}")

    def transform(self, matrix: np.ndarray, parallel: bool = False) -> Self:
        """
        Apply a 4x4 transformation matrix to the x, y, z coordinates of the point cloud.

        Args:
            matrix (np.ndarray): A 4x4 affine transformation matrix.
            parallel (bool): Whether to use Numba parallelization for performance.

        Returns:
            Self: The transformed point cloud.

        Raises:
            ValueError: If x, y, z fields are missing.
        """
        if not all(k in self.pc_data.dtype.names for k in ("x", "y", "z")):
            raise ValueError("PointCloud must have x, y, z fields")

        r = matrix[:3, :3]
        t = matrix[:3, 3]

        xyz = np.stack(
            [self.pc_data["x"], self.pc_data["y"], self.pc_data["z"]], axis=1
        )

        if parallel:
            apply_transform_xyz_parallel(xyz, r, t)
        else:
            apply_transform_xyz(xyz, r, t)

        self.pc_data["x"][:] = xyz[:, 0]
        self.pc_data["y"][:] = xyz[:, 1]
        self.pc_data["z"][:] = xyz[:, 2]
        return self

    def set_field(self, name: str, value: Union[float, np.ndarray]) -> Self:
        """
        Set all values in a field to a constant or an array.

        Args:
            name (str): The name of the field to update.
            value (float or np.ndarray): A scalar or array of values.

        Returns:
            Self: The updated point cloud.

        Raises:
            ValueError: If the field does not exist or array length mismatches.
            TypeError: If value type is not supported.
        """
        if name not in self.pc_data.dtype.names:
            raise ValueError(f"Field '{name}' does not exist")

        if isinstance(value, float) or isinstance(value, int):
            self.pc_data[name][:] = value
        elif isinstance(value, np.ndarray):
            if value.shape[0] != self.pc_data.shape[0]:
                raise ValueError(
                    f"Input array length ({value.shape[0]}) does not match number of points ({self.pc_data.shape[0]})"
                )
            self.pc_data[name][:] = value
        else:
            raise TypeError(f"Unsupported value type: {type(value)}")

        return self

    def drop_points(self, indices: np.ndarray) -> Self:
        """
        Drop points at specified indices from the point cloud.

        Args:
            indices (np.ndarray): An array of indices to remove.

        Returns:
            Self: The updated point cloud instance.
        """
        pass
