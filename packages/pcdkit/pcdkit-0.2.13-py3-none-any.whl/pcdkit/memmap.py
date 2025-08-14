from pathlib import Path
from typing import Union

import numpy as np
from typing_extensions import Self

from .pcd_metadata import PCDMetadata
from .point_cloud import PointCloud
from .typings import PathLike
from .utils import insert_field, remove_field


class MemMapPointCloud(PointCloud):
    """
    A PointCloud implementation that uses memory-mapped files to store large point cloud data efficiently on disk.

    Attributes:
        metadata (PCDMetadata): Metadata describing the structure and properties of the point cloud.
        pc_data (np.memmap): The memory-mapped NumPy array containing point cloud data.
        memmap_file_path (Path): File path backing the memory map.
    """

    def __init__(
        self,
        metadata: PCDMetadata,
        pc_data: np.ndarray,
        memmap_file_path: PathLike,
    ):
        """
        Initialize a MemMapPointCloud and write the provided array to a memory-mapped file.

        Args:
            metadata (PCDMetadata): Metadata describing the point cloud.
            pc_data (np.ndarray): A structured NumPy array with point data.
            memmap_file_path (PathLike): File path to store the memory-mapped array.
        """
        self.metadata = metadata

        pc_data.tofile(memmap_file_path)
        self.memmap_file_path = Path(memmap_file_path)
        self.pc_data = np.memmap(
            filename=memmap_file_path,
            dtype=metadata.to_dtype(),
            mode="r+",
            shape=(metadata.points,),
        )

    def transform(self, matrix: np.ndarray, parallel: bool = False) -> Self:
        """
        Apply a 4x4 transformation matrix to the x, y, z fields and flush the changes to disk.

        Args:
            matrix (np.ndarray): A 4x4 affine transformation matrix.
            parallel (bool): Whether to use parallelized transformation with Numba.

        Returns:
            Self: The transformed MemMapPointCloud.
        """
        super().transform(matrix, parallel)
        self.pc_data.flush()

        return self

    def add_field(
        self,
        name: str,
        dtype: Union[str, type, np.dtype],
        default: float = 0,
    ) -> Self:
        """
        Add a new field to the memory-mapped point cloud, writing changes to disk.

        Args:
            name (str): The name of the new field.
            dtype (str or np.dtype): The data type of the new field.
            default (float): The default value to initialize the new field.

        Returns:
            Self: The updated MemMapPointCloud.

        Raises:
            ValueError: If the field already exists.
        """
        tmp_array = insert_field(self.pc_data, name, dtype, default)
        tmp_array.tofile(self.memmap_file_path)

        self.metadata.add_field(name, np.dtype(dtype))
        self.pc_data = np.memmap(
            self.memmap_file_path,
            dtype=self.metadata.to_dtype(),
            mode="r+",
            shape=(self.metadata.points,),
        )
        return self

    def drop_field(self, name: str) -> Self:
        """
        Remove a field from the memory-mapped point cloud, writing the result back to disk.

        Args:
            name (str): The name of the field to remove.

        Returns:
            Self: The updated MemMapPointCloud.

        Raises:
            ValueError: If the field does not exist.
        """
        tmp_array = remove_field(self.pc_data, name)
        tmp_array.tofile(self.memmap_file_path)

        self.metadata.remove_field(name)
        self.pc_data = np.memmap(
            self.memmap_file_path,
            dtype=self.metadata.to_dtype(),
            mode="r+",
            shape=(self.metadata.points,),
        )
        return self

    def set_field(self, name: str, value: Union[float, np.ndarray]) -> Self:
        """
        Set the values of a field to a scalar or array and flush changes to disk.

        Args:
            name (str): The name of the field to modify.
            value (float or np.ndarray): A scalar or array of values.

        Returns:
            Self: The updated MemMapPointCloud.

        Raises:
            ValueError: If the field does not exist or array length mismatches.
            TypeError: If the value type is not supported.
        """
        super().set_field(name, value)
        self.pc_data.flush()
        return self

    def drop_points(self, indices: np.ndarray) -> Self:
        if not np.issubdtype(indices.dtype, np.integer):
            raise TypeError("Indices must be an integer array.")

        total_points = self.pc_data.shape[0]
        mask = np.ones(total_points, dtype=bool)
        mask[indices] = False

        new_array = self.pc_data[mask].copy()
        new_array.tofile(self.memmap_file_path)

        self.metadata.points = new_array.shape[0]
        self.metadata.width = new_array.shape[0]
        self.metadata.height = 1

        self.pc_data = np.memmap(
            self.memmap_file_path,
            dtype=self.metadata.to_dtype(),
            mode="r+",
            shape=(self.metadata.points,),
        )

        return self
